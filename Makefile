.PHONY: up lint

up:
	@if ! command -v docker-compose &> /dev/null; then \
		echo "Docker is not installed. Download Docker Desktop at https://www.docker.com/get-started/"; \
		exit 1; \
	fi
	docker-compose up --build

lint:
	@if ! command -v uv &> /dev/null; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	uv run ruff check --fix .
	uv run ruff format .
	uv run mypy .
