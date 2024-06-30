# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## Unreleased

<small>[Compare with latest](https://github.com/DataShades/ckanext-collection/compare/v0.1.2...HEAD)</small>

### Features

- Serializer.dictize_row returns only Columns.visible ([0ad5295](https://github.com/DataShades/ckanext-collection/commit/0ad5295fd6a5c463befe3630b4b46dd801c3ac9b) by Sergey Motornyuk).

### Code Refactoring

- Columns filterable and sortable are empty by default ([aeb3950](https://github.com/DataShades/ckanext-collection/commit/aeb3950bda6013a680d9f48bba9d481d52d0bd47) by Sergey Motornyuk).

<!-- insertion marker -->
## [v0.1.2](https://github.com/DataShades/ckanext-collection/releases/tag/v0.1.2) - 2024-03-03

<small>[Compare with v0.1.1](https://github.com/DataShades/ckanext-collection/compare/v0.1.1...v0.1.2)</small>

### Features

- register collections via `collection:register_collections` signal ([6db3be0](https://github.com/DataShades/ckanext-collection/commit/6db3be0121ee9f8a05c40b6ac71fb13a5e6334cf) by Sergey Motornyuk).
- Serializer has serialize method, stream and render moved to Streaming and Renderable serializers ([d749f36](https://github.com/DataShades/ckanext-collection/commit/d749f361cc40c0f431d94a383aeb24af8833fb52) by Sergey Motornyuk).
- add static_columns to table data ([9d5cd80](https://github.com/DataShades/ckanext-collection/commit/9d5cd80411c3b975561ba1186f2f8250ec5b7d65) by Sergey Motornyuk).
- add attrs to link and button filter options ([8a184fe](https://github.com/DataShades/ckanext-collection/commit/8a184fe8a3f6313f2924182794445bd77aa2c7ef) by Sergey Motornyuk).
- serializers has row_dictizer attribute ([883f3d7](https://github.com/DataShades/ckanext-collection/commit/883f3d73946008a6736a183686ac3f918800f1c4) by Sergey Motornyuk).
- register configuration in ckanext-amdin-panel ([8c8f5ca](https://github.com/DataShades/ckanext-collection/commit/8c8f5ca14853174c28a4c0e8f68bc9acaa816985) by Sergey Motornyuk).
- Collection and DB explorers MVP ([5b8b0bd](https://github.com/DataShades/ckanext-collection/commit/5b8b0bd2fda237d9c5aa139cf52937787d90f334) by Sergey Motornyuk).
- collection-refresh event on body or htmx form_id reloads collection ([9c8619d](https://github.com/DataShades/ckanext-collection/commit/9c8619d81827718d0cd01ccfe225fd6ccfabbd0d) by Sergey Motornyuk).
- TableFilters ([d7f1ff2](https://github.com/DataShades/ckanext-collection/commit/d7f1ff28d0913dea0a3ac88b6faf078800487770) by Sergey Motornyuk).
- DbCollection(TableData, TableColumns, DbConnection) ([48a1b24](https://github.com/DataShades/ckanext-collection/commit/48a1b24a17398eed64d0a6b487daf39e9221a877) by Sergey Motornyuk).
- register collection-explorer collection in debug mode ([42e547f](https://github.com/DataShades/ckanext-collection/commit/42e547fe953a0d5bc3922127c90668df98e1f94c) by Sergey Motornyuk).

### Bug Fixes

- naive filters cannot use IN operator ([a26b3b7](https://github.com/DataShades/ckanext-collection/commit/a26b3b7054758c0ff2559d781fe43d9378344193) by Sergey Motornyuk).
- naive search with q does not work with model ([aa46d0c](https://github.com/DataShades/ckanext-collection/commit/aa46d0c9f7066b14477c6a8d43be1fd52a4337f5) by Sergey Motornyuk).
- non-sortable columns are still sorted in model data ([353691d](https://github.com/DataShades/ckanext-collection/commit/353691df25e0b0ec64b3765cc59e506d04422c9c) by Sergey Motornyuk).
- HtmxTableSerializer reloads the page when page size changed ([feaa86c](https://github.com/DataShades/ckanext-collection/commit/feaa86c04ce38fec507ff53d2841eb6b708ebce2) by Sergey Motornyuk).

### Code Refactoring

- move pagination switcher into pagination template ([30dc9a9](https://github.com/DataShades/ckanext-collection/commit/30dc9a9f6457438f3b5090d408edd5bf51d744fe) by Sergey Motornyuk).
- remove generic type from collection ([8497e1e](https://github.com/DataShades/ckanext-collection/commit/8497e1e3ee8a6810806f1ed83f3b6baf64604235) by Sergey Motornyuk).
- use Iterable instead of Sequence for filters ([f047ed0](https://github.com/DataShades/ckanext-collection/commit/f047ed0ffcbe39d51a5300a32dc6017dd1fa09d5) by Sergey Motornyuk).

## [v0.1.1](https://github.com/DataShades/ckanext-collection/releases/tag/v0.1.1) - 2024-01-26

<small>[Compare with v0.1.0](https://github.com/DataShades/ckanext-collection/compare/v0.1.0...v0.1.1)</small>

### Bug Fixes

- fix ModelData statement_with_filters method ([3c6cb1c](https://github.com/DataShades/ckanext-collection/commit/3c6cb1cfad74ac653b8e2e9a1a223016381e9d99) by mutantsan).

## [v0.1.0](https://github.com/DataShades/ckanext-collection/releases/tag/v0.1.0) - 2024-01-25

<small>[Compare with v0.0.1](https://github.com/DataShades/ckanext-collection/compare/v0.0.1...v0.1.0)</small>

### Features

- init ckan modules for htmx responses ([5ab4972](https://github.com/DataShades/ckanext-collection/commit/5ab4972b105a75cfa2ce14b09d5fd4cdd3c838e2) by Sergey Motornyuk).
- filters in table searializer and naive filters/search for model data ([8175728](https://github.com/DataShades/ckanext-collection/commit/8175728f73c47b8357e1566b8bbd79a4690591e8) by Sergey Motornyuk).
- sorting order values controlled by columns ([41fec28](https://github.com/DataShades/ckanext-collection/commit/41fec2841cafba37e4ed3d65ca15ff1655f679ba) by Sergey Motornyuk).
- move serializer templates into dedicated forlders ([dadecde](https://github.com/DataShades/ckanext-collection/commit/dadecde5265080e2395a337f445b29c4fe5edda3) by Sergey Motornyuk).
- auto-serialize values insize dictize_row ([7ba26fe](https://github.com/DataShades/ckanext-collection/commit/7ba26feddaf64c1c07be8e6167c0ddda946b5957) by Sergey Motornyuk).
- add value_serializers to all serializers and ensure_dictized to html serializers ([e2cc754](https://github.com/DataShades/ckanext-collection/commit/e2cc754eecd29eb7ed861b65e45479f44fe21f40) by Sergey Motornyuk).
- raw collection export(without format) ([4db8397](https://github.com/DataShades/ckanext-collection/commit/4db839702a61383af8c7324159d43af215043f0b) by Sergey Motornyuk).
- export endpoint accepts filename argument ([7c237e4](https://github.com/DataShades/ckanext-collection/commit/7c237e47903ee353c76dc4010b5de15312ea3e00) by Sergey Motornyuk).
- Union and Statement ModelData ([16d2aa3](https://github.com/DataShades/ckanext-collection/commit/16d2aa3a245d879b7e8c34535d6e649a6c7cb4e8) by Sergey Motornyuk).
- Collection.replace_service ([a34518b](https://github.com/DataShades/ckanext-collection/commit/a34518b520743855f09f5eb32a4a0d4718356b11) by Sergey Motornyuk).
- add CLI ([9ea7e56](https://github.com/DataShades/ckanext-collection/commit/9ea7e5601062989a8752c16eb9eb0cff597191ed) by Sergey Motornyuk).
- export view ([3dd019d](https://github.com/DataShades/ckanext-collection/commit/3dd019d3469564ea119c900b1858ff7836586929) by Sergey Motornyuk).
- Domain.with_attributes ([31adfa1](https://github.com/DataShades/ckanext-collection/commit/31adfa1fbbd8ebb13354e24ed494627578e0d89d) by Sergey Motornyuk).
- add htmx table serializer ([fd99cd3](https://github.com/DataShades/ckanext-collection/commit/fd99cd3d61954372cc73a1198d4eec389ba68b49) by Sergey Motornyuk).
- table serializer use record/collection variables instead of row/table ([8189eb0](https://github.com/DataShades/ckanext-collection/commit/8189eb09707470735831cd62e45c5fada32575e6) by Sergey Motornyuk).
- Data has no limits ([0be661c](https://github.com/DataShades/ckanext-collection/commit/0be661c9c75216de7559441eea625c0af510fde5) by Sergey Motornyuk).
- split ApiData into ApiSearchData and ApiListData ([0315ae2](https://github.com/DataShades/ckanext-collection/commit/0315ae214111da68c367bba3261de0b8f5894e8b) by Sergey Motornyuk).
- ApiData.make_payload renamed to prepare_payload ([2a0bc61](https://github.com/DataShades/ckanext-collection/commit/2a0bc610f6757eef9e03c2d96f1e2a3d35e3b96c) by Sergey Motornyuk).
- `params` removed from Pager ([a96206f](https://github.com/DataShades/ckanext-collection/commit/a96206fd3cacc8aedff2b0a0da47688b82ccb5c1) by Sergey Motornyuk).
- table_id and form_id properties removed from chartjs and table serializers ([f919c8f](https://github.com/DataShades/ckanext-collection/commit/f919c8f6e65e631a2879dc3c5c5886f81fdade9a) by Sergey Motornyuk).
- `_collection` attribute replaced by `attached` property ([ad1a10f](https://github.com/DataShades/ckanext-collection/commit/ad1a10fc2c122645a87f7a58f1ac9052596e6f11) by Sergey Motornyuk).
- Filters now have only actions and filters attributes ([3f2ec4c](https://github.com/DataShades/ckanext-collection/commit/3f2ec4c61673081a36b6e2dd2a64ae09b34dfaa1) by Sergey Motornyuk).
- add model data support to all serializers ([daaf4bc](https://github.com/DataShades/ckanext-collection/commit/daaf4bcdc0b7db04641603c8587237dad13adbdf) by Sergey Motornyuk).
- add model data support to CsvSerializer ([b774684](https://github.com/DataShades/ckanext-collection/commit/b774684b012862f1c2fadb3dde139f5e2fe521b9) by Sergey Motornyuk).

### Bug Fixes

- fix sorting for table serializer ([b4cd2cb](https://github.com/DataShades/ckanext-collection/commit/b4cd2cbf50dde4ac364b86c4ee62c1fef86699ec) by Sergey Motornyuk).
- invariant base collection causes typing error ([6ebb0a1](https://github.com/DataShades/ckanext-collection/commit/6ebb0a1e3b445c83dbdc86f6a7a594074e1333e3) by Sergey Motornyuk).

## [v0.0.1](https://github.com/DataShades/ckanext-collection/releases/tag/v0.0.1) - 2023-10-23

<small>[Compare with first commit](https://github.com/DataShades/ckanext-collection/compare/3bb615ac5019219f8072e2f915797f1bd9917b1a...v0.0.1)</small>
