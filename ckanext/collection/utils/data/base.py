from __future__ import annotations

from functools import cached_property
from typing import Any, Iterable, Iterator

from ckanext.collection import shared, types


class Data(
    types.BaseData[types.TData],
    shared.Domain[types.TDataCollection],
):
    """Data source for collection.

    This class produces data for collection.

    """

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        super().__init__(obj, **kwargs)

    def __iter__(self) -> Iterator[types.TData]:
        yield from self._data

    def __len__(self):
        return self.total

    def refresh_data(self):
        """Update data and counters.

        Use this method when parameters that affect Data are changed. This is a
        cheaper alternative of recreating the whole collection with new
        parameters.

        """
        self._data = self.compute_data()
        self._total = self.compute_total(self._data)

    def compute_data(self) -> Any:
        """Produce data."""
        return []

    def compute_total(self, data: Any) -> int:
        """Compute number of data records."""
        return len(data)

    def range(self, start: Any, end: Any) -> Iterable[types.TData]:
        """Slice data."""
        return self._data[start:end]

    @property
    def total(self):
        return self._total

    @cached_property
    def _data(self):
        return self.compute_data()

    @cached_property
    def _total(self) -> int:
        return self.compute_total(self._data)
