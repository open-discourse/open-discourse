# see https://blog.mathieu-leplatre.info/tips-for-your-makefile-with-python.html
NAME := open_discourse
VENV := $(shell echo $${VIRTUAL_ENV-.venv})
UV := $(shell command -v uv 2> /dev/null)
PYTHON := $(VENV)/bin/python
INSTALL_STAMP := $(VENV)/.install.stamp
INSTALL_DEV_STAMP := $(VENV)/.install.dev.stamp

.DEFAULT_GOAL = install-dev

$(PYTHON):
	@if [ -z $(UV) ]; then echo "uv could not be found."; exit 2; fi
	$(UV) venv $(VENV)

.PHONY: install
install: $(INSTALL_STAMP)

$(INSTALL_STAMP): $(PYTHON) pyproject.toml
	$(UV) sync --no-dev
	touch $(INSTALL_STAMP)

.PHONY: install-dev
install-dev: $(INSTALL_DEV_STAMP)

$(INSTALL_DEV_STAMP): $(PYTHON) pyproject.toml
	$(UV) sync
	touch $(INSTALL_DEV_STAMP)

.PHONY: lint
lint: $(INSTALL_DEV_STAMP)
	$(UV) run ruff check
	$(UV) run ruff check --select I

.PHONY: format
format: $(INSTALL_DEV_STAMP)
	$(UV) run ruff check --select I --fix
	$(UV) run ruff format

.PHONY: database
database:
	docker-compose up -d database
	sleep 20
	cd ../database; yarn run db:update:local

.PHONY: clean
clean:
	rm -rf $(VENV_NAME)
	rm -rf .ruff_cache
	rm -rf open_discourse.egg-info
	rm -rf dist
	find . -name __pycache__ -type d -exec rm -r {} +

.PHONY: clean-data
clean-data:
	rm -rf data

.PHONY: list-tasks
list-tasks:
	$(UV) run doit list --all --deps

.PHONY: test
test:
	$(UV) run pytest -vv tests
