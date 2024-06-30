# Structure of the collection

## Introduction

Collections are designed to describe the data. Most common logic often can be
define declaratively and all imperative commands are ether hidden deep inside
different parts of collection or injected as tiny lambda-functions.

But describing the data is not simple, especially if data needs to be
interactive. As result, collections have complex internal structure. Good news,
you don't need to know everything in order to use the collections. As long as
you need something simple, you can use the minimum of knowledge.

Look how collection with all the users from DB can be created:

/// tab | Using anonymous classes and verbose initialization
```python
from ckan import model
from ckanext.collection.shared import collection

users = collection.ModelCollection(data_settings={"model": model.User})

```
///

/// tab | Using dedicated class and simple initialization
```python
from ckan import model
from ckanext.collection.shared import collection, data

class Users(collection.Collection):
    DataFactory = data.ModelData.with_attributes(model=model.User)

users = Users()
```
///

For the standard scenarios, ckanext-collection already contains a number of
classes that do the heavy lifting. And in future, as more popular scenarios
discovered, the number of classes will grow.

Still, custom requirements are often appear in the project. Because of it,
understanding how collection works and how it can be customized is the key
point in building the perfect collection.

## Services

Collection itself contains just a bare minimum of logic, and real magic happens
inside its *services*. Collection knows how to initialize services and usually
the only difference between all your collections, is the way all their services
are configured.

Collection contains the following standard services:

* `data`: controls the exact data that can be received from
  collection. Contains logic for searching, filters, sorting, etc.
* `pager`: defines restrictions for data iteration. Exactly this service limits
  results to 10 records when you iterating over collection.
* `serializer`: specifies how collection can be transformed into specific
  format. Using correct serializer you'll be able to dump the whole collection
  as CSV, JSON, YAML or render it as HTML table.
* `columns`: contains configuration of specific data columns used by other
  services. It may define model attributes that are dumped into CSV, names of
  the transformation functions that are applied to the certain attribute, names
  of the columns that are available for sorting in HTML representation of data.
* `filters`: contains configuration of additional widgets produced during data
  serialization. For example, when data is serialized into an HTML table,
  filters can define configuration of dropdowns and input fields from the data
  search form.

/// tip

You can define more services in custom collections. The list above only
enumerates all the services that are available in the base collection and in
all collections shipped with the current extension. For example, one of
built-in collections, `DbCollection` has additional service called
`db_connection` that can communicate with DB.

///
