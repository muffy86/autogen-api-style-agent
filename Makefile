.PHONY: install dev serve mcp cli test lint format docker-build docker-run docker-up docker-down bootstrap setup-trae clean typecheck lint-all test-all smoke post-deploy-verify

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

typecheck:
	mypy src/autogen_api_agent --ignore-missing-imports || true
	pnpm run typecheck

lint-all:
	ruff check src/ tests/
	ruff format --check src/ tests/
	pnpm run lint

test-all:
	pytest -v
	pnpm run test

smoke:
	bash scripts/smoke-test.sh

post-deploy-verify:
	bash scripts/post-deploy-verify.sh

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
