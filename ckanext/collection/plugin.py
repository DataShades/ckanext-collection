from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.common import CKANConfig

from . import shared
from .interfaces import CollectionFactory, ICollection


@tk.blanket.blueprints
@tk.blanket.auth_functions
@tk.blanket.config_declarations
@tk.blanket.helpers
@tk.blanket.cli
class CollectionPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IConfigurable)
    p.implements(ICollection, inherit=True)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "collection")

    # IConfigurable
    def configure(self, config_: CKANConfig):
        shared.collection_registry.reset()

        for plugin in p.PluginImplementations(ICollection):
            for name, factory in plugin.get_collection_factories().items():
                shared.collection_registry.register(name, factory)

    def get_collection_factories(self) -> dict[str, CollectionFactory]:
        if tk.config["debug"]:
            from .utils import CollectionExplorer, DatastoreDbConnection, DbExplorer

            return {
                "collection-explorer": CollectionExplorer,
                "core-db-explorer": lambda n, p, **kwargs: DbExplorer(
                    n,
                    p,
                    **dict(kwargs, db_connection_factory=DatastoreDbConnection),
                ),
            }

        return {}
