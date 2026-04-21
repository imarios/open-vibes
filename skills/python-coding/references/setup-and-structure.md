# Python Setup and Project Structure

## Key Tools

- Always use `poetry` for dependency management and working with a virtual environment.
  - When we run python we always use `poetry run python`

## Adding Dependencies

- Use `poetry add` to add dependencies rather than manually editing `pyproject.toml`
- Poetry will automatically resolve and install the latest compatible version
- Never try to guess the most current version number

**Examples:**
```bash
# Add a production dependency
poetry add requests

# Add a development dependency
poetry add --group dev pytest

# Add a specific version if needed
poetry add "requests>=2.28.0"
```

## Library Documentation

- Use the **context7 MCP tool** any time you don't have high confidence about a library
- Context7 provides up-to-date documentation and examples for Python libraries
- Always consult context7 before implementing unfamiliar library features
- This ensures you're using current best practices and avoiding deprecated patterns

## Project Structure

- Use src-layout with `src/your_package_name/`
- Place tests in `tests/` directory parallel to `src/`
- Keep configuration in `config/` or as environment variables
- Use `pyproject.toml` for modern dependency management with Poetry.
- Place static files in `static/` directory
- Always use virtual environments.
- Use __init__.py files appropriately to control import exposure.
- Consider using `.env` files with `python-dotenv` for environment variables.

## Running Python Commands

Always execute Python commands using `poetry`. Examples:
- `poetry run pytest`
- `poetry run python main.py`
- `poetry run mypy src/`

## Scripts

We want to use python to implement most of our scripts.

```toml
[tool.poetry.scripts]
# Format: "command_name" = "module_path:function_name"
start = "my_package.main:main"
migrate = "my_package.db.migrations:run_migrations"
lint = "my_package.tools.linting:run_linters"
test = "my_package.tests.runner:run_tests"
```

With this configuration:
- `poetry run start` will execute the `main()` function from `my_package/main.py`
- `poetry run migrate` will execute the `run_migrations()` function from `my_package/db/migrations.py`
- `poetry run lint` will execute the `run_linters()` function from `my_package/tools/linting.py`
- `poetry run test` will execute the `run_tests()` function from `my_package/tests/runner.py`

This approach lets you define convenient command aliases for your project's common operations.
