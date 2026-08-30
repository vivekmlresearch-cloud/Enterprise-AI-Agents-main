.PHONY: up down seed test fmt

up:
	docker compose up --build

down:
	docker compose down -v

seed:
	python scripts/seed_demo_logs.py

test:
	cd backend && pytest -q

fmt:
	cd backend && ruff check . --fix && black .
