from __future__ import annotations

import pytest

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
