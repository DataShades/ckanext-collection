from __future__ import annotations
import abc
import io
import csv
import json
import ckan.plugins.toolkit as tk
import operator
from functools import reduce
from typing import Any, Generic, Iterable
from ckanext.collection.types import TDataCollection


class Serializer(abc.ABC, Generic[TDataCollection]):
    _collection: TDataCollection

    def __init__(self, col: TDataCollection, /, **kwargs: Any):
        self._collection = col

    @abc.abstractmethod
    def stream(self) -> Iterable[str] | Iterable[bytes]:
        return []

    def render(self) -> str | bytes:
        return reduce(operator.add, self.stream())


class CsvSerializer(Serializer[TDataCollection]):
    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        writer = csv.DictWriter(
            buff,
            fieldnames=[
                name
                for name in self._collection.columns.names
                if name in self._collection.columns.visible
            ],
            extrasaction="ignore",
        )

        writer.writerow(
            {
                col: self._collection.columns.labels.get(col, col)
                for col in writer.fieldnames
            },
        )
        yield buff.getvalue()
        buff.seek(0)
        buff.truncate()

        for row in self._collection.data:
            writer.writerow(row)
            yield buff.getvalue()
            buff.seek(0)
            buff.truncate()


class JsonlSerializer(Serializer[TDataCollection]):
    def stream(self) -> Iterable[str]:
        buff = io.StringIO()
        for row in self._collection.data:
            json.dump(row, buff)
            yield buff.getvalue()
            yield "\n"
            buff.seek(0)
            buff.truncate()


class JsonSerializer(Serializer[TDataCollection]):
    def stream(self):
        yield json.dumps(list(self._collection.data))


class ChartJsSerializer(Serializer[TDataCollection]):
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

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
        super().__init__(obj, **kwargs)
        self.label_column = kwargs.get("label_column", "")

        self.dataset_labels = kwargs.get("dataset_labels", {})

        self.dataset_columns = kwargs.get("dataset_columns", [])
        self.colors = kwargs.get("colors", {})

    def stream(self):
        labels = []
        data: list[list[int]] = []

        for item in self._collection.data:
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


class HtmlSerializer(Serializer[TDataCollection]):
    template: str

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
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


class TableSerializer(HtmlSerializer[TDataCollection]):
    template: str = "collection/snippets/table.html"
    row_snippet: str = "collection/snippets/row.html"
    prefix: str = "collection-table"

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
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
