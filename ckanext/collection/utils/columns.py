from __future__ import annotations
from typing import Generic
import dataclasses
from ckanext.collection.types import TDataCollection


@dataclasses.dataclass
class Columns(Generic[TDataCollection]):
    """Collection of columns details for filtering/rendering.

    Attributes:
      names: list of all available columns
      visible: columns that can be viewed
      sortable: columns that can be sorted
      labels: UI labels for columns
    """

    _collection: TDataCollection
    names: list[str] = dataclasses.field(default_factory=list)
    visible: set[str] = dataclasses.field(default_factory=set)
    sortable: set[str] = dataclasses.field(default_factory=set)
    labels: dict[str, str] = dataclasses.field(default_factory=dict)
