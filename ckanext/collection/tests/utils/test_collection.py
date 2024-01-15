from __future__ import annotations

from typing import Any

from ckanext.collection import utils


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
