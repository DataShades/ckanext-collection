from __future__ import annotations
from typing import Any
import pytest

from ckanext.collection.utils import *


class TestCollection:
    def test_basic_collection_creation(self):
        obj = Collection("", {})
        assert isinstance(obj.columns, Columns)
        assert isinstance(obj.pager, ClassicPager)
        assert isinstance(obj.filters, Filters)
        assert isinstance(obj.data, Data)
        assert isinstance(obj.serializer, Serializer)

    def test_custom_instance(self):
        data = Data(None)

        collection = Collection("", {}, data_instance=data)
        assert collection.data is data
        assert data.attached is collection

    def test_custom_factory(self):
        custom_factory = Data[Any, Any].with_attributes()
        collection = Collection[Any]("", {}, data_factory=custom_factory)

        assert isinstance(collection.data, custom_factory)

    def test_replace_service(self):
        collection = Collection("", {})
        data = Data(None)
        columns = Columns(None)

        assert collection.data is not data
        assert collection.columns is not columns

        collection.replace_service(data)
        collection.replace_service(columns)

        assert collection.data is data
        assert collection.columns is columns
