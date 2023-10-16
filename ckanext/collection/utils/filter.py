from __future__ import annotations
from typing import Any, Generic, TypedDict
from ckanext.collection.types import TDataCollection

class Option(TypedDict):
    """Single option for Filter."""

    value: str
    label: str


class Filter(TypedDict):
    """Dropdown filter."""

    name: str
    placeholder: str | None
    options: list[Option]


class DateRange(TypedDict):
    """After/before datepicker."""

    name: str
    label: str


class Filters(Generic[TDataCollection]):
    """Information about UI filters.

    Redefine its methods to produce information for UI filters, date-range
    field and action buttions(Download, Export, etc.).

    """

    dropdowns: list[Filter]
    date_range: DateRange | None
    actions: list[Any]

    _collection: TDataCollection

    def __init__(self, obj: TDataCollection, /, **kwargs: Any):
        self._collection = obj

        self.date_range = self.make_date_range()
        self.dropdowns = self.make_dropdowns()
        self.actions = self.make_actions()

    def make_date_range(self) -> None | DateRange:
        return
        # return DateRange(name="date_range", label="Date Range")

    def make_actions(self) -> list[Option]:
        return []

    def make_dropdowns(self) -> list[Filter]:
        return []
