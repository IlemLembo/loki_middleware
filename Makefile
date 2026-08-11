.PHONY: help install lint format typecheck test test-cov check build clean bump release

.DEFAULT_GOAL := help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install environment and development dependencies
	uv sync --dev

lint: ## Run linter and check code formatting
	uv run ruff check .
	uv run ruff format --check .

format: ## Fix lint issues and format code automatically
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Run mypy static type checking
	uv run mypy src/loki_middleware

test: ## Run pytest test suite
	uv run pytest

test-cov: ## Run test suite with coverage report
	uv run pytest --cov=src/loki_middleware --cov-report=term-missing

check: lint typecheck test ## Run all CI checks (lint, typecheck, tests)

build: ## Build wheel and source package using uv
	uv build

clean: ## Remove build artifacts and cache folders
	uv clean
	python -c "import shutil, glob, os; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('dist') + glob.glob('*.egg-info') + glob.glob('.pytest_cache') + glob.glob('.ruff_cache') + glob.glob('.mypy_cache') + glob.glob('.coverage') + glob.glob('htmlcov')]"

bump: check ## Run all CI checks, auto-increment version and update changelog
	uv run cz bump

release: bump ## Run bump and push commits and tags to trigger PyPI release via GitHub Actions
	git push origin main --tags