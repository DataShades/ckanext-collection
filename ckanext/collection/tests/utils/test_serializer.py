from __future__ import annotations

import csv
import json
from typing import Any

import pytest

from ckanext.collection.utils import Collection, serialize
from ckanext.collection.utils.data import StaticData


class StaticCollection(Collection[Any]):
    DataFactory = StaticData


@pytest.fixture()
def collection():
    return StaticCollection(
        "",
        {},
        data_settings={
            "data": [
                {"name": "a", "age": 1},
                {"name": "b", "age": 2},
            ],
        },
        columns_settings={
            "names": ["name", "age"],
        },
    )


class TestCsvSerializer:
    def test_output(self, collection: StaticCollection):
        serializer = serialize.CsvSerializer(collection)
        collection.serializer = serializer

        output = serializer.render().strip()
        nl = csv.get_dialect("excel").lineterminator
        expected_output = nl.join(["name,age", "a,1", "b,2"])

        assert output == expected_output


class TestJsonlSerializer:
    def test_output(self, collection: StaticCollection):
        serializer = serialize.JsonlSerializer(collection)
        collection.serializer = serializer

        output = serializer.render().strip()
        nl = "\n"
        expected_output = nl.join(map(json.dumps, collection.data))

        assert output == expected_output


class TestJsonSerializer:
    def test_output(self, collection: StaticCollection):
        serializer = serialize.JsonSerializer(collection)
        collection.serializer = serializer

        output = serializer.render().strip()
        expected_output = json.dumps(list(collection.data))

        assert output == expected_output


class TestChartJsSerializer:
    def test_output(self, collection: StaticCollection):
        serializer = serialize.ChartJsSerializer(
            collection,
            label_column="name",
            dataset_columns=["age"],
            dataset_labels={"age": "Age"},
            colors={"age": "test"},
        )
        collection.serializer = serializer

        output = serializer.render().strip()

        expected_output = json.dumps(
            {
                "labels": ["a", "b"],
                "datasets": [
                    {"data": [1, 2], "label": "Age", "backgroundColor": "test"},
                ],
            },
        )

        assert output == expected_output


class TestHtmlSerializer:
    @pytest.mark.usefixtures("with_request_context")
    def test_output(self, collection: StaticCollection, ckan_config: Any):
        serializer = serialize.HtmlSerializer(collection)
        collection.serializer = serializer
        output = serializer.render().strip()

        expected_output = (
            """<ul><li>{"age": 1, "name": "a"}</li>"""
            + """<li>{"age": 2, "name": "b"}</li></ul>"""
        )

        assert output == expected_output
