from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ckanext.collection import internal, types


class Pager(types.BasePager, internal.Domain[types.TDataCollection]):
    """Base for pager service.

    This class must be extended by every implementation of the pager service.

    Example:
        ```python
        class StaticPager(Pager):
            @property
            def start(self) -> int:
                return 0

            @property
            def end(self) -> int:
                return 10

            @property
            def size(self) -> int:
                return 10
        ```

    """


class ClassicPager(Pager[types.TDataCollection]):
    """Page-number based pagination.

    Attributes:
        page: current active page
        rows_per_page: max number of items per page
        prioritize_params: if `params` contain pagination details,
            use them instead of `pager_settings`. Defaults to True.

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.StaticData,
        >>>     data_settings={"data": range(1, 100)},
        >>>     pager_factory=pager.ClassicPager,
        >>>     pager_settings={"page": 2, "rows_per_page": 5},
        >>> )
        >>> list(col)
        [6, 7, 8, 9, 10]
        ```
    """

    prioritize_params: bool = internal.configurable_attribute(True)
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


class OffsetPager(Pager[types.TDataCollection]):
    """Limit/offset based pagination.

    Attributes:
        offset: number of items to skip
        limit: max number of items per page

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.StaticData,
        >>>     data_settings={"data": range(1, 100)},
        >>>     pager_factory=pager.OffsetPager,
        >>>     pager_settings={"offset": 2, "limit": 3},
        >>> )
        >>> list(col)
        [3, 4, 5]
        ```
    """

    offset: int = internal.configurable_attribute(0)
    limit: int = internal.configurable_attribute(10)

    @property
    def start(self) -> int:
        return self.offset

    @property
    def end(self) -> int:
        return self.start + self.size

    @property
    def size(self) -> Any:
        return self.limit


class TemporalPager(Pager[types.TDataCollection]):
    """Date based pagination.

    Data service of the collection that uses TemporalPager must implement
    `range` as `range(start: date | None, end: date | None)`.

    Attributes:
        since: date of the oldest record(`>=`)
        until: date of the newest record(`<`)

    Example:
        Define data service that supports date ranges.

        ```python
        from datetime import datetime, timedelta

        class TemporalModelData(data.TemporalSaData, data.ModelData):
            pass
        ```

        Initialize the collection

        ```python
        >>> col = collection.Collection(
        >>>     data_factory=TemporalModelData,
        >>>     data_settings={
        >>>         "model": model.Package,
        >>>         "temporal_column": model.Package.metadata_created,
        >>>     },
        >>>     pager_factory=pager.TemporalPager,
        >>>     pager_settings={"since": datetime.now() - timedelta(days=1)},
        >>> )
        >>> list(col)
        [(...package created yesterday), ...]
        ```

    """

    since: date | None = internal.configurable_attribute(None)
    until: date | None = internal.configurable_attribute(None)

    @property
    def start(self) -> date | None:
        return self.since

    @property
    def end(self) -> date | None:
        return self.until

    @property
    def size(self) -> timedelta:
        return (self.end or date.max) - (self.start or date.min)
