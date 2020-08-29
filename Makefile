
.PHONY: all, format, f, e, c, p, t

app=thread5.py

all:
	@echo "make <target>"
	@echo "targets:"
	@echo " f|format   # Format"
	@echo " e|c        # Run with cq-editor"
	@echo " p          # Run with python"
	@echo " t          # Run pytest"

p:
	python ${app}

e: c
c:
	cq-editor ${app}

format: f
f:
	isort *.py
	black *.py
	flake8 *.py

t:
	pytest
