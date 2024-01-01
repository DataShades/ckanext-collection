from __future__ import annotations


from ckan.plugins import Interface

from ckanext.collection.types import CollectionFactory


class ICollection(Interface):
    """Extend functionality of ckanext-collections"""

    def get_collection_factories(self) -> dict[str, CollectionFactory]:
        """Register named collection factories.

        Example:
            def get_collection_factories(self) -> dict[str, CollectionFactory]:
                return {
                    "packages": PackageCollection,
                }
        """
        return {}
