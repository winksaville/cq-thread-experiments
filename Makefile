
.PHONY: all, format, f, e, c, p

app=thread4.py

all:
	@echo "make <target>"
	@echo "targets:"
	@echo "f   # Format"
	@echo "e   # Run with cq-editor"
	@echo "p   # Run with python"

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
