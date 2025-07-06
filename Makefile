# ============================================================================
# Ultimate Makefile for Python Projects with uv
# ============================================================================
# A production-ready Makefile leveraging uv's speed and modern Python tooling
# Features:
# - Automatic dependency tracking and virtual environment rebuilding
# - Separation of production and development dependencies
# - Integration with ruff, mypy, pylint, pytest, and pre-commit
# - Unix-only compatibility (no Windows support)
# - Efficient caching and parallel execution
# - CI/CD optimized targets
# ============================================================================

# Configuration
# ============================================================================
SHELL := /bin/bash
.DEFAULT_GOAL := help
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.SUFFIXES:

# Variables
# ============================================================================
PROJECT_NAME := $(shell grep '^name' pyproject.toml | head -1 | cut -d'"' -f2)
PYTHON_VERSION := $(shell cat .python-version 2>/dev/null || echo "3.11")
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Unix-only configuration
VENV_BIN := .venv/bin
PYTHON := $(VENV_BIN)/python
UV := uv
SEP := :

# Dependency files
VENV_MARKER := .venv/pyvenv.cfg
UV_LOCK := uv.lock
PYPROJECT := pyproject.toml
PYTHON_VERSION_FILE := .python-version
PRE_COMMIT_CONFIG := .pre-commit-config.yaml

# Cache directories
CACHE_DIR := .cache
UV_CACHE := $(CACHE_DIR)/uv
BUILD_CACHE := $(CACHE_DIR)/build
COVERAGE_CACHE := $(CACHE_DIR)/coverage

# Parallel execution
MAKEFLAGS += --jobs=$(shell nproc 2>/dev/null || echo 4)

# Colors for output
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

# Help Documentation
# ============================================================================
.PHONY: help
help: ## Show this help message
	@echo -e "$(BOLD)$(BLUE)Ultimate Python Project Makefile$(RESET)"
	@echo -e "$(BOLD)================================$(RESET)"
	@echo -e ""
	@echo -e "$(BOLD)Usage:$(RESET)"
	@echo -e "  make $(GREEN)<target>$(RESET)"
	@echo -e ""
	@echo -e "$(BOLD)Main Targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BOLD)$(YELLOW)%s$(RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

# Environment Management
# ============================================================================

##@ Environment Management

.PHONY: uv
uv: ## Install uv if not present
	@which uv > /dev/null 2>&1 || (echo "Installing uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)

.PHONY: install
install: uv $(UV_LOCK) ## Install production dependencies
	@echo -e "$(BOLD)Installing production dependencies...$(RESET)"
	$(UV) sync --frozen --no-group dev

.PHONY: install-dev
install-dev: uv $(UV_LOCK) ## Install all dependencies including dev
	@echo -e "$(BOLD)Installing all dependencies...$(RESET)"
	$(UV) sync --frozen --all-extras

.PHONY: install-all
install-all: uv $(UV_LOCK) ## Install all optional dependency groups
	@echo -e "$(BOLD)Installing all dependency groups...$(RESET)"
	$(UV) sync --frozen --all-groups

# Advanced dependency tracking
$(UV_LOCK): uv $(PYPROJECT) $(PYTHON_VERSION_FILE) | $(VENV_MARKER)
	@echo -e "$(BOLD)Updating lockfile...$(RESET)"
	$(UV) lock
	@touch $@

$(VENV_MARKER): uv $(PYTHON_VERSION_FILE)
	@echo -e "$(BOLD)Creating virtual environment with Python $(PYTHON_VERSION)...$(RESET)"
	$(UV) venv --python $(PYTHON_VERSION)
	@touch $@

$(PYTHON_VERSION_FILE):
	@echo -e "$(BOLD)Creating Python version file...$(RESET)"
	@echo "$(PYTHON_VERSION)" > $@

.PHONY: update
update: uv ## Update all dependencies to latest versions
	@echo -e "$(BOLD)Updating dependencies...$(RESET)"
	$(UV) lock --upgrade
	$(UV) sync

.PHONY: update-deps
update-deps: uv ## Interactive dependency update
	@echo -e "$(BOLD)Checking outdated dependencies...$(RESET)"
	$(UV) pip list --outdated
	@echo -e "\n$(YELLOW)Update specific package: make update-package PACKAGE=name$(RESET)"

.PHONY: update-package
update-package: uv ## Update specific package (use with PACKAGE=name)
	@if [ -z "$(PACKAGE)" ]; then \
		echo -e "$(RED)Error: PACKAGE variable required$(RESET)"; \
		echo -e "Usage: make update-package PACKAGE=requests"; \
		exit 1; \
	fi
	$(UV) lock --upgrade-package $(PACKAGE)
	$(UV) sync

# Development Commands
# ============================================================================

##@ Development

.PHONY: dev
dev: install-dev ## Set up development environment
	@echo -e "$(GREEN)✓ Development environment ready!$(RESET)"
	@echo -e "Run '$(BLUE)make run$(RESET)' to start the application"

.PHONY: run
run: uv ## Run the Streamlit application
	$(UV) run streamlit run app.py

.PHONY: init-data
init-data: uv ## Initialize local database with NFL teams and sample data
	$(UV) run python scripts/init_data.py

# Supabase Development
# ============================================================================

##@ Supabase Development

.PHONY: supabase-start
supabase-start: ## Start local Supabase stack
	@echo -e "$(BOLD)Starting local Supabase stack...$(RESET)"
	supabase start

.PHONY: supabase-stop
supabase-stop: ## Stop local Supabase stack
	@echo -e "$(BOLD)Stopping local Supabase stack...$(RESET)"
	supabase stop

.PHONY: supabase-status
supabase-status: ## Show Supabase stack status
	supabase status

.PHONY: supabase-reset
supabase-reset: ## Reset local Supabase database
	@echo -e "$(BOLD)Resetting local Supabase database...$(RESET)"
	supabase db reset

.PHONY: supabase-studio
supabase-studio: ## Open Supabase Studio (web interface)
	@echo -e "$(GREEN)Opening Supabase Studio at http://localhost:54323$(RESET)"
	@if command -v open &> /dev/null; then \
		open http://localhost:54323; \
	elif command -v xdg-open &> /dev/null; then \
		xdg-open http://localhost:54323; \
	else \
		echo -e "$(YELLOW)Please open http://localhost:54323 manually$(RESET)"; \
	fi

.PHONY: run-supabase
run-supabase: use-local supabase-start init-data-supabase ## Complete local setup: switch env, start Supabase, init data, run app
	@echo -e "$(BOLD)Starting app with local Supabase...$(RESET)"
	$(UV) run streamlit run app.py

.PHONY: local
local: run-supabase ## Alias for run-supabase (shorter to type)

.PHONY: use-local
use-local: ## Switch to local Supabase environment
	@echo -e "$(BOLD)Switching to local Supabase...$(RESET)"
	@cp .env.local .env
	@echo -e "$(GREEN)✓ Using local Supabase at http://127.0.0.1:54321$(RESET)"

.PHONY: use-production
use-production: ## Switch to production Supabase environment
	@echo -e "$(BOLD)$(RED)Switching to production Supabase...$(RESET)"
	@cp .env.production .env
	@echo -e "$(YELLOW)⚠️  Using production database!$(RESET)"

.PHONY: init-data-supabase
init-data-supabase: uv use-local ## Initialize Supabase database with NFL teams and sample data
	@echo -e "$(BOLD)Resetting Supabase database and applying migrations...$(RESET)"
	supabase db reset
	$(UV) run python scripts/init_data.py

.PHONY: run-local
run-local: uv ## Run the app locally with all setup (init + run)
	@if [ ! -d "data/db" ] || [ -z "$$(ls -A data/db 2>/dev/null)" ]; then \
		echo -e "$(BOLD)Initializing database...$(RESET)"; \
		$(MAKE) init-data; \
	fi
	@echo -e "$(BOLD)Starting Streamlit app...$(RESET)"
	$(UV) run streamlit run app.py

.PHONY: shell
shell: uv $(UV_LOCK) ## Open Python REPL with project context
	$(UV) run python

.PHONY: script
script: uv $(UV_LOCK) ## Run a Python script (use with SCRIPT=path/to/script.py)
	@if [ -z "$(SCRIPT)" ]; then \
		echo -e "$(RED)Error: SCRIPT variable required$(RESET)"; \
		exit 1; \
	fi
	$(UV) run python $(SCRIPT)

# Code Quality
# ============================================================================

##@ Code Quality

.PHONY: format
format: uv $(UV_LOCK) ## Format code with ruff
	@echo -e "$(BOLD)Formatting code...$(RESET)"
	$(UV) run ruff format $(SRC_DIR) $(TEST_DIR)
	$(UV) run ruff check --fix $(SRC_DIR) $(TEST_DIR)

.PHONY: lint
lint: uv $(UV_LOCK) ## Run all linting checks
	@echo -e "$(BOLD)Running linting checks...$(RESET)"
	@$(MAKE) --no-print-directory ruff
	@$(MAKE) --no-print-directory mypy
	@$(MAKE) --no-print-directory pylint

.PHONY: ruff
ruff: uv $(UV_LOCK) ## Run ruff linter
	@echo -e "$(BOLD)Running ruff...$(RESET)"
	$(UV) run ruff check $(SRC_DIR) $(TEST_DIR)

.PHONY: ruff-fix
ruff-fix: uv $(UV_LOCK) ## Run ruff with auto-fix
	$(UV) run ruff check --fix $(SRC_DIR) $(TEST_DIR)

.PHONY: mypy
mypy: uv $(UV_LOCK) ## Run mypy type checker
	@echo -e "$(BOLD)Running mypy...$(RESET)"
	$(UV) run mypy $(SRC_DIR)

.PHONY: type-check
type-check: mypy ## Alias for mypy (for CI compatibility)

.PHONY: pylint
pylint: uv $(UV_LOCK) ## Run pylint
	@echo -e "$(BOLD)Running pylint...$(RESET)"
	$(UV) run pylint $(SRC_DIR)

.PHONY: format-check
format-check: uv $(UV_LOCK) ## Check code formatting without changes
	@echo -e "$(BOLD)Checking code format...$(RESET)"
	$(UV) run ruff format --check $(SRC_DIR) $(TEST_DIR)
	$(UV) run ruff check $(SRC_DIR) $(TEST_DIR)

# Testing
# ============================================================================

##@ Testing

.PHONY: test
test: uv $(UV_LOCK) ## Run tests with coverage
	@echo -e "$(BOLD)Running tests...$(RESET)"
	$(UV) run pytest

.PHONY: test-fast
test-fast: uv $(UV_LOCK) ## Run tests without coverage
	$(UV) run pytest -x --no-cov

.PHONY: test-watch
test-watch: uv $(UV_LOCK) ## Run tests in watch mode
	$(UV) run pytest-watch -- -x

.PHONY: test-parallel
test-parallel: uv $(UV_LOCK) ## Run tests in parallel
	$(UV) run pytest -n auto

.PHONY: test-failed
test-failed: uv $(UV_LOCK) ## Re-run failed tests
	$(UV) run pytest --lf -x

.PHONY: test-verbose
test-verbose: uv $(UV_LOCK) ## Run tests with verbose output
	$(UV) run pytest -vv

.PHONY: coverage
coverage: uv $(UV_LOCK) ## Generate coverage report
	@echo -e "$(BOLD)Generating coverage report...$(RESET)"
	$(UV) run pytest --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo -e "$(GREEN)Coverage report: htmlcov/index.html$(RESET)"

.PHONY: coverage-open
coverage-open: coverage ## Generate and open coverage report
	@if command -v xdg-open &> /dev/null; then \
		xdg-open htmlcov/index.html; \
	elif command -v open &> /dev/null; then \
		open htmlcov/index.html; \
	else \
		echo -e "$(YELLOW)Please open htmlcov/index.html manually$(RESET)"; \
	fi

# Pre-commit
# ============================================================================

##@ Git Hooks

.PHONY: pre-commit-install
pre-commit-install: uv $(UV_LOCK) ## Install pre-commit hooks
	@echo -e "$(BOLD)Installing pre-commit hooks...$(RESET)"
	$(UV) run pre-commit install
	$(UV) run pre-commit install --hook-type commit-msg

.PHONY: pre-commit
pre-commit: uv $(UV_LOCK) ## Run pre-commit on all files
	@echo -e "$(BOLD)Running pre-commit...$(RESET)"
	$(UV) run pre-commit run --all-files

.PHONY: pre-commit-update
pre-commit-update: uv $(UV_LOCK) ## Update pre-commit hooks
	$(UV) run pre-commit autoupdate

# Documentation
# ============================================================================

##@ Documentation

.PHONY: docs
docs: uv $(UV_LOCK) ## Build documentation
	@echo -e "$(BOLD)Building documentation...$(RESET)"
	$(UV) run --group docs sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html

.PHONY: docs-serve
docs-serve: docs ## Build and serve documentation
	@echo -e "$(GREEN)Serving docs at http://localhost:8000$(RESET)"
	cd $(DOCS_DIR)/_build/html && python -m http.server 8000

.PHONY: docs-clean
docs-clean: ## Clean documentation build
	rm -rf $(DOCS_DIR)/_build

# Build & Distribution
# ============================================================================

##@ Build & Distribution

.PHONY: requirements
requirements: uv $(UV_LOCK) ## Export requirements.txt for deployment
	@echo -e "$(BOLD)Exporting requirements.txt...$(RESET)"
	$(UV) export --no-dev --format requirements-txt > requirements-temp.txt
	@echo -e "$(BOLD)Cleaning requirements.txt (removing hashes for Streamlit)...$(RESET)"
	@grep -v "hash=" requirements-temp.txt | grep -v "^[[:space:]]*--hash" | sed '/^[[:space:]]*$$/d' | sed 's/ \\$$//' > requirements.txt
	@rm requirements-temp.txt
	@echo -e "$(GREEN)✓ requirements.txt created for Streamlit deployment$(RESET)"

.PHONY: build
build: uv clean $(UV_LOCK) ## Build distribution packages
	@echo -e "$(BOLD)Building distribution packages...$(RESET)"
	$(UV) build

.PHONY: build-check
build-check: uv build ## Build and check package
	$(UV) run twine check dist/*

.PHONY: publish-test
publish-test: uv build-check ## Publish to TestPyPI
	@echo -e "$(BOLD)Publishing to TestPyPI...$(RESET)"
	$(UV) publish --publish-url https://test.pypi.org/legacy/

.PHONY: publish
publish: uv build-check ## Publish to PyPI
	@echo -e "$(BOLD)$(RED)Publishing to PyPI...$(RESET)"
	@echo -e "$(YELLOW)This will publish to the real PyPI. Continue? [y/N]$(RESET)"
	@read -r response && [ "$$response" = "y" ] || exit 1
	$(UV) publish

# Project Initialization
# ============================================================================

##@ Project Setup

.PHONY: init
init: ## Initialize new project with best practices
	@echo -e "$(BOLD)Initializing project structure...$(RESET)"
	@mkdir -p $(SRC_DIR)/$(PROJECT_NAME) $(TEST_DIR) $(DOCS_DIR) scripts
	@touch $(SRC_DIR)/$(PROJECT_NAME)/__init__.py
	@touch $(SRC_DIR)/$(PROJECT_NAME)/py.typed
	@echo -e "$(GREEN)✓ Project structure created$(RESET)"
	@$(MAKE) --no-print-directory dev
	@$(MAKE) --no-print-directory pre-commit-install
	@echo -e "$(GREEN)✓ Project initialized successfully!$(RESET)"

# CI/CD Targets
# ============================================================================

##@ CI/CD

.PHONY: ci-install
ci-install: uv ## Install dependencies for CI
	@echo -e "$(BOLD)Installing CI dependencies...$(RESET)"
	$(UV) sync --frozen --all-extras --no-cache

.PHONY: ci-test
ci-test: uv ## Run tests for CI
	$(UV) run pytest --cov=$(SRC_DIR) --cov-report=xml --cov-report=term

.PHONY: ci-lint
ci-lint: uv ## Run linting for CI
	$(UV) run ruff check --output-format=github $(SRC_DIR) $(TEST_DIR)
	$(UV) run ruff format --check $(SRC_DIR) $(TEST_DIR)
	$(UV) run mypy $(SRC_DIR) --no-error-summary

.PHONY: ci
ci: ci-install ci-lint ci-test ## Run complete CI pipeline

# Maintenance
# ============================================================================

##@ Maintenance

.PHONY: clean
clean: ## Clean build artifacts and cache
	@echo -e "$(BOLD)Cleaning build artifacts...$(RESET)"
	rm -rf build dist *.egg-info
	rm -rf .coverage htmlcov .pytest_cache .mypy_cache .ruff_cache
	rm -rf $(CACHE_DIR)
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.orig" -delete

.PHONY: clean-all
clean-all: clean ## Clean everything including virtual environment
	@echo -e "$(BOLD)$(RED)Removing virtual environment...$(RESET)"
	rm -rf .venv
	rm -f $(UV_LOCK)

.PHONY: info
info: uv ## Show project information
	@echo -e "$(BOLD)Project Information$(RESET)"
	@echo -e "$(BOLD)==================$(RESET)"
	@echo -e "Project: $(GREEN)$(PROJECT_NAME)$(RESET)"
	@echo -e "Python:  $(GREEN)$(PYTHON_VERSION)$(RESET)"
	@echo -e "uv:      $(GREEN)$(shell $(UV) --version 2>/dev/null || echo "not installed")$(RESET)"
	@echo -e ""
	@echo -e "$(BOLD)Environment$(RESET)"
	@echo -e "Virtual env: $(GREEN)$(shell [ -d .venv ] && echo "✓ Created" || echo "✗ Not created")$(RESET)"
	@echo -e "Lock file:   $(GREEN)$(shell [ -f $(UV_LOCK) ] && echo "✓ Present" || echo "✗ Missing")$(RESET)"
	@echo -e ""
	@if [ -d .venv ]; then \
		echo -e "$(BOLD)Installed Packages$(RESET)"; \
		$(UV) pip list; \
	fi

# Advanced Features
# ============================================================================

##@ Advanced

.PHONY: security
security: uv $(UV_LOCK) ## Run security checks
	@echo -e "$(BOLD)Running security audit...$(RESET)"
	$(UV) run pip-audit

.PHONY: licenses
licenses: uv $(UV_LOCK) ## Check dependency licenses
	@echo -e "$(BOLD)Checking licenses...$(RESET)"
	$(UV) run pip-licenses

.PHONY: profile
profile: uv $(UV_LOCK) ## Profile the application
	@echo -e "$(BOLD)Profiling application...$(RESET)"
	$(UV) run python -m cProfile -o profile.stats -m $(PROJECT_NAME)
	$(UV) run python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

.PHONY: benchmark
benchmark: uv $(UV_LOCK) ## Run benchmarks
	@echo -e "$(BOLD)Running benchmarks...$(RESET)"
	$(UV) run pytest tests/benchmarks/ -v

# Dependency tracking for auto-rebuild
# ============================================================================

# Track all Python files for changes
PY_FILES := $(shell find $(SRC_DIR) -name "*.py" 2>/dev/null)

# Auto-rebuild when source files change
.PHONY: watch
watch: ## Watch for changes and rebuild
	@echo -e "$(BOLD)Watching for changes...$(RESET)"
	@while true; do \
		$(MAKE) --no-print-directory test-fast || true; \
		inotifywait -qre modify $(SRC_DIR) $(TEST_DIR) $(PYPROJECT); \
	done

# Create cache directories
$(CACHE_DIR) $(UV_CACHE) $(BUILD_CACHE) $(COVERAGE_CACHE):
	@mkdir -p $@

# Include dependency rules for better tracking
-include $(PY_FILES:.py=.d)

%.d: %.py
	@echo "# Generated dependencies for $<" > $@
	@echo "$<: $(PYPROJECT)" >> $@