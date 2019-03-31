.PHONY: venv
venv:
	@virtualenv -p python3.7 venv
	@venv/bin/pip install -e .[dev]

.PHONY: test
test:
	@pytest --cov-report term-missing --cov sqlitemap
	@flake8 sqlitemap tests
	@isort -rc -c --diff sqlitemap tests
	@mypy sqlitemap
