[![Tests](https://github.com/DataShades/ckanext-collection/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-collection/actions)

# ckanext-collection

Base classes for presenting data series from CKAN.

## Content

* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
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

## Usage

The goal of this plugin is to supply you with generic classes for processing
collections of data. As result, it doesn't do much out of the box and you have
to write some code to see a result.

Majority of useful classes are available inside `ckanext.collection.utils`
module, so all examples below require adding the following line in the
beginning of your script: `from ckanext.collection.utils import *`.

Let's start with the basics. We have few different collections suitable for
different puproses. The most basic collection is `Collection`, but it has no
value without customization, so we'll start from `StaticCollection`:

```python
col = StaticCollection("name", {})
```

Constructor of a collection has two mandatory arguments: name and
parameters. Name is mostly used internally and consists of any combination of
letters, digits, hyphens and underscores. Parameters change the behavior of the
collection, but they have to wait as well.

We are interested in collection's purpose now. In the most basic scenario,
collection represents a number of similar items: datasets, users,
organizations, dictionaries, numbers, etc. As result, it can be transformed
into list or iterated over:

```python
list(col)

for item in col:
    print(item)
```

But our collection is empty at the moment, so you will not see anything right
now. `StaticCollection` contains static data, specified when collection is
defined. As we haven't specified any data, collection contains nothing.

To fix this problem, we have to use **settings**. Collection relies internally
on different services and each of them can be configured via settings. We are
interested in the **data** service, so we'll use
`data_settings`. `StaticCollection` has configurable attribute named `data`,
and we'll specify the content of the collection using it. All settings can be
passed to the constructor, when collection is created:

```python
col = StaticCollection("name", {}, data_settings={"data": [1,2,3]})
```

Now try again iterating over the collection and now you'll see the result:

```python
for item in col:
    print(item)
```

It's not very impressive, but you didn't expect much from **static**
collection, right? There are other collections that are more smart, but we have
to learn more concepts of this extension to use them, so for now we'll only
take a brief look on them.

**Note**: collections have certain restrictions when it comes to amount of
data. By default, you'll see only around 10 records, even if you have more. The
same is true for `StaticCollection` - you can see it if you set `data` option
of its data-service to `range(1, 100)`. We'll learn how to control these
restrictions later.

`ModelCollection` works with SQLAlchemy models. We are going to use two options
of its data-service: `model` and `is_scalar`. The former sets actual model that
collection processes, while the latter controls, how we work with every
individual record. By default, `ModelCollection` returns every record as a
number of columns, but we'll set its value to `True` and receive model instance
for every record instead:

```python
col = ModelCollection("", {}, data_settings={"is_scalar": True, "model": model.User})
for user in col:
  print(f"{user.name}, {user.email}")
```

`ApiSearchCollection` works with API actions similar to `package_search`. They
have to use `rows` and `start` parameters for pagination and their result must
contain `count` and `results` keys. Its data-service accepts `action` option
with the name of API action that produces the data:

```python
col = ApiSearchCollection("", {}, data_settings={"action": "package_search"})
for pkg in col:
  print(f"{pkg['id']}: {pkg['title']}")
```

`ApiListCollection` works with API actions similar to `package_list`. They have
to use `limit` and `offset` parameters for pagination and their result must be
represented by a list.

```python
col = ApiListCollection("", {}, data_settings={"action": "package_list"})
for name in col:
  print(name)
```

`ApiCollection` works with API actions similar to `user_list`. They have to
return all records at once, as list.

```python
col = ApiCollection("", {}, data_settings={"action": "user_list"})
for user in col:
  print(user["name"])
```


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
