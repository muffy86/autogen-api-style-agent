.PHONY: install dev serve mcp cli test lint format docker-build docker-run docker-up docker-down bootstrap setup-trae clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

serve:
	agent serve --reload

mcp:
	agent mcp-serve

cli:
	agent interactive

test:
	pytest -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/

docker-build:
	docker build -t autogen-agent .

docker-run:
	docker run -p 8000:8000 --env-file .env autogen-agent

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

bootstrap:
	bash scripts/bootstrap.sh

setup-trae:
	python scripts/setup_trae.py

clean:
	rm -rf .venv __pycache__ .pytest_cache dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
