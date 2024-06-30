# Filters


This service used only by HTML table serializers at the moment. It has two
configurable attributes `static_filters` and `static_actions`. `static_filters`
are used for building search form for the data table. `static_actions` are not
used, but you can put into it details about batch or record-level actions and
use these details to extend one of standard serializers. For example,
ckanext-admin-panel defines allowed actions (remove, restore, hide) for content
and creates custom templates that are referring these actions.
