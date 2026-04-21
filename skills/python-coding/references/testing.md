# Python Testing with pytest

## Testing Framework

- Use `pytest` for testing
- Use pytest-cov for coverage
- Implement proper fixtures for re-usability
- Use proper mocking with pytest-mock
- Use @pytest.mark.slow annotations for tests that take longer time to run
- For stub methods during TDD have them raise a NotImplementedError() with proper messaging rather than just using `pass`

## Test Organization

Place tests in `tests/` directory parallel to `src/`

```
project/
├── src/
│   └── my_package/
│       └── module.py
└── tests/
    └── test_module.py
```

## Fixtures

Implement proper fixtures for re-usability:

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_something(sample_data):
    assert sample_data["key"] == "value"
```

## Mocking

Use proper mocking with pytest-mock:

```python
def test_with_mock(mocker):
    mock_func = mocker.patch('module.function')
    mock_func.return_value = 42
    assert module.function() == 42
```

## Test Annotations

Use pytest markers to categorize tests:

```python
@pytest.mark.slow
def test_long_running():
    # Test that takes a long time
    pass

@pytest.mark.integration
def test_database_integration():
    # Integration test
    pass
```

## TDD Stub Patterns

For stub methods during TDD, have them raise a NotImplementedError() with proper messaging rather than just using `pass`:

```python
def stub_method():
    raise NotImplementedError("stub_method needs to be implemented")
```

This ensures tests fail clearly rather than passing silently.

## Coverage

Use pytest-cov for coverage reporting:

```bash
poetry run pytest --cov=src --cov-report=html
```

## Integration Testing Patterns

### Async Workflow Testing with Database Sessions

When testing async workflows that involve background tasks and database access, use the tuple fixture pattern to avoid race conditions caused by database session isolation.

**Problem**: Background tasks run in separate database sessions and can't see uncommitted test data, causing tests to fail even when logic is correct.

**Solution**: Use manual execution pattern with shared session.

**Implementation Pattern**:

```python
@pytest.fixture
async def client(db_session) -> tuple[AsyncClient, AsyncSession]:
    """Return tuple of (http_client, session) for integration tests."""
    async with AsyncClient(app=app, base_url="http://test") as http_client:
        yield http_client, db_session

async def test_workflow_execution(self, client):
    # 1. Unpack client and session from fixture
    http_client, session = client

    # 2. Create workflow/templates/test data
    workflow_id = await create_test_workflow(http_client)

    # 3. CRITICAL: Commit test data so background task can see it
    await session.commit()

    # 4. Start workflow via API
    response = await http_client.post(f"/v1/{tenant}/workflows/{workflow_id}/run",
                                    json={"input_data": test_input})
    assert response.status_code == 202
    workflow_run_id = response.json()["workflow_run_id"]

    # 5. Manually trigger execution using same session
    from backend_y.services.workflow_execution import WorkflowExecutor
    executor = WorkflowExecutor(session)
    await executor.monitor_execution(workflow_run_id)
    await session.commit()

    # 6. Verify results via API
    details = await http_client.get(f"/v1/{tenant}/workflow-runs/{workflow_run_id}")
    assert details.status_code == 200
    # ... verify execution results
```

**Key Requirements**:
- **Use tuple fixture**: `async def client(self, db_session) -> tuple[AsyncClient, AsyncSession]`
- **Unpack in test**: `http_client, session = client`
- **Commit before execution**: `await session.commit()`
- **Manual execution**: Use executor with same session to avoid race conditions
- **Commit after execution**: `await session.commit()`

**When to Use**:
- ✅ Tests that verify workflow execution completes correctly
- ✅ Tests that check workflow output data/results
- ✅ Tests that validate complex workflow patterns (fan-in, pipelines)
- ❌ Tests that only verify API responses (202, 404, etc.)
- ❌ Tests that check immediate workflow creation/validation

**Benefits**:
- Eliminates race conditions in test execution
- Tests run synchronously, making debugging easier
- Each test gets its own session and execution context
- Uses same execution logic as production, just triggered manually

## HTTP Mocking with pytest-httpx

Use pytest-httpx for testing code that makes HTTP requests, especially when testing retry logic.

**Installation**:
```bash
poetry add --group dev pytest-httpx
```

**Basic Usage**:

```python
def test_api_call(httpx_mock):
    # Mock a successful response
    httpx_mock.add_response(
        url="https://api.example.com/data",
        json={"result": "success"},
        status_code=200
    )

    # Call your code that makes HTTP requests
    result = fetch_data()
    assert result["result"] == "success"
```

**Testing Retry Logic**:

```python
def test_retry_on_500(httpx_mock):
    # First two calls fail with 500, third succeeds
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(
        json={"result": "success"},
        status_code=200
    )

    # Code with @http_retry_policy() should retry and eventually succeed
    result = api_call_with_retry()
    assert result["result"] == "success"

    # Verify 3 requests were made
    assert len(httpx_mock.get_requests()) == 3
```

**Testing Exception Injection**:

```python
import httpx

def test_retry_on_network_error(httpx_mock):
    # First call raises connection error, second succeeds
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))
    httpx_mock.add_response(json={"result": "success"}, status_code=200)

    result = api_call_with_retry()
    assert result["result"] == "success"
```

**Best Practices**:
- Test actual code paths instead of bypassing HTTP calls in test environments
- Verify retry behavior with exception injection and response mocking
- Use httpx_mock.get_requests() to verify number of attempts
- Mock both success and failure scenarios
- Test that 4xx errors (except 429) don't retry, but 5xx errors do

**Example with Tenacity Retry**:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_with_retry(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def test_fetch_with_retry_eventually_succeeds(httpx_mock):
    # Simulate transient failures followed by success
    httpx_mock.add_response(status_code=503)
    httpx_mock.add_response(status_code=503)
    httpx_mock.add_response(json={"data": "ok"}, status_code=200)

    result = await fetch_with_retry("https://api.example.com/endpoint")
    assert result["data"] == "ok"
    assert len(httpx_mock.get_requests()) == 3
```

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_module.py

# Run specific test
poetry run pytest tests/test_module.py::test_function

# Run tests excluding slow tests
poetry run pytest -m "not slow"
```
