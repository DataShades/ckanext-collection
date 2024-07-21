# Columns

## Overview

This service contains additional information about separate columns of data
records. It defines following settings:

* names: all available column names. Used by other settings of columns service
* hidden: `names` members that should not be serialized
* visible: `names` members that must be serialized
* sortable: `names` members that support sorting
* filterable: `names` members that support filtration/facetting
* searchable: `names` members that support search by partial match
* labels: human readable labels for `names` members

There are not rules regarding usage of this service. Any serializer, data
service or any other service can use information from the columns service or
ignore it.

You can also add more properties to this service. For example, if you want to
use specific order of columns inside your custom implementation of CSV
serializer, you can add `order` attribute to the columns service and read it
during serialization.

If you are not going to share your custom services, you can ignore columns
service. Otherwise, it's recommended to keep any column-related options
here.

For example, almost all built-in serializers of ckanext-collection use
`visible`/`hidden` attributes of the columns service to include/exclude certain
fields into serialization output. In this way you can switch to a different
serializer with a minimal amount of setings and receive the same set of fields
serialized into a different format.

/// admonition
    type: example

```pycon
>>> col = collection.Collection(
>>>     data_factory=data.ModelData.with_attributes(model=model.User),
>>>     columns_factory=columns.Columns.with_attributes(
>>>         names={"name", "id", "sysadmin"},
>>>         hidden={"id"},
>>>     )
>>> )
>>> serialize.CsvSerializer(col).serialize()
name,sysadmin
default,True
>>> serialize.JsonSerializer(col).serialize()
[{"sysadmibn": true, "name": "default"}]
```

///
## Available columns factories

::: collection.shared.columns.Columns
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []
