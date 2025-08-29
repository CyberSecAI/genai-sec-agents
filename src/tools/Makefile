# Makefile for the GenAI Security Agents project.
# Provides commands to validate rule cards and compile agent packages.

.PHONY: validate compile clean

VENV=.venv
PY=$(VENV)/bin/python

# Sets up the Python virtual environment and installs dependencies.
$(VENV)/bin/activate:
	python -m venv $(VENV)
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r requirements.txt

# Validates the schema and integrity of all Rule Card YAML files.
validate: $(VENV)/bin/activate
	$(PY) tools/validate_cards.py

# Compiles the validated Rule Cards into JSON packages for each agent.
compile: validate
	$(PY) tools/compile_agents.py --manifest tools/agents_manifest.yml --out dist/agents

# Removes compiled agent packages.
clean:
	rm -rf dist/agents
