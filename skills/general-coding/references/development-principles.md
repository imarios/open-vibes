# Development Principles

Core development workflow patterns and philosophical approaches to writing maintainable, evolvable code.

## Read Existing Code First

When starting a new phase of the project, always read code in other files (like other unit tests, integration tests, migration files, etc.) to understand the main design patterns. Do not invent new ways of working unless verified with co-developers.

## Test-Driven Development (TDD)

### Stub Patterns
- When using TDD, all stubs should throw an exception and the unit tests that call them should all fail
- Do not try to anticipate the exception so that tests pass
- When asked to create a stub method, unless explicitly requested otherwise, never try to create mocked data or random values
- Keep stubs empty with `pass` or raise `NotImplementedError()` with proper messaging to make it easier to come back and fix them later

## DRY Principle (Don't Repeat Yourself)

Use DRY always when it comes to configurations. If there are constants, define them in a single place/file and reference them throughout the code.

## Simplicity and Incremental Development

### Prefer Simple Solutions
- Always look for existing code to iterate on instead of creating new code
- Always prefer simple solutions
- Only make changes that are requested or are well understood and related to the change being requested

### Complex Logic
For complex logic, split the problem into multiple smaller steps (5-10) and implement each step as a function that can be easily unit tested in isolation. This creates a sequence of steps as function calls rather than one large function that is harder to understand and troubleshoot.

### Fail Fast During Development
Early in the development phase, prefer to fail with Exceptions that clearly explain the problem rather than trying to fix things and be robust. Robustness can be added explicitly later, but early on it's important to spot issues in the code.

Example: If expecting JSON and receiving a string, fail immediately—don't try to convert the string into JSON.

## Pattern Consistency

### Avoid Introducing New Patterns
When fixing an issue or bug, do not introduce a new pattern or technology without first exhausting all options for the existing implementation. If you finally do introduce a new pattern, make sure to remove the old implementation afterwards so there is no duplicate logic.

## Change Scope Management

### Focused Changes
- Be careful to only make changes that are requested or are confident are well understood and related to the change being requested
- Keep the codebase clean and organized
- Focus on the areas of code relevant to the task
- Do not touch code that is unrelated to the task
- Always think about what other methods and areas of code might be affected by code changes

### Refactoring vs Features
- **When asked to refactor**: Focus only on refactoring. Add tests that are missing that may introduce bugs or unwanted changes to functionality
- **When asked to add a feature**: Focus on the feature, do not refactor! Do not change things that are unrelated to the feature at hand

### Avoid Major Architecture Changes
Avoid making major changes to the patterns and architecture of how a feature works, after it has shown to work well, unless explicitly instructed.

## File Organization

### File Size Limits
Avoid having files over 500 lines of code. Refactor at that point.

## Negative Logic

Avoid double negation. Prefer `"enable": true` rather than `"disable": false`.
