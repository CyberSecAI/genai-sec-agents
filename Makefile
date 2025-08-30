# GenAI Security Agents Makefile
# Helper commands for development and validation

.PHONY: help install validate test clean build

help:		## Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:	## Install Python dependencies
	pip install -r requirements.txt

validate:	## Validate all Rule Cards
	python app/tools/validate_cards.py app/rule_cards/

test:		## Run all tests
	pytest tests/ -v

clean:		## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf app/dist/agents/*.json

build:		## Build agent packages (placeholder)
	@echo "Agent compilation not yet implemented"

lint:		## Run code linting
	@echo "Linting not yet configured"