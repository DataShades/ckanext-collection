from __future__ import annotations

from typing import Any
from unittest import mock

import pytest
import sqlalchemy as sa
from sqlalchemy.engine import Row

from ckan import model

from ckanext.collection.utils import Collection, data


@pytest.fixture()
def collection() -> Collection[Any]:
    return Collection("", {})


class TestLaziness:
    @mock.patch.object(data.Data, "compute_data", return_value=[])
    def test_data(self, stub: mock.Mock):
        obj = data.Data(None)
        assert not stub.called

        assert obj.total == 0
        assert stub.called

        stub.reset_mock()

        obj = data.Data(None)
        assert not stub.called

        assert list(obj) == []
        assert stub.called

        stub.reset_mock()

        obj = data.Data(None)
        assert list(obj) == []
        assert len(obj) == 0
        assert list(obj) == []
        assert len(obj) == 0

        stub.assert_called_once()

    @mock.patch.object(data.Data, "compute_total", return_value=0)
    def test_total(self, stub: mock.Mock):
        obj = data.Data(None)
        assert not stub.called

        assert obj.total == 0
        assert stub.called

        stub.reset_mock()

        obj = data.Data(None)
        assert not stub.called

        assert obj._data == []
        assert not stub.called

        stub.reset_mock()

        obj = data.Data(None)
        assert list(obj) == []
        assert len(obj) == 0
        assert list(obj) == []
        assert len(obj) == 0

        stub.assert_called_once()


class TestStaticData:
    def test_settings(self, collection: Collection[Any]):
        dump = [{"a": 1}, {"a": 2}]
        obj = data.StaticData(collection, data=dump)

        assert list(obj) == dump
        assert len(obj) == len(dump)

    def test_pagination(self):
        dump = [{"a": 1}, {"a": 2}]

        collection = Collection[Any](
            "",
            {"page": 2, "rows_per_page": 1},
            data_settings={"data": dump},
            data_factory=data.StaticData,
        )

        assert list(collection) == [dump[1]]
        assert len(collection.data) == 2


@pytest.mark.usefixtures("clean_db")
class TestModelData:
    def test_empty_result(self, collection: Collection[Any]):
        obj = data.ModelData(collection, model=model.Package)
        assert obj.total == 0

    def test_non_empty_result(self, package_factory: Any, collection: Collection[Any]):
        package_factory.create_batch(3)
        obj = data.ModelData(collection, model=model.Package)
        assert isinstance(list(obj)[0], Row)
        assert obj.total == 3
        assert len(list(obj)) == 3

    def test_scalar(self, package: Any, collection: Collection[Any]):
        obj = data.ModelData(collection, model=model.Package)
        assert isinstance(list(obj)[0], Row)

        obj = data.ModelData(collection, model=model.Package, is_scalar=True)
        assert isinstance(list(obj)[0], model.Package)

    def test_columns(self, package: Any, collection: Collection[Any]):
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

    def test_joins(self, package_factory: Any, collection: Collection[Any]):
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

    def test_filters(self, package_factory: Any, collection: Collection[Any]):
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
            data_factory=data.ModelData,
            data_settings={
                "model": model.Package,
                "is_scalar": True,
                "static_columns": [model.Package.id],
            },
        )

        assert list(collection) == [ids[1]]


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestApiSearchData:
    def test_base(self, package_factory: Any):
        ids = sorted([pkg["id"] for pkg in package_factory.create_batch(3)])

        collection = Collection("", {})
        obj = data.ApiSearchData(collection, action="package_search")

        assert obj.total == 3
        assert sorted([p["id"] for p in obj]) == ids

        obj = data.ApiSearchData(
            collection,
            action="package_search",
            payload={"fq": "id:" + ids[1]},
        )

        assert obj.total == 1
        assert next(iter(obj))["id"] == ids[1]


@pytest.mark.usefixtures("clean_db")
class TestApiListData:
    def test_base(self, organization_factory: Any):
        ids = sorted([o["name"] for o in organization_factory.create_batch(3)])

        collection = Collection("", {})
        obj = data.ApiListData(collection, action="organization_list")

        assert obj.total == 3
        assert sorted(obj) == ids

    def test_payload(self, organization_factory: Any):
        organization_factory(type="custom")

        collection = Collection("", {})

        obj = data.ApiListData(collection, action="organization_list")
        assert obj.total == 0

        obj = data.ApiListData(
            collection,
            action="organization_list",
            payload={"type": "custom"},
        )
        assert obj.total == 1
