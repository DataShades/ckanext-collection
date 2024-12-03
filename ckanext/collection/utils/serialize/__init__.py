from __future__ import annotations

import abc
import csv
import io
import itertools
import json
import operator
from functools import reduce
from typing import Any, Callable, Generic, Iterable, cast

import sqlalchemy as sa
from sqlalchemy.engine import Row
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import InstanceState

import ckan.plugins.toolkit as tk

from ckanext.collection import internal, types

__all__ = [
    "Serializer",
    "StreamingSerializer",
    "RenderableSerializer",
    "CsvSerializer",
    "DictListSerializer",
    "JsonlSerializer",
    "JsonSerializer",
    "ChartJsSerializer",
    "HtmlSerializer",
    "TableSerializer",
    "HtmxTableSerializer",
]


def basic_row_dictizer(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return cast("dict[str, Any]", row)

    if isinstance(row, Row):
        if hasattr(row, "_asdict"):
            return row._asdict()  # # type: ignore

        if hasattr(row, "keys"):
            return dict(zip(row.keys(), row))

    try:
        reflection = sa.inspect(row)
    except NoInspectionAvailable:
        raise TypeError(type(row)) from None

    if isinstance(reflection, InstanceState):
        return {attr.key: attr.value for attr in reflection.attrs}

    raise TypeError(type(row))


class Serializer(
    types.BaseSerializer,
    internal.Domain[types.TDataCollection],
    Generic[types.TSerialized, types.TDataCollection],
):
    """Base collection serializer.

    For any derived implementation, `serialize` must transfrom data of the
    collection into expected format.

    Example:
        ```pycon
        >>> class MySerializer(serialize.Serializer):
        >>>     def stream(self):
        >>>         for record in self.attached.data:
        >>>             yield yaml.dump(record)
        >>>
        >>>     def serialize(self):
        >>>         return "---\\n".join(self.stream())
        ```

    """

    value_serializers: dict[
        str, types.ValueSerializer
    ] = internal.configurable_attribute(
        default_factory=lambda self: {},
    )
    row_dictizer: Callable[[Any], dict[str, Any]] = internal.configurable_attribute(
        basic_row_dictizer,
    )

    def serialize(self) -> types.TSerialized:
        """Return serialized data."""
        result: Any = (r for r in self.attached.data)
        return result

    def serialize_value(self, value: Any, name: str, record: Any):
        """Transform record's value into its serialized form."""
        for serializer, options in self.attached.columns.serializers.get(name, []):
            if isinstance(serializer, str):
                serializer = self.value_serializers.get(serializer)

            if not serializer:
                continue

            value = serializer(value, options, name, record, self)

        return value

    def dictize_row(self, row: Any) -> dict[str, Any]:
        """Transform single data record into serializable dictionary."""
        result = self.row_dictizer(row)
        if fields := self.attached.columns.names:
            visible = self.attached.columns.visible
        else:
            fields = list(result)
            visible = set(fields)

        return {
            field: self.serialize_value(result.get(field), field, row)
            for field in fields
            if field in visible
        }


class StreamingSerializer(
    Serializer[types.TSerialized, types.TDataCollection],
):
    @abc.abstractmethod
    def stream(self) -> Iterable[types.TSerialized]:
        """Iterate over fragments of the content.

        Type of the stream fragment must be the same as type of serialized
        content. For example, serializer that produces list of dictionaries,
        must yield `[dict(...)]`, not just `dict(...)`
        """
        raise NotImplementedError

    def serialize(self) -> types.TSerialized:
        return reduce(operator.add, self.stream())


class DictListSerializer(
    StreamingSerializer["list[dict[str, Any]]", types.TDataCollection],
):
    """Convert data into a list of dictionaries.

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     serializer_factory=serialize.DictListSerializer,
        >>>     columns_factory=columns.Columns.with_attributes(
        >>>         names=["name", "sysadmin"],
        >>>     ),
        >>>     data_factory=data.ModelData,
        >>>     data_settings={"model": model.User},
        >>> )
        >>> col.serializer.serialize()
        [{'name': 'default', 'sysadmin': True}]
        ```

    """

    def stream(self):
        """Iterate over fragments of the content."""
        for item in self.attached.data:
            yield [self.dictize_row(item)]


class RenderableSerializer(StreamingSerializer[str, types.TDataCollection]):
    def stream(self) -> Iterable[str]:
        """Iterate over fragments of the content."""
        yield ""

    def render(self) -> str:
        """Combine content fragments into a single dump."""
        return self.serialize()


class CsvSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into CSV document.

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     serializer_factory=serialize.CsvSerializer,
        >>>     columns_factory=columns.Columns.with_attributes(
        >>>         names=["name", "sysadmin"],
        >>>     ),
        >>>     data_factory=data.ModelData,
        >>>     data_settings={"model": model.User},
        >>> )
        >>> col.serializer.serialize()
        name,sysadmin
        default,True
        ```
    """

    def get_writer(self, buff: io.StringIO, fieldnames: list[str]):
        return csv.DictWriter(buff, fieldnames, extrasaction="ignore")

    def get_header_row(self, writer: csv.DictWriter[str]) -> dict[str, str]:
        return {
            col: self.attached.columns.labels.get(col, col) for col in writer.fieldnames
        }

    def prepare_row(self, row: Any) -> dict[str, Any]:
        return self.dictize_row(row)

    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        data = iter(self.attached.data)
        fieldnames = [
            n for n in self.attached.columns.names if n in self.attached.columns.names
        ]
        if not fieldnames:
            empty = object()
            row = next(data, empty)
            if row is not empty:
                data = itertools.chain([row], data)
                fieldnames = list(self.prepare_row(row))

        writer = self.get_writer(buff, fieldnames)

        writer.writerow(self.get_header_row(writer))

        yield buff.getvalue()
        buff.seek(0)
        buff.truncate()

        for row in data:
            writer.writerow(self.prepare_row(row))
            yield buff.getvalue()
            buff.seek(0)
            buff.truncate()


class JsonlSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into JSONL lines.

    Attributes:
        encoder: `json.JSONEncoder` instance used for serialization

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     serializer_factory=serialize.JsonlSerializer,
        >>>     columns_factory=columns.Columns.with_attributes(
        >>>         names=["name", "sysadmin"],
        >>>     ),
        >>>     data_factory=data.ModelData,
        >>>     data_settings={"model": model.User},
        >>> )
        >>> col.serializer.serialize()
        {"name: "default", "sysadmin": true}
        {"name: "normal_user", "sysadmin": false}
        ```
    """

    encoder = internal.configurable_attribute(json.JSONEncoder(default=str))

    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        for row in map(self.dictize_row, self.attached.data):
            buff.write(self.encoder.encode(row))
            yield buff.getvalue()
            yield "\n"
            buff.seek(0)
            buff.truncate()


class JsonSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into single JSON document.

    Attributes:
        encoder: `json.JSONEncoder` instance used for serialization

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     serializer_factory=serialize.JsonSerializer,
        >>>     columns_factory=columns.Columns.with_attributes(
        >>>         names=["name", "sysadmin"],
        >>>     ),
        >>>     data_factory=data.ModelData,
        >>>     data_settings={"model": model.User},
        >>> )
        >>> col.serializer.serialize()
        [{"name: "default", "sysadmin": true},
         {"name: "normal_user", "sysadmin": false}]
        ```
    """

    encoder = internal.configurable_attribute(json.JSONEncoder(default=str))

    def stream(self):
        yield self.encoder.encode(
            [self.dictize_row(row) for row in self.attached.data],
        )


class ChartJsSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into data source for ChartJS."""

    label_column: str = internal.configurable_attribute("")
    dataset_columns: list[str] = internal.configurable_attribute(
        default_factory=lambda self: [],
    )
    dataset_labels: dict[str, str] = internal.configurable_attribute(
        default_factory=lambda self: {},
    )
    colors: dict[str, str] = internal.configurable_attribute(
        default_factory=lambda self: {},
    )

    def stream(self):
        labels = []
        data: list[list[int]] = []

        for item in map(self.dictize_row, self.attached.data):
            labels.append(item.get(self.label_column, None))
            data.append(
                [item[name] for name in self.dataset_columns],
            )

        datasets: list[dict[str, Any]] = [
            {
                "data": row,
                "label": self.dataset_labels.get(column, column),
                "backgroundColor": self.colors.get(column),
            }
            for column, row in zip(self.dataset_columns, zip(*data))
        ]
        yield json.dumps(
            {
                "labels": labels,
                "datasets": datasets,
            },
        )


class HtmlSerializer(RenderableSerializer[types.TDataCollection]):
    """Serialize collection into HTML document.

    Attributes:
        main_template: path to Jinja2 template for the collection
        record_template: path to Jinja2 template for the individual record

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     serializer_factory=serialize.HtmlSerializer,
        >>>     data_factory=data.StaticData,
        >>>     data_settings={"data": range(3)},
        >>> )
        >>> col.serializer.serialize()
        <ul>
          <li>0</li>
          <li>1</li>
          <li>2</li>
        </ul>
        ```
    """

    ensure_dictized: bool = internal.configurable_attribute(False)

    main_template: str = internal.configurable_attribute(
        "collection/serialize/html/main.html",
    )
    record_template: str = internal.configurable_attribute(
        "collection/serialize/html/record.html",
    )

    prefix: str = internal.configurable_attribute("collection-content")
    base_class: str = internal.configurable_attribute("collection")

    @property
    def form_id(self):
        return f"{self.prefix}-form--{self.attached.name}"

    def get_data(self) -> dict[str, Any]:
        return {
            "collection": self.attached,
        }

    def stream(self):
        import contextlib

        from flask import has_app_context

        from ckan.lib.helpers import _get_auto_flask_context  # type: ignore

        ctx: Any = (
            contextlib.nullcontext() if has_app_context() else _get_auto_flask_context()
        )
        with ctx:
            yield tk.render(
                self.main_template,
                self.get_data(),
            )


class TableSerializer(HtmlSerializer[types.TDataCollection]):
    """Serialize collection into HTML table.

    Attributes:
        main_template: path to template for the collection
        main_template: path to template for the table wrapper
        record_template: path to template for the individual record
        counter_template: path to template for the item counter
        pager_template: path to template for the table pagination widget
        form_template: path to template for the search form
        filter_template: path to template for filters block inside search form

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     serializer_factory=serialize.TableSerializer,
        >>>     columns_factory=columns.Columns.with_attributes(
        >>>         names=["name", "sysadmin"],
        >>>     ),
        >>>     data_factory=data.ModelData,
        >>>     data_settings={"model": model.User},
        >>> )
        >>> col.serializer.serialize()
        <table>...</table>
        ```
    """

    main_template: str = internal.configurable_attribute(
        "collection/serialize/table/main.html",
    )
    table_template: str = internal.configurable_attribute(
        "collection/serialize/table/table.html",
    )
    record_template: str = internal.configurable_attribute(
        "collection/serialize/table/record.html",
    )
    counter_template: str = internal.configurable_attribute(
        "collection/serialize/table/counter.html",
    )
    pager_template: str = internal.configurable_attribute(
        "collection/serialize/table/pager.html",
    )
    form_template: str = internal.configurable_attribute(
        "collection/serialize/table/form.html",
    )
    filter_template: str = internal.configurable_attribute(
        "collection/serialize/table/filter.html",
    )

    prefix: str = internal.configurable_attribute("collection-table")

    @property
    def table_id(self):
        return f"{self.prefix}-id--{self.attached.name}"


class HtmxTableSerializer(TableSerializer[types.TDataCollection]):
    """Serialize collection into HTML table powered by HTMX.

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     serializer_factory=serialize.HtmxTableSerializer,
        >>>     columns_factory=columns.Columns.with_attributes(
        >>>         names=["name", "sysadmin"],
        >>>     ),
        >>>     data_factory=data.ModelData,
        >>>     data_settings={"model": model.User},
        >>> )
        >>> col.serializer.serialize()
        <table>...</table>
        ```
    """

    main_template: str = internal.configurable_attribute(
        "collection/serialize/htmx_table/main.html",
    )
    table_template: str = internal.configurable_attribute(
        "collection/serialize/htmx_table/table.html",
    )
    record_template: str = internal.configurable_attribute(
        "collection/serialize/htmx_table/record.html",
    )
    counter_template: str = internal.configurable_attribute(
        "collection/serialize/htmx_table/counter.html",
    )
    pager_template: str = internal.configurable_attribute(
        "collection/serialize/htmx_table/pager.html",
    )
    form_template: str = internal.configurable_attribute(
        "collection/serialize/htmx_table/form.html",
    )
    filter_template: str = internal.configurable_attribute(
        "collection/serialize/htmx_table/filter.html",
    )

    debug: bool = internal.configurable_attribute(False)
    push_url: bool = internal.configurable_attribute(False)
    base_class: str = internal.configurable_attribute("htmx-collection")

    render_url: str = internal.configurable_attribute(
        default_factory=lambda self: tk.h.url_for(
            "ckanext-collection.render",
            name=self.attached.name,
        ),
    )
