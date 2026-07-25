SHELL := /bin/bash

.PHONY: setup start stop restart logs status test test-backend test-demo validate reset seed clean checkpoint

setup:
	@test -f .env || cp .env.example .env
	docker compose build

start:
	docker compose up -d --build
	@echo "Dashboard: http://localhost:3000"
	@echo "Swagger:   http://localhost:8000/docs"
	@echo "Mailpit:   http://localhost:8025"
	@echo "Flower:    http://localhost:5555"
	@echo "Demo:      http://localhost:8080/product"

stop:
	docker compose down

restart: stop start

logs:
	docker compose logs -f --tail=150

status:
	docker compose ps

seed:
	docker compose exec api python -m app.cli

test: test-backend test-demo

test-backend:
	cd backend && python -m pytest --cov=app --cov-report=term-missing

test-demo:
	cd demo-target && PYTHONPATH=. python -m pytest -q

validate:
	python scripts/validate_repository.py

reset:
	docker compose down -v --remove-orphans
	docker compose up -d --build

clean:
	rm -rf backend/.pytest_cache backend/.coverage backend/htmlcov frontend/node_modules frontend/dist

checkpoint:
	python scripts/create_checkpoint.py
