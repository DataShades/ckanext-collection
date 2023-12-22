from ckan.common import CKANConfig
import ckan.plugins as p
import ckan.plugins.toolkit as tk


class CollectionPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("assets", "collection")
