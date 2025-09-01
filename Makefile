# GenAI Security Agents Makefile
# Helper commands for development and validation

.PHONY: help install validate test clean build semsearch-build semsearch

help:		## Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:	## Install Python dependencies
	pip install -r requirements.txt

validate:	## Validate all Rule Cards
	python3 app/tools/validate_cards.py app/rule_cards/

test:		## Run all tests
	python3 tests/test_compiler_simple.py
	python3 app/tools/validate_cards.py app/rule_cards/

clean:		## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf app/dist/agents/*.json

compile:	## Compile Rule Cards into agent packages
	python3 app/tools/compile_agents.py --verbose

build: validate compile	## Validate Rule Cards and compile agent packages

lint:		## Run code linting
	@echo "Linting not yet configured"

semsearch-build:	## Build semantic search corpus from OWASP cheatsheets
	python3 tools/render_owasp_for_search.py --verbose --validate

semsearch:	## Perform semantic search on OWASP corpus (usage: make semsearch q="query")
	@if [ -z "$(q)" ]; then \
		echo "Usage: make semsearch q=\"your search query\""; \
		echo "Examples:"; \
		echo "  make semsearch q=\"jwt token validation\""; \
		echo "  make semsearch q=\"docker container security\""; \
		echo "  make semsearch q=\"session fixation prevention\""; \
	else \
		tools/semsearch.sh "$(q)"; \
	fi