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
        return ""

    def render(self) -> str | bytes:
        """Combine content fragments into a single dump."""
        return reduce(operator.add, self.stream())


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
            return dict(zip(row.keys(), row))
        return row

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
                dict(zip(row.keys(), row)) if isinstance(row, Row) else row
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
            data.append([item.get(name, 0) for name in self.dataset_columns])

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

    template: str = shared.configurable_attribute("collection/snippets/dump.html")

    def get_data(self) -> dict[str, Any]:
        return {
            "collection": self.attached,
        }

    def stream(self):
        yield tk.render(
            self.template,
            self.get_data(),
        )


class TableSerializer(HtmlSerializer[types.TDataCollection]):
    """Serialize collection into HTML table."""

    templatel: str = shared.configurable_attribute("collection/snippets/table.html")
    row_snippet: str = shared.configurable_attribute("collection/snippets/row.html")

    def get_data(self) -> dict[str, Any]:
        data = super().get_data()
        data.update(
            {
                "table": self.attached,
                "row_snippet": self.row_snippet,
            },
        )
        return data
