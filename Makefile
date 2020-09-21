
.PHONY: all, format, f, e, c, p, t

all:
	@echo "make <target>"
	@echo "targets:"
	@echo " f|format   # Format"
	@echo " e app=xxx  # Run with cq-editor with xxx as application"
	@echo " p app=xxx  # Run with python with xxx as application"
	@echo " t          # Run pytest"
	@echo " mypy       # Run mypy *.py"

p:
	@if [ "${app}" == "" ]; then echo "Expecting 'app=xxx'"; exit 1; fi
	python ${app}

e: c
c:
	@if [ "${app}" == "" ]; then echo "Expecting 'app=xxx'"; exit 1; fi
	cq-editor ${app}

format: f
f:
	isort *.py
	black *.py
	flake8 *.py

mypy:
	mypy *.py

t:
	pytest
