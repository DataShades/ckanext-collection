from __future__ import annotations

from typing import Any

import pytest
import sqlalchemy as sa
from sqlalchemy.engine import Row

from ckan import model

from ckanext.collection.utils import Collection, data


@pytest.fixture()
def collection():
    return Collection("", {})


class TestStaticData:
    def test_settings(self, collection: Collection):
        dump = [{"a": 1}, {"a": 2}]
        obj = data.StaticData(collection, initial_data=dump)

        assert obj.data == dump
        assert list(obj) == dump
        assert len(obj) == len(dump)
        assert obj.total == len(dump)

    def test_pagination(self):
        dump = [{"a": 1}, {"a": 2}]

        collection = Collection(
            "",
            {"page": 2, "rows_per_page": 1},
            data_settings={"initial_data": dump},
            data_factory=data.StaticData,
        )

        assert list(collection.data) == [dump[1]]
        assert len(collection.data) == 1
        assert collection.data.total == 2


@pytest.mark.usefixtures("clean_db")
class TestModelData:
    def test_empty_result(self, collection: Collection):
        obj = data.ModelData(collection, model=model.Package)
        assert obj.total == 0

    def test_non_empty_result(self, package_factory: Any, collection: Collection):
        package_factory.create_batch(3)
        obj = data.ModelData(collection, model=model.Package)
        assert isinstance(list(obj)[0], Row)

    def test_scalar(self, package: Any, collection: Collection):
        obj = data.ModelData(collection, model=model.Package)
        assert isinstance(list(obj)[0], Row)

        obj = data.ModelData(collection, model=model.Package, is_scalar=True)
        assert isinstance(list(obj)[0], model.Package)

    def test_columns(self, package: Any, collection: Collection):
        obj = data.ModelData(collection, model=model.Package)
        row = next(iter(obj))
        assert hasattr(row, "id")
        assert hasattr(row, "name")

        obj = data.ModelData(
            collection,
            model=model.Package,
            static_columns=[model.Package.id],
        )
        row = next(iter(obj))
        assert hasattr(row, "id")
        assert not hasattr(row, "name")

    def test_joins(self, package_factory: Any, collection: Collection):
        parent = package_factory()
        child = package_factory(notes=parent["id"])

        child_alias = sa.alias(model.Package)
        obj = data.ModelData(
            collection,
            model=model.Package,
            static_sources={"child": child_alias},
            static_columns=[
                model.Package.name.label("parent"),
                child_alias.c.name.label("child"),
            ],
            static_joins=[("child", child_alias.c.notes == model.Package.id, False)],
        )
        row = next(iter(obj))
        assert row.parent == parent["name"]
        assert row.child == child["name"]

    def test_filters(self, package_factory: Any, collection: Collection):
        pkg = package_factory(notes="x")
        package_factory(notes="y")

        obj = data.ModelData(
            collection,
            model=model.Package,
            static_filters=[model.Package.notes == "x"],
        )
        assert obj.total == 1
        assert next(iter(obj)).id == pkg["id"]

    def test_sorting(self, package_factory: Any):
        ids = sorted([pkg["id"] for pkg in package_factory.create_batch(3)])

        collection = Collection("", {})
        obj = data.ModelData(
            collection,
            model=model.Package,
            is_scalar=True,
            static_columns=[model.Package.id],
        )

        collection.params["sort"] = "id"
        obj.refresh_data()
        assert list(obj) == ids

        collection.params["sort"] = "-id"
        obj.refresh_data()
        assert list(obj) == list(reversed(ids))

        collection.params["sort"] = "id asc"
        obj.refresh_data()
        assert list(obj) == ids

        collection.params["sort"] = "id desc"
        obj.refresh_data()
        assert list(obj) == list(reversed(ids))

    def test_limits(self, package_factory: Any):
        ids = sorted([pkg["id"] for pkg in package_factory.create_batch(3)])

        collection = Collection(
            "",
            {"sort": "id"},
            pager_settings={"page": 2, "rows_per_page": 1},
        )
        obj = data.ModelData(
            collection,
            model=model.Package,
            is_scalar=True,
            static_columns=[model.Package.id],
        )

        assert obj.total == 3
        assert len(obj) == 1
        assert next(iter(obj)) == ids[1]
