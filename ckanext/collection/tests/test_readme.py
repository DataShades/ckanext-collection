from __future__ import annotations

import csv
import json
import os
from io import StringIO
from typing import Any, cast

import pytest

from ckan import model
from ckan.tests.factories import CKANFactory

import ckanext.collection.utils as cu


class TestModelCollection(cu.Collection):
    DataFactory = cu.ModelData.with_attributes(model=model.Resource)
    ColumnsFactory = cu.Columns.with_attributes(names=["name", "size"])


## collection of all packages available via search API
class TestApiCollection(cu.Collection):
    DataFactory = cu.ApiSearchData.with_attributes(action="package_search")
    ColumnsFactory = cu.Columns.with_attributes(names=["name", "title"])


## collection of all records from CSV file
class TestCsvCollection(cu.Collection):
    DataFactory = cu.CsvData.with_attributes(
        source=os.path.join(os.path.dirname(__file__), "data/file.csv"),
    )
    ColumnsFactory = cu.Columns.with_attributes(names=["a", "b"])


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestQuickstart:
    def test_model(self, resource_factory: type[CKANFactory]):
        col = TestModelCollection("", {})
        assert col.data.total == 0

        resource_factory.create_batch(3)

        col = TestModelCollection("", {})
        assert col.data.total == 3

        serializer = cu.JsonSerializer(col)
        expected = [{"name": r.name, "size": r.size} for r in col.data]
        assert json.loads(serializer.serialize()) == expected

        serializer = cu.CsvSerializer(col)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["name", "size"])
        writer.writerows([[r.name, r.size] for r in col.data])
        assert serializer.serialize() == output.getvalue()

        serializer = cu.DictListSerializer(col)
        expected = [{"name": r.name, "size": r.size} for r in col.data]
        assert serializer.serialize() == expected

    def test_api(self, package_factory: type[CKANFactory]):
        col = TestApiCollection("", {})
        assert col.data.total == 0

        package_factory.create_batch(3)

        col = TestApiCollection("", {})
        assert col.data.total == 3

        serializer = cu.JsonSerializer(col)
        expected = [{"name": r["name"], "title": r["title"]} for r in col.data]
        assert json.loads(serializer.serialize()) == expected

        serializer = cu.CsvSerializer(col)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["name", "title"])
        writer.writerows([[r["name"], r["title"]] for r in col.data])
        assert serializer.serialize() == output.getvalue()

        serializer = cu.DictListSerializer(col)
        expected = [{"name": r["name"], "title": r["title"]} for r in col.data]
        assert serializer.serialize() == expected

    def test_csv(self, package_factory: type[CKANFactory]):
        filename = cast(Any, TestCsvCollection.DataFactory).source
        col = TestCsvCollection("", {})
        assert col.data.total == 16

        assert len(list(col)) == 10
        assert len(list(col.data)) == 16
        assert len(list(col.data.range(2, 5))) == 3

        serializer = cu.JsonSerializer(col)
        with open(filename) as src:
            expected = [{"a": r["a"], "b": r["b"]} for r in csv.DictReader(src)]
        assert json.loads(serializer.serialize()) == expected

        serializer = cu.CsvSerializer(col)
        output = StringIO()
        with open(filename) as src:
            writer = csv.writer(output)
            for row in csv.reader(src):
                writer.writerow(row[:-1])
        assert serializer.serialize() == output.getvalue()

        serializer = cu.DictListSerializer(col)
        with open(filename) as src:
            expected = [{"a": r["a"], "b": r["b"]} for (r) in csv.DictReader(src)]
        assert serializer.serialize() == expected
