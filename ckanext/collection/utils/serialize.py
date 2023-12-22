from __future__ import annotations
import abc
import io
import csv
import json
import ckan.plugins.toolkit as tk
import operator
from functools import reduce
from sqlalchemy.engine import Row
from typing import Any, Iterable
from ckanext.collection import types
from .shared import AttachTrait, AttrSettingsTrait


class Serializer(types.BaseSerializer[types.TDataCollection], AttachTrait[types.TDataCollection], AttrSettingsTrait, abc.ABC):
    def __init__(self, col: types.TDataCollection, /, **kwargs: Any):
        self.attach(col)
        self.gather_settings(kwargs)

    @abc.abstractmethod
    def stream(self) -> Iterable[str] | Iterable[bytes]:
        return []

    def render(self) -> str | bytes:
        return reduce(operator.add, self.stream())


class CsvSerializer(Serializer[types.TDataCollection]):
    def get_writer(self, buff: io.StringIO):
        return csv.DictWriter(
            buff,
            fieldnames=self.get_fieldnames(),
            extrasaction="ignore",
        )

    def get_fieldnames(self) -> list[str]:
        return [
            name
            for name in self._collection.columns.names
            if name in self._collection.columns.visible
        ]

    def get_header_row(self, writer: csv.DictWriter[str]) -> dict[str, str]:
        return {
            col: self._collection.columns.labels.get(col, col)
            for col in writer.fieldnames
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

        for row in self._collection.data:
            writer.writerow(self.prepare_row(row, writer))
            yield buff.getvalue()
            buff.seek(0)
            buff.truncate()


class JsonlSerializer(Serializer[types.TDataCollection]):
    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        for row in self._collection.data:
            if isinstance(row, Row):
                row = dict(zip(row.keys(), row))

            json.dump(row, buff)
            yield buff.getvalue()
            yield "\n"
            buff.seek(0)
            buff.truncate()


class JsonSerializer(Serializer[types.TDataCollection]):
    def stream(self):
        yield json.dumps(
            dict(zip(row.keys(), row)) if isinstance(row, Row) else row
            for row in self._collection.data
        )


class ChartJsSerializer(Serializer[types.TDataCollection]):
    label_column: str
    dataset_columns: list[str]
    dataset_labels: dict[str, str]

    prefix: str = "interactive-table"

    @property
    def form_id(self):
        return f"{self.prefix}-form--{self._collection.name}"

    @property
    def table_id(self):
        return f"{self.prefix}-id--{self._collection.name}"

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        super().__init__(obj, **kwargs)
        self.label_column = kwargs.get("label_column", "")

        self.dataset_labels = kwargs.get("dataset_labels", {})

        self.dataset_columns = kwargs.get("dataset_columns", [])
        self.colors = kwargs.get("colors", {})

    def stream(self):
        labels = []
        data: list[list[int]] = []

        for item in self._collection.data:
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
    template: str

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        super().__init__(obj, **kwargs)

        if "template" in kwargs:
            self.template = kwargs["template"]

    def get_data(self) -> dict[str, Any]:
        return {
            "collection": self._collection,
        }

    def stream(self):
        yield tk.render(
            self.template,
            self.get_data(),
        )


class TableSerializer(HtmlSerializer[types.TDataCollection]):
    template: str = "collection/snippets/table.html"
    row_snippet: str = "collection/snippets/row.html"
    prefix: str = "collection-table"

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        kwargs.setdefault("template", self.template)
        super().__init__(obj, **kwargs)

        if "row_snippet" in kwargs:
            self.row_snippet = kwargs["row_snippet"]

    @property
    def form_id(self):
        return f"{self.prefix}-form--{self._collection.name}"

    @property
    def table_id(self):
        return f"{self.prefix}-id--{self._collection.name}"

    def get_data(self) -> dict[str, Any]:
        return {
            "table": self._collection,
            "row_snippet": self.row_snippet,
        }
