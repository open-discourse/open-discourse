VENV_NAME?=.venv

USER_PYTHON ?= python3
VENV_PYTHON=${VENV_NAME}/bin/python

.PHONY = prepare-venv install install-dev test lint format clean

.DEFAULT_GOAL = install-dev

prepare-venv: $(VENV_NAME)/bin/python

$(VENV_NAME)/bin/python:
	make clean && ${USER_PYTHON} -m venv $(VENV_NAME)

install: prepare-venv
	${VENV_PYTHON} -m pip install -U pip
	${VENV_PYTHON} -m pip install -e .

install-dev: prepare-venv
	${VENV_PYTHON} -m pip install -U pip
	${VENV_PYTHON} -m pip install -e .\[dev\]

lint: install-dev
	${VENV_PYTHON} -m ruff check
	${VENV_PYTHON} -m ruff check --select I

format: install-dev
	${VENV_PYTHON} -m ruff check --select I --fix
	${VENV_PYTHON} -m ruff format

database:
	docker-compose up -d database
	sleep 20
	cd ../database; yarn run db:update:local

data/01_raw/xml: install
	${VENV_PYTHON} open_discourse/01_preprocessing/01_download_raw_data.py

clean:
	rm -rf $(VENV_NAME)
	rm -rf .ruff_cache
	rm -rf open_discourse.egg-info
	rm -rf dist
	find . -name __pycache__ -type d -exec rm -r {} +

clean-data:
	rm -rf data
