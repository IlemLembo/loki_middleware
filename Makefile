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

# .PHONY: set-version reset-tag help

# Usage: make set-version VERSION=0.1.0
set-version:
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Erreur : Veuillez spécifier une version. Exemple : make set-version VERSION=0.1.0"; \
		exit 1; \
	fi
	@echo "🔧 Mise à jour des fichiers de configuration vers v$(VERSION)..."
	@# Mise à jour dans pyproject.toml
	@if [ -f pyproject.toml ]; then \
		sed -i -E 's/^version = ".*"/version = "$(VERSION)"/' pyproject.toml; \
		echo "  ✅ pyproject.toml mis à jour"; \
	fi
	@# Mise à jour dans cz.toml s'il existe
	@if [ -f cz.toml ]; then \
		sed -i -E 's/^version = ".*"/version = "$(VERSION)"/' cz.toml; \
		echo "  ✅ cz.toml mis à jour"; \
	fi
# ==========================================
# Commandes de Versionning & Tags
# ==========================================
# Usage: make set-version VERSION=0.1.8
set-version:
	@python -c "import sys, re; \
	v = '$(VERSION)'; \
	sys.exit('❌ Spécifiez VERSION=x.y.z') if not v else None; \
	[open(f, 'w').write(re.sub(r'^version\s*=\s*\".*\"', f'version = \"{v}\"', open(f).read(), flags=re.M)) for f in ['pyproject.toml', 'cz.toml'] if __import__('os').path.exists(f)]; \
	print(f'✅ Version mise à jour vers {v} dans les fichiers de configuration.')"

# Usage: make reset-tag OLD_TAG=v0.2.0 NEW_VERSION=0.1.8
reset-tag:
	@echo "🔥 Suppression du tag local et distant..."
	-git tag -d $(OLD_TAG)
	-git push origin :refs/tags/$(OLD_TAG)
	@echo "✏️ Mise à jour des fichiers..."
	@$(MAKE) set-version VERSION=$(NEW_VERSION)
	@echo "📦 Commit et création du tag v$(NEW_VERSION)..."
	git add pyproject.toml
	python -c "import os; os.system('git add cz.toml') if os.path.exists('cz.toml') else None"
	git commit -m "chore(release): reset version to $(NEW_VERSION)"
	git tag -a v$(NEW_VERSION) -m "v$(NEW_VERSION)"
	git push origin main --tags
	@echo "🚀 Tag v$(NEW_VERSION) forcé et synchronisé !"