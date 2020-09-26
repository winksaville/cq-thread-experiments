.PHONY: help, f, e, p, mypy, t, clean

define PRINT_HELP_PYSCRIPT
import re, sys

print("<targets>:")
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

p: ## Run xxx with python using "make p app=xxx"
	@if [ "${app}" == "" ]; then echo "Expecting 'app=xxx'"; exit 1; fi
	python ${app}

e: ## Run xxx with cq-editor using "make e app=xxx"
	@if [ "${app}" == "" ]; then echo "Expecting 'app=xxx'"; exit 1; fi
	cq-editor ${app}

f: ## Format with isort, black and flake8
	isort *.py cq-bolt cq-nut
	black *.py cq-bolt cq-nut
	flake8 *.py cq-bolt cq-nut

mypy: ## Run mypy over files
	mypy *.py
	mypy cq-bolt
	mypy cq-nut

t: ## Test using pytest
	pytest

clean: ## Clean files
	rm -rf __pycache__ .pytest_cache .mypy_cache
