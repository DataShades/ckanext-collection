from __future__ import annotations

import csv
import json
from typing import Any

import pytest

from ckanext.collection.utils import Collection, serialize
from ckanext.collection.utils.data import StaticData


class StaticCollection(Collection):
    DataFactory = StaticData


@pytest.fixture()
def collection():
    return StaticCollection(
        "",
        {},
        data_settings={
            "data": [
                {
                    "name": "a",
                    "age": 1,
                },
                {
                    "name": "b",
                    "age": 2,
                },
            ],
        },
        columns_settings={
            "names": ["name", "age"],
        },
    )


class TestSerializer:
    def test_value_serializers(self, faker):
        record = {"name": faker.word(), "age": faker.pyint(), "gender": None}
        collection = StaticCollection(
            "",
            {},
            columns_settings={
                "serializers": {"name": [("up", {})], "age": [("xN", {"scale": 10})]},
            },
            serializer_settings={
                "value_serializers": {
                    "up": lambda value, *_: value.upper(),
                    "xN": lambda value, options, *_: value * options["scale"],
                },
            },
        )
        assert collection.serializer.serialize_value(
            record["name"],
            "name",
            record,
        ) == str.upper(record["name"])
        assert (
            collection.serializer.serialize_value(record["age"], "age", record)
            == record["age"] * 10
        )
        assert (
            collection.serializer.serialize_value(record["gender"], "gender", record)
            == record["gender"]
        )


class TestCsvSerializer:
    def test_output(self, collection: StaticCollection):
        serializer = serialize.CsvSerializer(collection)

        output = serializer.serialize().strip()
        nl = csv.get_dialect("excel").lineterminator
        expected_output = nl.join(["name,age", "a,1", "b,2"])

        assert output == expected_output


class TestJsonlSerializer:
    def test_output(self, collection: StaticCollection):
        serializer = serialize.JsonlSerializer(collection)

        output = serializer.serialize().strip()
        nl = "\n"
        expected_output = nl.join(map(json.dumps, collection.data))

        assert output == expected_output


class TestJsonSerializer:
    def test_output(self, collection: StaticCollection):
        serializer = serialize.JsonSerializer(collection)

        output = serializer.serialize().strip()
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

        output = serializer.serialize().strip()

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
        output = serializer.render().strip()
        expected_output = """<ul><li>{&#39;name&#39;: &#39;a&#39;, &#39;age&#39;: 1}</li><li>{&#39;name&#39;: &#39;b&#39;, &#39;age&#39;: 2}</li></ul>"""

        assert output == expected_output
