
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

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: p
p: ## Run xxx with python using "make p app=xxx"
	@if [ "${app}" == "" ]; then echo "Expecting 'app=xxx'"; exit 1; fi
	python ${app}

.PHONY: e
e: ## Run xxx with cq-editor using "make e app=xxx"
	@if [ "${app}" == "" ]; then echo "Expecting 'app=xxx'"; exit 1; fi
	cq-editor ${app}

.PHONY: f, format
f: format ## Format with isort, black and flake8
format: ## Format with isort, black and flake8
	isort *.py cq-bolt cq-nut
	black *.py cq-bolt cq-nut
	flake8 *.py cq-bolt cq-nut

.PHONY: mypy
mypy: ## Run mypy over files
	mypy *.py
	mypy cq-bolt
	mypy cq-nut

.PHONY: t, test
t: test ## Test using pytest
test: ## Test using pytest
	pytest

.PHONY: clean
clean: ## Clean files
	rm -rf __pycache__ .pytest_cache .mypy_cache
