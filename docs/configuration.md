# Configuration

```ini
# Names of registered collections that are viewable by any visitor, including
# anonymous.
# (optional, default: )
ckanext.collection.auth.anonymous_collections =

# Names of registered collections that are viewable by any authenticated
# user.
# (optional, default: )
ckanext.collection.auth.authenticated_collections =

# Add HTMX asset to pages. Enable this option if you are using CKAN v2.10
# (optional, default: false)
ckanext.collection.include_htmx_asset = false

# Initialize CKAN JS modules every time HTMX fetches HTML from the server.
# (optional, default: false)
ckanext.collection.htmx_init_modules = false

# Import path for serializer used by CSV export endpoint.
# (optional, default: ckanext.collection.utils.serialize:CsvSerializer)
ckanext.collection.export.csv.serializer = ckanext.collection.utils.serialize:CsvSerializer

# Import path for serializer used by JSON export endpoint.
# (optional, default: ckanext.collection.utils.serialize:JsonSerializer)
ckanext.collection.export.json.serializer = ckanext.collection.utils.serialize:JsonSerializer

# Import path for serializer used by JSONl export endpoint.
# (optional, default: ckanext.collection.utils.serialize:JsonlSerializer)
ckanext.collection.export.jsonl.serializer = ckanext.collection.utils.serialize:JsonlSerializer

# Import path for serializer used by `format`-export endpoint.
# (optional, default: )
ckanext.collection.export.<format>.serializer =

```
