.PHONY: install dev-install test lint format clean build publish commit bump changelog version

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-coverage:
	pytest --cov --cov-report=html --cov-report=term

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

build: clean
	python -m build

publish: build
	python -m twine upload dist/*

publish-test: build
	python -m twine upload --repository testpypi dist/*

# --- Versioning & Changelog ---

commit:
	cz commit

bump:
	cz bump

bump-dry:
	cz bump --dry-run

changelog:
	cz changelog

version:
	cz version

release: bump
	git push && git push --tags
	@echo "Version bumped, changelog updated, and tag pushed."
	@echo "GitHub Actions will publish to PyPI and create the GitHub release."