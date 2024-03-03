from __future__ import annotations

import abc
import csv
import io
import json
import operator
from functools import reduce
from typing import Any, Callable, Generic, Iterable, cast

import sqlalchemy as sa
from sqlalchemy.engine import Row
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import InstanceState

import ckan.plugins.toolkit as tk

from ckanext.collection import shared, types

__all__ = [
    "Serializer",
    "StreamingSerializer",
    "RenderableSerializer",
    "CsvSerializer",
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
        return dict(zip(row.keys(), row))

    try:
        reflection = sa.inspect(  # pyright: ignore[reportUnknownVariableType]
            row,
        )
    except NoInspectionAvailable:
        raise TypeError(type(row)) from None

    if isinstance(reflection, InstanceState):
        return {attr.key: attr.value for attr in reflection.attrs}  # pyright: ignore

    raise TypeError(type(row))


class Serializer(
    types.BaseSerializer,
    shared.Domain[types.TDataCollection],
    Generic[types.TSerialized, types.TDataCollection],
):
    """Base collection serializer.

    For any derived implementation, `serialize` must transfrom data of the
    collection into expected format. Example:

    >>> def stream(self):
    >>>     for record in self.attached.data:
    >>>         yield yaml.dump(record)
    >>>
    >>> def serialize(self):
    >>>     return "---\n".join(self.stream())

    """

    value_serializers: dict[str, types.ValueSerializer] = shared.configurable_attribute(
        default_factory=lambda self: {},
    )
    row_dictizer: Callable[[Any], dict[str, Any]] = shared.configurable_attribute(
        basic_row_dictizer,
    )

    def serialize(self) -> types.TSerialized:
        """Return serialized data."""
        return cast(types.TSerialized, None)

    def serialize_value(self, value: Any, name: str, record: Any):
        """Transform record's value into its serialized form."""
        for serializer_name, options in self.attached.columns.serializers.get(name, []):
            if serializer_name not in self.value_serializers:
                continue
            value = self.value_serializers[serializer_name](
                value,
                options,
                name,
                record,
                self,
            )

        return value

    def dictize_row(self, row: Any) -> dict[str, Any]:
        """Transform single data record into serializable dictionary."""
        result = self.row_dictizer(row)

        return {k: self.serialize_value(v, k, row) for k, v in result.items()}


class StreamingSerializer(Serializer[types.TSerialized, types.TDataCollection]):
    @abc.abstractmethod
    def stream(self) -> Iterable[types.TSerialized]:
        """Iterate over fragments of the content."""
        raise NotImplementedError

    def serialize(self):
        return reduce(operator.add, self.stream())


class RenderableSerializer(StreamingSerializer[str, types.TDataCollection]):
    def stream(self) -> Iterable[str]:
        """Iterate over fragments of the content."""
        yield ""

    def render(self) -> str:
        """Combine content fragments into a single dump."""
        return self.serialize()


class CsvSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into CSV document."""

    def get_writer(self, buff: io.StringIO):
        return csv.DictWriter(
            buff,
            fieldnames=self.get_fieldnames(),
            extrasaction="ignore",
        )

    def get_fieldnames(self) -> list[str]:
        return [
            name
            for name in self.attached.columns.names
            if name in self.attached.columns.visible
        ]

    def get_header_row(self, writer: csv.DictWriter[str]) -> dict[str, str]:
        return {
            col: self.attached.columns.labels.get(col, col) for col in writer.fieldnames
        }

    def prepare_row(self, row: Any, writer: csv.DictWriter[str]) -> dict[str, Any]:
        return self.dictize_row(row)

    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        writer = self.get_writer(buff)

        writer.writerow(self.get_header_row(writer))

        yield buff.getvalue()
        buff.seek(0)
        buff.truncate()

        for row in self.attached.data:
            writer.writerow(self.prepare_row(row, writer))
            yield buff.getvalue()
            buff.seek(0)
            buff.truncate()


class JsonlSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into JSONL lines."""

    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        for row in map(self.dictize_row, self.attached.data):
            json.dump(row, buff)
            yield buff.getvalue()
            yield "\n"
            buff.seek(0)
            buff.truncate()


class JsonSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into single JSON document."""

    def stream(self):
        yield json.dumps(
            [self.dictize_row(row) for row in self.attached.data],
        )


class ChartJsSerializer(StreamingSerializer[str, types.TDataCollection]):
    """Serialize collection into data source for ChartJS module of
    ckanext-charts.

    """

    label_column: str = shared.configurable_attribute("")
    dataset_columns: list[str] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )
    dataset_labels: dict[str, str] = shared.configurable_attribute(
        default_factory=lambda self: {},
    )
    colors: dict[str, str] = shared.configurable_attribute(
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
    """Serialize collection into HTML document."""

    ensure_dictized: bool = shared.configurable_attribute(False)

    main_template: str = shared.configurable_attribute(
        "collection/serialize/html/main.html",
    )
    record_template: str = shared.configurable_attribute(
        "collection/serialize/html/record.html",
    )

    def get_data(self) -> dict[str, Any]:
        return {
            "collection": self.attached,
        }

    def stream(self):
        yield tk.render(
            self.main_template,
            self.get_data(),
        )


class TableSerializer(HtmlSerializer[types.TDataCollection]):
    """Serialize collection into HTML table."""

    main_template: str = shared.configurable_attribute(
        "collection/serialize/table/main.html",
    )
    table_template: str = shared.configurable_attribute(
        "collection/serialize/table/table.html",
    )
    record_template: str = shared.configurable_attribute(
        "collection/serialize/table/record.html",
    )
    counter_template: str = shared.configurable_attribute(
        "collection/serialize/table/counter.html",
    )
    pager_template: str = shared.configurable_attribute(
        "collection/serialize/table/pager.html",
    )
    form_template: str = shared.configurable_attribute(
        "collection/serialize/table/form.html",
    )
    filter_template: str = shared.configurable_attribute(
        "collection/serialize/table/filter.html",
    )

    prefix: str = shared.configurable_attribute("collection-table")
    base_class: str = shared.configurable_attribute("collection")

    @property
    def form_id(self):
        return f"{self.prefix}-form--{self.attached.name}"

    @property
    def table_id(self):
        return f"{self.prefix}-id--{self.attached.name}"


class HtmxTableSerializer(TableSerializer[types.TDataCollection]):
    """Serialize collection into HTML table."""

    main_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table/main.html",
    )
    table_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table/table.html",
    )
    record_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table/record.html",
    )
    counter_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table/counter.html",
    )
    pager_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table/pager.html",
    )
    form_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table/form.html",
    )
    filter_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table/filter.html",
    )

    debug: bool = shared.configurable_attribute(False)
    push_url: bool = shared.configurable_attribute(False)
    base_class: str = shared.configurable_attribute("htmx-collection")

    render_url: str = shared.configurable_attribute(
        default_factory=lambda self: tk.h.url_for(
            "ckanext-collection.render",
            name=self.attached.name,
        ),
    )
