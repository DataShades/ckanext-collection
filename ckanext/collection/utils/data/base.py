from __future__ import annotations

from functools import cached_property
from typing import Any, Generic, Iterable, Iterator

from ckanext.collection import internal, types


class Data(
    types.BaseData,
    internal.Domain[types.TDataCollection],
    Generic[types.TData, types.TDataCollection],
):
    """Base data source for collection.

    This class defines an outline of the data service. In basic case, sublcass
    should override `compute_data` method and return a Sequence from it to keep
    all methods functional.

    Example:
        ```python
        class MyData(data.Data):
            def compute_data(self):
                return range(1, 20)
        ```

    """

    @cached_property
    def _data(self):
        return self.compute_data()

    @cached_property
    def _total(self) -> int:
        return self.compute_total(self._data)

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

    def __getitem__(self, key: Any):
        if isinstance(key, slice):
            return self.range(key.start, key.stop)
        return self.at(key)

    def compute_data(self) -> Any:
        """Produce data."""
        return []

    def compute_total(self, data: Any) -> int:
        """Compute number of data records."""
        return len(data)

    def range(self, start: Any, end: Any) -> Iterable[types.TData]:
        """Slice data."""
        return self._data[start:end]

    def at(self, index: Any) -> types.TData:
        """Slice data."""
        return self._data[index]

    @property
    def total(self):
        return self._total
