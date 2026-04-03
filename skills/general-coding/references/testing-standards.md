# Testing Standards

Test creation hygiene, isolation patterns, and best practices for writing reliable, maintainable tests.

## Key Test Creation Hygiene Patterns

Follow these essential patterns when creating tests:

### 1. Always Use Unique IDs
Add UUID suffixes to prevent conflicts between test runs. This ensures tests can run in parallel or be re-run without cleanup issues.

**Example:**
```python
test_user_id = f"test_user_{uuid.uuid4()}"
test_resource_name = f"test_resource_{uuid.uuid4()}"
```

### 2. Disable Background Workers
Prevent ARQ workers, cron jobs, and other background processes from interfering during tests. This eliminates non-deterministic behavior and race conditions.

**Example:**
```python
@pytest.fixture(autouse=True)
def disable_background_workers():
    # Disable ARQ, cron, etc.
    pass
```

### 3. Proper Test Isolation
Each test should be independent and not rely on other tests. Tests should be able to run in any order without affecting each other.

**Guidelines:**
- Do not share state between tests
- Reset state in setup/teardown fixtures
- Use fresh test data for each test
- Avoid dependencies on test execution order

### 4. Database Cleanup
Ensure proper commit/rollback patterns to maintain clean database state between tests.

**Guidelines:**
- Use transactions that rollback after each test
- Clean up test data explicitly if rollback isn't possible
- Verify database state in assertions
- Use database fixtures that ensure clean state

## Test Type Separation

### Unit Tests
- **Definition**: Tests that do NOT require a running server or external dependencies
- **Characteristics**: Fast, isolated, test individual functions/classes
- **Execution**: Should run with standard `pytest` command
- **Location**: Typically in `tests/unit/`

### Integration Tests
- **Definition**: Tests that require multiple components but may not need full server
- **Characteristics**: Test interactions between modules/classes
- **Marking**: Mark with `@pytest.mark.integration`
- **Execution**: Can be excluded from regular runs with `-m "not integration"`

### Live Tests
- **Definition**: Tests that require a running server or external services
- **Characteristics**: End-to-end testing, slower execution
- **Marking**: Mark with `@pytest.mark.live`
- **Execution**: Exclude from regular runs with `-m "not live"`

## Test Organization Best Practices

### Test File Structure
```
tests/
├── unit/              # Fast, isolated unit tests
├── integration/       # Multi-component integration tests
└── live/              # Server-dependent live tests
```

### Test Naming
Use descriptive test names that explain what is being tested:
```python
def test_user_creation_with_valid_email():
    pass

def test_user_creation_fails_with_invalid_email():
    pass
```

### Fixtures
Implement proper fixtures for re-usability and clean test setup/teardown.

## Running Tests

**All unit tests (default):**
```bash
pytest
```

**Exclude slow tests:**
```bash
pytest -m "not slow"
```

**Exclude integration and live tests:**
```bash
pytest -m "not integration and not live"
```

**Run only specific test:**
```bash
pytest tests/test_module.py::test_specific_function
```
