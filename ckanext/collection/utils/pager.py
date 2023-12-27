from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.collection import shared, types


class Pager(types.BasePager, shared.Domain[types.TDataCollection]):
    """Pagination logic for collections.

    This class must be abstract enough to fit into majority of pager
    implementations.

    """


class ClassicPager(Pager[types.TDataCollection]):
    """Limit/offset based pagination.

    Attributes:
      page: current active page
      rows_per_page: max number of items per page
    """

    page: int = shared.configurable_attribute(1)
    rows_per_page: int = shared.configurable_attribute(10)

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        """Use `page` and `rows_per_page` parameters."""
        super().__init__(obj, **kwargs)
        self.page = tk.h.get_page_number(self.attached.params, "page", self.page)
        self.rows_per_page = tk.h.get_page_number(
            self.attached.params,
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
    def size(self) -> Any:
        return self.rows_per_page
