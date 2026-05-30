SHELL := /bin/bash
PYTHON ?= python3
VENV := .venv
VENV_PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.DEFAULT_GOAL := help

.PHONY: help install run build clean kill lint format typecheck test coverage security ci release-dry-run

help:
	@echo "LongView Markets"
	@echo "Comandos disponibles:"
	@echo "  make install     Instala backend, frontend y prepara .env local"
	@echo "  make run         Arranca backend + frontend e inicializa datos si faltan"
	@echo "  make build       Compila frontend y prepara artefactos de release"
	@echo "  make clean       Limpia caches, builds y temporales"
	@echo "  make kill        Detiene procesos arrancados por make run"
	@echo "  make lint        Ejecuta linters backend/frontend"
	@echo "  make format      Formatea backend/frontend"
	@echo "  make typecheck   Ejecuta typecheck backend/frontend"
	@echo "  make test        Ejecuta tests backend/frontend"
	@echo "  make coverage    Ejecuta cobertura y exige backend >= 80%"
	@echo "  make security    Ejecuta checks de seguridad"
	@echo "  make ci          Ejecuta lint, typecheck, test, coverage, security y build"

install:
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "backend[dev]"
	npm --prefix frontend install
	test -f .env || cp .env.example .env
	cd backend && ../$(VENV_PY) -m app.cli.main --project-root ..

run:
	$(VENV_PY) scripts/run/run_app.py

build:
	cd backend && ../$(VENV_PY) -m ruff check app
	npm --prefix frontend run build
	$(VENV_PY) scripts/package/build_release.py

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage build dist logs .pids
	rm -rf frontend/dist frontend/coverage frontend/node_modules/.vite
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +

kill:
	$(VENV_PY) scripts/run/kill_app.py

lint:
	cd backend && ../$(VENV_PY) -m ruff check app
	cd backend && ../$(VENV_PY) -m black --check app
	$(VENV_PY) scripts/design/check_design_system.py
	npm --prefix frontend run lint
	npm --prefix frontend run format:check

format:
	cd backend && ../$(VENV_PY) -m ruff check app --fix
	cd backend && ../$(VENV_PY) -m black app
	npm --prefix frontend run format

typecheck:
	cd backend && ../$(VENV_PY) -m mypy app
	npm --prefix frontend run typecheck

test:
	cd backend && ../$(VENV_PY) -m pytest --no-cov
	npm --prefix frontend run test

coverage:
	cd backend && ../$(VENV_PY) -m pytest

security:
	cd backend && ../$(VENV_PY) -m bandit -r app -q -x app/tests
	cd backend && ../$(VENV_PY) -m pip_audit --skip-editable
	npm --prefix frontend audit --audit-level=critical
	$(VENV_PY) scripts/check_secrets.py

ci: lint typecheck test coverage security build

release-dry-run:
	$(VENV_PY) scripts/release/check_release_artifacts.py --platform current --allow-missing-windows-exe
