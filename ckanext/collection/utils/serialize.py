from __future__ import annotations

import csv
import io
import json
import operator
from functools import reduce
from typing import Any, Iterable

from sqlalchemy.engine import Row

import ckan.plugins.toolkit as tk

from ckanext.collection import shared, types


class Serializer(types.BaseSerializer, shared.Domain[types.TDataCollection]):
    """Abstract collection serializer.

    Its`stream` produces iterable of collection records in the format that has
    sense for the serializer. Example:

    >>> def stream(self):
    >>>     for record in self.attached.data:
    >>>         yield yaml.dump(record)

    By default, all chunks are combined into single dump via `render` method,
    which combines fragments using addition operator. If this strategy doesn't
    work, override `render`:

    >>> def render(self):
    >>>     return "\n---\n".join(self.stream())

    """

    def stream(self) -> Iterable[str] | Iterable[bytes]:
        """Iterate over fragments of the content."""
        return ["", ""]

    def render(self) -> str | bytes:
        """Combine content fragments into a single dump."""
        return reduce(operator.add, self.stream())

    def serialize_value(self, value: Any, name: str, record: Any):
        return value


class CsvSerializer(Serializer[types.TDataCollection]):
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
        if isinstance(row, Row):
            row = dict(zip(row.keys(), row))

        return {k: self.serialize_value(v, k, row) for k, v in row.items()}

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


class JsonlSerializer(Serializer[types.TDataCollection]):
    """Serialize collection into JSONL lines."""

    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        for row in self.attached.data:
            if isinstance(row, Row):
                row = dict(zip(row.keys(), row))

            row = {k: self.serialize_value(v, k, row) for k, v in row.items()}
            json.dump(row, buff)
            yield buff.getvalue()
            yield "\n"
            buff.seek(0)
            buff.truncate()


class JsonSerializer(Serializer[types.TDataCollection]):
    """Serialize collection into single JSON document."""

    def stream(self):
        yield json.dumps(
            [
                {
                    k: self.serialize_value(v, k, row)
                    for k, v in (
                        dict(zip(row.keys(), row)) if isinstance(row, Row) else row
                    ).items()
                }
                for row in self.attached.data
            ],
        )


class ChartJsSerializer(Serializer[types.TDataCollection]):
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

        for item in self.attached.data:
            if isinstance(item, Row):
                item = dict(zip(item.keys(), item))

            labels.append(item.get(self.label_column, None))
            data.append(
                [
                    self.serialize_value(item.get(name, 0), name, item)
                    for name in self.dataset_columns
                ],
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


class HtmlSerializer(Serializer[types.TDataCollection]):
    """Serialize collection into HTML document."""

    main_template: str = shared.configurable_attribute(
        "collection/serialize/html_main.html",
    )
    record_template: str = shared.configurable_attribute(
        "collection/serialize/html_record.html",
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
        "collection/serialize/table_main.html",
    )
    table_template: str = shared.configurable_attribute(
        "collection/serialize/table_table.html",
    )
    record_template: str = shared.configurable_attribute(
        "collection/serialize/table_record.html",
    )
    counter_template: str = shared.configurable_attribute(
        "collection/serialize/table_counter.html",
    )
    pager_template: str = shared.configurable_attribute(
        "collection/serialize/table_pager.html",
    )
    form_template: str = shared.configurable_attribute(
        "collection/serialize/table_form.html",
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
        "collection/serialize/htmx_table_main.html",
    )
    table_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table_table.html",
    )
    record_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table_record.html",
    )
    counter_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table_counter.html",
    )
    pager_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table_pager.html",
    )
    form_template: str = shared.configurable_attribute(
        "collection/serialize/htmx_table_form.html",
    )

    debug: str = shared.configurable_attribute(False)
    push_url: str = shared.configurable_attribute(False)
    base_class: str = shared.configurable_attribute("htmx-collection")

    @property
    def render_url(self) -> str:
        return tk.h.url_for("ckanext-collection.render", name=self.attached.name)
