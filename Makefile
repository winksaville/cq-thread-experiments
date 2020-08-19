
.PHONY: all, format

app=thread1.py

all:
	@echo "make <target>"
	@echo "targets:"
	@echo "f   # Format"
	@echo "e   # Run with cq-editor"
	@echo "p   # Run with python"

p:
	python ${app}

c:
	cq-editor ${app}

f:
	isort *.py
	black *.py
	flake8 *.py
