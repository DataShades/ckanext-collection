[![Tests](https://github.com/DataShades/ckanext-collection/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-collection/actions)

# ckanext-collection

Base classes for presenting data series from CKAN.

## Content

* [Requirements](#requirements)
* [Installation](#installation)
* [Config settings](#config-settings)
* [License](#license)

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | no          |
| 2.10         | yes         |
| master       | yes         |

## Installation

To install ckanext-collection:

1. Install the extension:
   ```sh
   pip install ckanext-collection
   ```

1. Add `collection` to the `ckan.plugins` setting in your CKAN
   config file .

## Config settings

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

```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
