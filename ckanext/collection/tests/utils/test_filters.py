from __future__ import annotations

import pytest

from ckanext.collection.utils import Collection, filters


@pytest.fixture()
def collection():
    return Collection("", {})


class TestFilters:
    def test_settings(self, collection: Collection):
        obj = filters.Filters(collection)
        assert obj.filters == []
        assert obj.actions == []

        obj = filters.Filters(collection, static_filters=[1, 2, 3])
        assert obj.filters == [1, 2, 3]
        assert obj.actions == []
