FILES=*.py

.PHONY: all
all: test flake8 pylint mypy black

.PHONY: test
test:
	@python3 -m unittest tests/*.py

.PHONY: flake8
flake8:
	@flake8 --ignore=E501 $(FILES)

.PHONY: pylint
pylint:
	@pylint $(FILES)

.PHONY: mypy
mypy:
	@mypy $(FILES)

.PHONY: black
black:
	@black --check $(FILES)
