from __future__ import annotations

import pytest

from ckanext.collection.utils import Collection, pager


@pytest.fixture()
def collection():
    return Collection("", {})


class TestClassicPager:
    def test_settings(self, collection: Collection):
        obj = pager.ClassicPager(collection)
        assert obj.page == 1
        assert obj.size == 10

        obj = pager.ClassicPager(collection, page=5, rows_per_page=101)
        assert obj.page == 5
        assert obj.size == 101

    def test_params_has_higher_proirity_than_settings(self, collection: Collection):
        obj = pager.ClassicPager(collection, params={"page": 2, "rows_per_page": 5})
        assert obj.page == 2
        assert obj.size == 5

    @pytest.mark.parametrize(
        ("page", "size", "start", "end"),
        [
            (1, 10, 0, 10),
            (3, 2, 4, 6),
            (10, 1, 9, 10),
        ],
    )
    def test_logic(
        self,
        collection: Collection,
        page: int,
        size: int,
        start: int,
        end: int,
    ):
        obj = pager.ClassicPager(
            collection,
            params={"page": page, "rows_per_page": size},
        )
        assert obj.size == size
        assert obj.start == start
        assert obj.end == end
