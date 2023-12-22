from __future__ import annotations

import abc
from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.collection import types

from .shared import AttachTrait, AttrSettingsTrait


class Pager(
    types.BasePager[types.TDataCollection],
    AttachTrait[types.TDataCollection],
    AttrSettingsTrait,
    abc.ABC,
):
    """Pagination logic for collections.

    This class must be abstract enough to fit into majority of pager
    implementations.

    """

    params: dict[str, Any]

    @abc.abstractproperty
    def start(self) -> Any:
        """Inclusive lower bound of the page.

        For classic limit/offset pagination, start:0 means that index of the
        first element is 0.

        """
        ...

    @abc.abstractproperty
    def end(self) -> Any:
        """Exclusive upper bound of the page.

        For classic limit/offset pagination, end:10 means that index of the
        last element is less than 10.

        """
        ...

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        """Get relevant information from search params and store it inside pager."""
        self.attach(obj)
        self.gather_settings(kwargs)

        self.params = kwargs.get("params", {})

    @property
    def size(self):
        """Range of the pager.

        In classic pager it may be the number of items per page. For date range
        pager, it can be a timespan within which we are searching for records.

        """
        return self.start - self.end


class ClassicPager(Pager[types.TDataCollection]):
    """Limit/offset based pagination.

    Attributes:
      page: current active page
      rows_per_page: max number of items per page
    """

    page: int = 1
    rows_per_page: int = 10

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        """Use `page` and `rows_per_page` parameters."""
        super().__init__(obj, **kwargs)
        self.page = tk.h.get_page_number(self.params, "page", self.page)
        self.rows_per_page = tk.h.get_page_number(
            self.params,
            "rows_per_page",
            self.rows_per_page,
        )

    @property
    def start(self) -> int:
        return self.size * self.page - self.size

    @property
    def end(self) -> int:
        return self.start + self.size

    @property
    def size(self):
        return self.rows_per_page
