from __future__ import annotations

from typing import Any

from ckanext.collection import internal, types


class Pager(types.BasePager, internal.Domain[types.TDataCollection]):
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

    prioritize_params: int = internal.configurable_attribute(True)
    page: int = internal.configurable_attribute(1)
    rows_per_page: int = internal.configurable_attribute(10)

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        """Use `page` and `rows_per_page` parameters."""
        super().__init__(obj, **kwargs)

        if self.prioritize_params:
            self.page = max(int(self.attached.params.get("page", self.page)), 1)

            self.rows_per_page = max(
                int(
                    self.attached.params.get(
                        "rows_per_page",
                        self.rows_per_page,
                    ),
                ),
                0,
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
