.PHONY: help build up down test lint logs clean

help:
	@echo "Verfügbare Befehle:"
	@echo "  make build  - Baut die Docker-Images neu"
	@echo "  make up     - Startet die Container im Hintergrund"
	@echo "  make down   - Stoppt und entfernt die Container"
	@echo "  make logs   - Zeigt die Logs des Web-Containers"
	@echo "  make test   - Führt Pytest im Container aus"
	@echo "  make lint   - Führt den Ruff Linter und Formatter aus"
	@echo "  make clean  - Entfernt Cache-Dateien"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f web

test:
	docker compose exec web pytest -v

lint:
	docker compose exec web ruff check .
	docker compose exec web ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
