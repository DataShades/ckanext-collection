from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .utils.collection import BaseCollection


TDataCollection = TypeVar("TDataCollection", bound="BaseCollection")
