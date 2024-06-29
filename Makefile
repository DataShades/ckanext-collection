.DEFAULT_GOAL := help
.PHONY = help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


# Type	Section
# build	Build
# chore	Chore
# ci	Continuous Integration
# deps	Dependencies
# doc(s)	Docs
# feat	Features
# fix	Bug Fixes
# perf	Performance Improvements
# ref(actor)	Code Refactoring
# revert	Reverts
# style	Style
# test(s)	Tests
changelog:  ## compile changelog
	git changelog

vendor:
	cp node_modules/htmx.org/dist/htmx.js ckanext/collection/assets/vendor

deploy-docs:  ## build and publish documentation
	mkdocs gh-deploy
