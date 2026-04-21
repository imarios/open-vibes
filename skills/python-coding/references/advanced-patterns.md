# Advanced Python Patterns

## Type Hints

- Use **type hints** for all function parameters and return values
- Import types from `typing` module
- Use `Type | None` instead of `Optional[Type]`
- Use `TypeVar` for generic types
- Define custom types in `types.py`
- Use `Protocol` for duck typing
- Implement `mypy` for static type checking

### Type Hints Examples

```python
from typing import TypeVar, Protocol

# Basic type hints
def greet(name: str) -> str:
    return f"Hello, {name}"

# Use Type | None instead of Optional
def find_user(user_id: int) -> User | None:
    # Implementation
    pass

# Generic types
T = TypeVar('T')
def first(items: list[T]) -> T | None:
    return items[0] if items else None

# Protocol for duck typing
class Drawable(Protocol):
    def draw(self) -> None:
        ...
```

### Running mypy

```bash
poetry run mypy src/
```

## AsyncIO

Core rules:
- **Upgrade first** – CPython 3.12+ ships an asyncio core that's up to ~75% faster; most gains are free.
- **Single entry** – wrap your program in async def main() and run with asyncio.run(main()) (or asyncio.Runner when you need nested loops, e.g. in REPL/tests).
- **Structured concurrency** – prefer asyncio.TaskGroup (3.11+) to create_task/gather; Python 3.13 fixed tricky cancellation races.
- **Keep coroutines pure-async** – push CPU-bound or blocking I/O to await asyncio.to_thread(fn, *args) (or a process pool).
- **Time-bounded awaits** – use asyncio.timeout(seconds); propagate asyncio.CancelledError in a finally:.
- **Back-pressure** – limit fan-out with asyncio.Semaphore(N) (or anyio.CapacityLimiter) to stay within FD/connection limits.
- **Micro-optimise last** – uvloop still buys ~1.3–2× throughput; loop.set_task_factory(asyncio.eager_task_factory) can shave overhead for in-memory hits—always benchmark.

### Preferred AsyncIO Pattern (HTTP burst)

```python
from __future__ import annotations
import asyncio
from typing import List

# — optional faster event loop on Linux/macOS —
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass  # default loop is fine

from langchain_openai import ChatOpenAI

CONCURRENCY = 10                      # ↩︎ stay below OpenAI rate limits
SEM = asyncio.Semaphore(CONCURRENCY)
TIMEOUT = 30                          # seconds

async def ask(llm: ChatOpenAI, prompt: str) -> str:
    """Run a single prompt with defensive timeouts & soft‑fail."""
    try:
        async with SEM, asyncio.timeout(TIMEOUT):
            resp = await llm.ainvoke(prompt)     # async API call
            return resp.content  # ChatMessage → str
    except Exception as e:
        return f"Error for {prompt[:40]}…: {e}"

async def main(prompts: List[str]) -> List[str]:
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(ask(llm, p)) for p in prompts]
    return [t.result() for t in tasks]

if __name__ == "__main__":
    questions = [
        "Explain async in one sentence",
        "Python vs Rust for ML?",
        "Best pizza topping?",
    ]
    answers = asyncio.run(main(questions))
    for q, a in zip(questions, answers):
        print(q, "→", a[:60])
```

Runs six-figure req/s on commodity hardware when I/O-bound.

## Key AsyncIO Patterns

### Single Entry Point

```python
async def main():
    # Your async code here
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### Structured Concurrency with TaskGroup

```python
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(async_function1())
    task2 = tg.create_task(async_function2())
# Tasks are automatically awaited and errors propagated
```

### Time-Bounded Awaits

```python
async with asyncio.timeout(10):
    result = await long_running_operation()
```

### Back-Pressure with Semaphore

```python
sem = asyncio.Semaphore(10)

async def limited_task():
    async with sem:
        # Only 10 concurrent executions
        await do_work()
```

### CPU-Bound Work in Async Context

```python
import asyncio

def cpu_intensive_task(data):
    # CPU-bound work
    return process(data)

async def main():
    result = await asyncio.to_thread(cpu_intensive_task, data)
```
