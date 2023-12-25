from __future__ import annotations

import abc
from typing import Any, Iterable, Sized, TypedDict, TypeVar

TDataCollection = TypeVar("TDataCollection", bound="BaseCollection")


class BaseColumns(abc.ABC):
    """Declaration of columns properties"""

    names: list[str]
    visible: set[str]
    sortable: set[str]
    filterable: set[str]
    labels: dict[str, str]


class BaseData(abc.ABC, Sized, Iterable[Any]):
    """Declaration of data properties."""

    total: int
    data: Iterable[Any]


class BasePager(abc.ABC):
    """Declaration of pager properties"""

    params: dict[str, Any]

    @property
    def size(self) -> Any:
        """Range of the pager.

        In classic pager it may be the number of items per page. For date range
        pager, it can be a timespan within which we are searching for records.

        """
        return self.start - self.end

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


class BaseSerializer(abc.ABC):
    @abc.abstractmethod
    def stream(self) -> Iterable[str] | Iterable[bytes]:
        """Iterate over fragments of the content."""
        ...

    @abc.abstractmethod
    def render(self) -> str | bytes:
        """Combine content fragments into a single dump."""
        ...


class BaseCollection(abc.ABC):
    """Declaration of collection properties."""

    name: str
    params: dict[str, Any]

    columns: BaseColumns
    data: BaseData
    filters: BaseFilters
    pager: BasePager
    serializer: BaseSerializer


class BaseFilters(abc.ABC):
    """Declaration of filters properties."""

    filters: list[Filter]
    actions: list[Filter]


class Filter(TypedDict):
    """Filter details."""

    name: str
    options: dict[str, Any]
    type: str
