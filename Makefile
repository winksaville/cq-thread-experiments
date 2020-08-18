
.PHONY: all, format

app=thread1.py

all:
	echo make f | p | c

p:
	python ${app}

c:
	cq-editor ${app}

f:
	isort *.py
	black *.py
	flake8 *.py
