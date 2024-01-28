from __future__ import annotations

from typing import Any

import pytest

from ckan.tests.helpers import call_action

from ckanext.collection import config, shared, utils


class TestCollection:
    def test_basic_collection_creation(self):
        obj = utils.Collection("", {})
        assert isinstance(obj.columns, utils.Columns)
        assert isinstance(obj.pager, utils.ClassicPager)
        assert isinstance(obj.filters, utils.Filters)
        assert isinstance(obj.data, utils.Data)
        assert isinstance(obj.serializer, utils.Serializer)

    def test_custom_instance(self):
        data = utils.Data(None)

        collection = utils.Collection("", {}, data_instance=data)
        assert collection.data is data
        assert data.attached is collection

    def test_custom_factory(self):
        custom_factory = utils.Data[Any, Any].with_attributes()
        collection = utils.Collection[Any]("", {}, data_factory=custom_factory)

        assert isinstance(collection.data, custom_factory)

    def test_replace_service(self):
        collection = utils.Collection("", {})
        data = utils.Data(None)
        columns = utils.Columns(None)

        assert collection.data is not data
        assert collection.columns is not columns

        collection.replace_service(data)
        collection.replace_service(columns)

        assert collection.data is data
        assert collection.columns is columns


@pytest.mark.usefixtures("with_plugins")
class TestCollectionExplorer:
    def extract_names(self, collection: utils.Collection[Any]):
        return {
            f["value"]
            for f in collection.filters.filters[0]["options"]["options"]
            if f["value"]
        }

    @pytest.mark.ckan_config(config.CONFIG_ANNONYMOUS, "hello")
    def test_only_accessible_collections_are_visible(
        self,
        collection_registry: shared.Registry[Any],
    ):
        collection_registry.register("hello", utils.Collection)
        collection_registry.register("world", utils.Collection)

        explorer = utils.CollectionExplorer("", {})

        assert self.extract_names(explorer) == {"hello"}

        user = call_action("get_site_user")
        explorer = utils.CollectionExplorer(
            "",
            {},
            filters_settings={"user": user["name"]},
        )
        assert self.extract_names(explorer) == {"hello", "world"}
