from __future__ import annotations

import abc
from typing import Any, Generic, Iterable, Sized, TypedDict, TypeVar

from typing_extensions import Self

TDataCollection = TypeVar("TDataCollection", bound="BaseCollection")


class BaseColumns(abc.ABC, Generic[TDataCollection]):
    """Declaration of columns properties"""

    names: list[str]
    visible: set[str]
    sortable: set[str]
    filterable: set[str]
    labels: dict[str, str]


class BaseData(abc.ABC, Generic[TDataCollection], Sized, Iterable[Any]):
    """Declaration of data properties."""

    total: int
    data: Iterable[Any]


class BasePager(abc.ABC, Generic[TDataCollection]):
    """Declaration of pager properties"""

    params: dict[str, Any]
    start: Any
    end: Any
    size: Any


class BaseSerializer(abc.ABC, Generic[TDataCollection]):
    @abc.abstractmethod
    def stream(self) -> Iterable[str] | Iterable[bytes]:
        """Iterate over fragments of the content."""
        raise NotImplementedError

    @abc.abstractmethod
    def render(self) -> str | bytes:
        """Combine content fragments into a single dump."""
        raise NotImplementedError


class BaseCollection(abc.ABC):
    """Declaration of collection properties."""

    name: str
    params: dict[str, Any]

    columns: BaseColumns[Self]
    data: BaseData[Self]
    filters: BaseFilters[Self]
    pager: BasePager[Self]
    serializer: BaseSerializer[Self]


class BaseFilters(abc.ABC, Generic[TDataCollection]):
    """Declaration of filters properties."""

    filters: list[Filter]
    actions: list[Filter]


class Filter(TypedDict):
    """Filter details."""

    name: str
    options: dict[str, Any]
    type: str
