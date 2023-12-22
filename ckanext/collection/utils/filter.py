from __future__ import annotations

from typing import Any

from ckanext.collection import types

from .shared import AttachTrait, AttrSettingsTrait


class Filters(
    types.BaseFilters[types.TDataCollection],
    AttachTrait[types.TDataCollection],
    AttrSettingsTrait,
):
    """Information about UI filters.

    Redefine its methods to produce information for UI filters, date-range
    field and action buttions(Download, Export, etc.).

    """

    def __init__(self, obj: types.TDataCollection, /, **kwargs: Any):
        self.attach(obj)
        self.gather_settings(kwargs)

        self.date_range = kwargs.get("date_range", self.make_date_range())
        self.dropdowns = kwargs.get("dropdowns", self.make_dropdowns())
        self.actions = kwargs.get("actions", self.make_actions())

    def make_date_range(self) -> None | types.DateRange:
        return
        # return DateRange(name="date_range", label="Date Range")

    def make_actions(self) -> list[types.Option]:
        return []

    def make_dropdowns(self) -> list[types.Filter]:
        return []
