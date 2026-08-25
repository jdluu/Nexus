# Nexus Makefile
# Unified interface for development, testing, and release tasks.

.PHONY: help test lint typecheck check build publish-release

INFISICAL_PROJECT_ID ?= b5af8dff-e2cd-492a-bf10-a71ce71deb58
INFISICAL_ENV ?= prod
INFISICAL_PATH ?= /Nexus
INFISICAL_TOKEN_HELPER ?= $(HOME)/projects/infisical-token.sh

help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

test: ## Run the test suite with coverage
	uv run pytest --cov=nexus --cov-report=term-missing

lint: ## Lint with ruff
	uv run ruff check .

typecheck: ## Type-check with mypy
	uv run mypy .

check: lint typecheck test ## Run all CI checks locally

build: ## Build distributions
	uv build

publish-release: ## Publish to PyPI using PYPI_TOKEN from Infisical (prod)
	@test -n "$$INFISICAL_TOKEN" || INFISICAL_TOKEN=$$(bash $(INFISICAL_TOKEN_HELPER)); \
	env INFISICAL_TOKEN="$$INFISICAL_TOKEN" infisical secrets get PYPI_TOKEN \
		--projectId $(INFISICAL_PROJECT_ID) --env $(INFISICAL_ENV) --path $(INFISICAL_PATH) --token "$$INFISICAL_TOKEN" --plain > /tmp/pypi_token; \
	uv publish --token "$$(cat /tmp/pypi_token)"; rm -f /tmp/pypi_token
