from __future__ import annotations

from typing import Iterable

from ckan.authz import is_authorized_boolean

from ckanext.collection import shared
from ckanext.collection.utils.data import Data
from ckanext.collection.utils.serialize import HtmlSerializer

from .base import Collection


class CollectionExplorerCollection(Collection[str]):
    """Collection of all registered collections.

    It exists for debugging and serves as an example of non-canonical usage of
    collections.
    """

    class DataFactory(Data[str, "CollectionExplorerCollection"], shared.UserTrait):
        static_names = shared.configurable_attribute(
            default_factory=lambda self: map(str, shared.collection_registry.members),
        )

        def compute_data(self) -> Iterable[str]:
            return [
                name
                for name in self.static_names
                if name != self.attached.name
                and is_authorized_boolean(
                    "collection_view_render",
                    {"user": self.user},
                    {"name": name},
                )
            ]

    class SerializerFactory(HtmlSerializer["CollectionExplorerCollection"]):
        main_template: str = shared.configurable_attribute(
            "collection/serialize/collection_explorer/main.html",
        )
