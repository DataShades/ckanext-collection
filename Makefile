.DEFAULT_GOAL := help
.PHONY = help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


changelog:  ## compile changelog
	git changelog -c conventional -o CHANGELOG.md $(if $(bump),-B $(bump))

vendor:
	cp node_modules/htmx.org/dist/htmx.js ckanext/collection/assets/vendor

deploy-docs:  ## build and publish documentation
	mkdocs gh-deploy
