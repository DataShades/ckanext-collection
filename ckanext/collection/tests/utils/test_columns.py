from __future__ import annotations

import pytest

from ckanext.collection.utils import Collection, columns


@pytest.fixture()
def collection():
    return Collection("", {})


class TestColumns:
    def test_defaults(self, collection: Collection):
        obj = columns.Columns(collection)
        assert obj.names == []
        assert obj.hidden == set()
        assert obj.visible == set()
        assert obj.sortable == set()
        assert obj.filterable == set()
        assert obj.labels == {}

    def test_names(self, collection: Collection):
        names = ["a", "b", "c"]
        obj = columns.Columns(collection, names=names)
        assert obj.names == names
        assert obj.hidden == set()
        assert obj.visible == set(names)
        assert obj.sortable == set(names)
        assert obj.filterable == set(names)
        assert obj.labels == {n: n for n in names}

    def test_hidden(self, collection: Collection):
        names = ["a", "b", "c"]
        obj = columns.Columns(collection, names=names, hidden={"b"})
        assert obj.names == names
        assert obj.hidden == {"b"}
        assert obj.visible == {"a", "c"}
