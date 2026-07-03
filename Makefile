.PHONY: help build up down test lint logs clean

help:
	@echo "Available commands:"
	@echo "  make build  - Rebuilds Docker images"
	@echo "  make up     - Starts containers in background"
	@echo "  make down   - Stops and removes containers"
	@echo "  make logs   - Shows web container logs"
	@echo "  make test   - Runs pytest inside the container"
	@echo "  make lint   - Runs pylint"
	@echo "  make clean  - Removes cache files"

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
	docker compose exec web pylint src/app tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +