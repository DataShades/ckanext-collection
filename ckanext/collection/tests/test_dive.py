from __future__ import annotations

import pytest

from ckan import model

from ckanext.collection import internal
from ckanext.collection.utils import *


class TestOverview:
    def test_static(self):
        col = StaticCollection("name", {})
        assert list(col) == []

        col = StaticCollection("name", {}, data_settings={"data": [1, 2, 3]})
        assert list(col) == [1, 2, 3]

    @pytest.mark.usefixtures("clean_db")
    def test_model(self):
        col = ModelCollection(
            "",
            {},
            data_settings={"is_scalar": True, "model": model.User},
        )

        for user in col:
            assert isinstance(user, model.User)

    @pytest.mark.usefixtures("clean_db", "clean_index", "package")
    def test_api_search(self):
        col = ApiSearchCollection("", {}, data_settings={"action": "package_search"})

        for pkg in col:
            assert isinstance(pkg, dict)

    @pytest.mark.usefixtures("clean_db", "user")
    def test_api(self):
        col = ApiCollection("", {}, data_settings={"action": "user_list"})

        for user in col:
            assert isinstance(user, dict)


class TestInitialization:
    def test_params(self):
        col = Collection("hello", {"hello:a": 1, "b": 2, "world:c": 3})
        assert col.params == {"a": 1}

        col = Collection("world", {"hello:a": 1, "b": 2, "world:c": 3})
        assert col.params == {"c": 3}

    def test_multi(self):
        params = {"users:page": 2, "packages:page": 5}

        users = ModelCollection("users", params, data_settings={"model": model.User})
        packages = ModelCollection(
            "packages",
            params,
            data_settings={"model": model.Package},
        )

        assert isinstance(users.pager, ClassicPager)
        assert isinstance(packages.pager, ClassicPager)

        assert users.pager.page == 2
        assert packages.pager.page == 5


class TestServices:
    def test_default_initialization(self):
        col = Collection("name", {})
        assert isinstance(col.data, Data)
        assert col.pager
        assert col.serializer
        assert col.columns
        assert col.filters

    def test_service_replacement(self):
        col = Collection("name", {})
        static_data = StaticData(col, data=[1, 2, 3])
        col.replace_service(static_data)

        assert list(col) == [1, 2, 3]

    def test_factory(self):
        col = Collection("name", {}, data_factory=StaticData)
        assert list(col) == []

        col.data.data = [1, 2, 3]
        col.data.refresh_data()
        assert list(col) == [1, 2, 3]

    def test_custom_settings(self):
        col = Collection(
            "name",
            {},
            data_factory=StaticData,
            data_settings={"data": [1, 2, 3]},
        )
        assert list(col) == [1, 2, 3]

    def test_custom_service_factory(self):
        class MyCollection(Collection):
            DataFactory = StaticData

        col = MyCollection("name", {}, data_settings={"data": [1, 2, 3]})
        assert list(col) == [1, 2, 3]

    def test_with_attributes(self):
        class MyCollection(Collection):
            DataFactory = StaticData.with_attributes(data=[1, 2, 3])

        col = MyCollection("name", {})
        assert list(col) == [1, 2, 3]


class TestCommonLogic:
    def test_attached(self):
        col = Collection("name", {})
        assert col.data.attached is col
        assert col.pager.attached is col
        assert col.columns.attached is col

        another_col = Collection("another-name", {}, data_instance=col.data)
        assert col.data.attached is not col
        assert col.data.attached is another_col
        assert col.data is another_col.data

    def test_settings(self):
        col = Collection("name", {})
        data = StaticData(col, data=[], not_real=True)
        assert hasattr(data, "data")
        assert not hasattr(data, "not_real")

    def test_configurable_attributes(self):
        col = Collection("name", {})

        class MyData(StaticData):
            i_am_real = internal.configurable_attribute(False)

        data = MyData(col, data=[], i_am_real=True)
        assert hasattr(data, "data")
        assert hasattr(data, "i_am_real")
        assert data.i_am_real is True

    def test_configurable_attribute_default_factory(self):
        col = Collection("name", {})

        class MyData(StaticData):
            ref = 42
            i_am_real = internal.configurable_attribute(
                default_factory=lambda self: self.ref * 10,
            )

        data = MyData(col, data=[])
        assert data.i_am_real == 420
