# Python Code Standards

## Code Style

- Use **PEP 8** style compliance throughout the codebase.
- Follow Black code formatting
- Use isort for import sorting
- Unless we have conditional imports, have all the imports at the top of the file
- Follow PEP 8 naming conventions:
  - snake_case for functions and variables
  - PascalCase for classes
  - UPPER_CASE for constants
- Implement linting with tools like flake8.
- Maximum line length of 88 characters (Black default)
- Use absolute imports over relative imports
- Prefer **descriptive variable names** with auxiliary verbs (e.g., `is_active`, `has_permission`)
- Favor **functional, declarative programming**; avoid unnecessary classes
- Prefer `def` for synchronous and `async def` for async logic
- Use **lowercase with underscores** for file and directory names
- Set up `pre-commit hooks` for automated quality checks
- Write docstrings in a consistent format (e.g., Google-style for new, or keep existing project format for existing projects)
- Follow the "Flat is better than nested" principle from the Zen of Python
- Use context managers (`with` statements) for resource management
- Leverage `list/dict` comprehensions for cleaner code, but avoid excessive complexity
- Consider `dataclasses` for data structures
- Implement proper logging using the `logging` module instead of print statements

## Logging

If the code is meant for production and is not just an internal tool then:
- Log to a file not just stdout
- Rotate and clean logs
- Format logs as JSONs
- Include "tenant" information

## Best Practices

- Use context managers (`with` statements) for resource management
- Leverage `list/dict` comprehensions for cleaner code, but avoid excessive complexity
- Consider `dataclasses` for data structures
- Implement proper logging using the `logging` module instead of print statements
- Prefer descriptive variable names with auxiliary verbs (e.g., `is_active`, `has_permission`)
- Favor functional, declarative programming; avoid unnecessary classes
- Prefer `def` for synchronous and `async def` for async logic
- Use lowercase with underscores for file and directory names
- Set up pre-commit hooks for automated quality checks
- Write docstrings in a consistent format (e.g., Google-style for new projects, or keep existing project format for existing projects)
- Follow the "Flat is better than nested" principle from the Zen of Python
