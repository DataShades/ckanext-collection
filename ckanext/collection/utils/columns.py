
from __future__ import annotations
from typing import Any
from ckanext.collection.types import TDataCollection
from .shared import AttachTrait, AttrSettingsTrait


class Columns(AttachTrait[TDataCollection], AttrSettingsTrait):
    """Collection of columns details for filtering/rendering.

    Attributes:
      names: list of all available columns
      visible: columns that can be viewed
      sortable: columns that can be sorted
      labels: UI labels for columns
    """

    names: list[str]
    visible: set[str]
    sortable: set[str]
    filterable: set[str]
    labels: dict[str, str]

    def __init__(
        self,
        collection: TDataCollection,
        names: list[str] | None = None,
        visible: set[str] | None = None,
        hidden: set[str] | None = None,
        sortable: set[str] | None = None,
        filterable: set[str] | None = None,
        labels: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        self.attach(collection)
        self.gather_settings(kwargs)
        self.names = names if names is not None else []

        self.visible = visible if visible is not None else set(self.names)
        if hidden is not None:
            self.visible = {c for c in self.visible if c not in hidden}

        self.sortable = sortable if sortable is not None else set(self.names)
        self.filterable = filterable if filterable is not None else set(self.names)

        self.labels = labels if labels is not None else {c: c for c in self.names}
