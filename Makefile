.PHONY: lint fmt typecheck test all clean

# Run ruff lint check
lint:
	poetry run ruff check jamanthi tests

# Run ruff format check
fmt:
	poetry run ruff format jamanthi tests
	poetry run ruff check --fix jamanthi tests

# Run mypy type checks
typecheck:
	poetry run mypy jamanthi tests

# Run pytest
test:
	poetry run pytest -v -s

# Run all checks
all: lint fmt typecheck test

#Clean up project directories
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
