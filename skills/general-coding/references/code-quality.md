# Code Quality Standards

Documentation, security, resource management, and maintainability practices for production-ready code.

## Documentation

### What to Document
- Document public APIs, complex functions, and non-obvious code segments
- Include comments for complex logic, but avoid commenting obvious code
- Add context to complex solutions to help others understand the approach
- Leave TODO comments for incomplete work that needs attention
- Document environment setup in a README.md for new developers

### What NOT to Document
- When making code changes, avoid adding a comment about the change unless absolutely needed
- Do not comment on self-explanatory code
- Avoid redundant comments that simply restate the code

### Documentation Tools
- Use context7 MCP tool for documentation and examples for libraries you don't know enough about

## Code Formatting

Maintain consistent code formatting throughout the project. Use automated formatters and linters to enforce consistency.

**Best practices:**
- Follow the project's established formatting style
- Use automated formatters (Black, Prettier, etc.)
- Configure pre-commit hooks for automated quality checks
- Follow language-specific style guides (PEP 8 for Python, etc.)

## Security Practices

### Sensitive Data Handling
- Handle sensitive data securely
- **Never log passwords, tokens, API keys, or other credentials**
- Sanitize data before logging
- Use environment variables for secrets
- Never commit secrets to version control

### Input Validation
- Validate and sanitize all user inputs
- Use parameterized queries to prevent SQL injection
- Validate file uploads and restrict file types
- Implement proper authentication and authorization checks

## Resource Management

### Memory and Resource Cleanup
Be mindful of memory usage and resource cleanup:
- Close database connections when done
- Dispose of file handles and network connections
- Clean up temporary files
- Use context managers (`with` statements in Python) for automatic cleanup
- Monitor memory usage in long-running processes

### Connection Pooling
- Use connection pooling for databases and external services
- Configure appropriate pool sizes
- Handle connection timeouts gracefully

## Error Handling and Logging

### Error Logging
Log errors with appropriate context for debugging:
- Include relevant identifiers (user ID, request ID, etc.)
- Log stack traces for exceptions
- Use structured logging (JSON format) for production
- Include timestamps and severity levels
- Add correlation IDs for request tracing

### Log Levels
Use appropriate log levels:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error events that might still allow the application to continue
- **CRITICAL**: Critical events that may cause the application to abort

## Dependency Management

### Adding Dependencies
Be cautious about adding new dependencies; evaluate their necessity:
- Check if the functionality can be implemented without a new dependency
- Evaluate the dependency's maintenance status
- Consider the size and impact on build times
- Review security vulnerabilities
- Check license compatibility

### Dependency Updates
- Keep dependencies up to date for security patches
- Test thoroughly after updating dependencies
- Use lock files to ensure reproducible builds

## Performance Considerations

### Optimization Strategy
- Optimize critical paths from the beginning
- Avoid premature optimization for non-critical code
- Profile before optimizing
- Measure performance impact of changes
- Consider scalability implications

### Code Efficiency
- Use appropriate data structures and algorithms
- Avoid unnecessary loops and iterations
- Cache expensive computations when appropriate
- Lazy-load resources when possible

## Code Organization

### File and Module Organization
- Keep related code together
- Use clear, descriptive names for files and directories
- Follow the project's established structure
- Separate concerns appropriately (business logic, data access, presentation)

### Code Reusability
- Extract common functionality into reusable functions/modules
- Avoid code duplication (DRY principle)
- Create utility modules for shared functionality
- Use inheritance and composition appropriately
