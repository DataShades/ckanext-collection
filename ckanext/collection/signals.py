import ckan.plugins.toolkit as tk

register_collection_signal = tk.signals.ckanext.signal(
    "collection:register_collections",
)
