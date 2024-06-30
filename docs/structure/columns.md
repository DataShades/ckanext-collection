# Columns


This service contains additional information about separate columns of data
records. It defines following settings:

* names: all available column names. Used by other settings of columns service
* hidden: columns that should not be shown by serializer. Used by serializer
  services
* visible: columns that must be shown by serializer. Used by serializer
  services
* sortable: columns that support sorting. Used by data services
* filterable: columns that support filtration/facetting. Used by data services
* searchable: columns that support search by partial match. Used by data
  services
* labels: human readable labels for columns. Used by serializer services

This service contains information used by other service, so defining additional
attributes here is completely normal. For example, some custom serializer, that
serializes data into ORC, can expect `orc_format` attribute in the `columns`
service to be available. So you can add as much additional column related
details as required into this service.
