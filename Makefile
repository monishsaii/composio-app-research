PY ?= python
APP ?= Notion

.PHONY: install test research-one research-all verify analyze accuracy build-site all

install:
	$(PY) -m pip install -e ".[dev,browser]"

test:
	$(PY) -m pytest -q

research-one:
	$(PY) -m appresearch research --app "$(APP)" --stage pass1

research-all:
	$(PY) -m appresearch research --all --stage pass1

verify:
	$(PY) -m appresearch verify --all

analyze:
	$(PY) -m appresearch analyze

accuracy:
	$(PY) -m appresearch accuracy

build-site:
	$(PY) -m appresearch build-site

all: verify accuracy analyze build-site
