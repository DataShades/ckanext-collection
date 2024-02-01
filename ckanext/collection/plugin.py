from __future__ import annotations

import operator
from dataclasses import is_dataclass
from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.common import CKANConfig

from . import shared
from .interfaces import CollectionFactory, ICollection

try:
    from ckanext.ap_main.interfaces import IAdminPanel
    from ckanext.ap_main.types import ConfigurationItem, SectionConfig

    class ApImplementation(p.SingletonPlugin):  # pyright: ignore[reportRedeclaration]
        p.implements(IAdminPanel, inherit=True)

        def register_config_sections(
            self,
            config_list: list[SectionConfig],
        ) -> list[SectionConfig]:
            """Extension will receive the list of section config objects."""
            config_page = ConfigurationItem(
                name="Collections",
                info="ckanext-collection configuration",
                blueprint="ckanext-collection.ap_config",
            )
            getter: Any = (
                operator.attrgetter
                if is_dataclass(SectionConfig)
                else operator.itemgetter
            )

            for section in config_list:
                if getter("name")(section) == "Basic site settings":
                    getter("configs")(section).append(config_page)
                    break
            else:
                config_list.append(
                    SectionConfig(  # type: ignore
                        name="Basic site settings",
                        configs=[config_page],
                    ),
                )

            return config_list

except ImportError:

    class ApImplementation(p.SingletonPlugin):
        pass


@tk.blanket.blueprints
@tk.blanket.auth_functions
@tk.blanket.config_declarations
@tk.blanket.helpers
@tk.blanket.cli
class CollectionPlugin(ApImplementation, p.SingletonPlugin):
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
            from .utils import (
                CkanDbConnection,
                CollectionExplorer,
                DatastoreDbConnection,
                DbExplorer,
            )

            return {
                "collection-explorer": CollectionExplorer,
                "core-db-explorer": lambda n, p, **kwargs: DbExplorer(
                    n,
                    p,
                    **dict(kwargs, db_connection_factory=CkanDbConnection),
                ),
                "datastore-db-explorer": lambda n, p, **kwargs: DbExplorer(
                    n,
                    p,
                    **dict(kwargs, db_connection_factory=DatastoreDbConnection),
                ),
            }

        return {}
