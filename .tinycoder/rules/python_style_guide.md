# Python Style Guide

## Code Style and Organization

- **PEP 8 Compliance**: Follow PEP-8 with 4-space indentation
- **Naming Conventions**:
  - `snake_case` for functions, variables, and methods
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants
  - `_leading_underscore` for private attributes/methods

## Writing Clean Code

- **Type Hints**: Always use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings with clear sections
- **String Formatting**: Use f-strings for clarity and performance
- **Resource Management**: Always use context managers for files and resources
- **Comments**: Use comments to explain "why" not "what", don't state the obvious

## Error Handling

- Use specific exception types, not just `except Exception:`
- Handle exceptions where you can take meaningful action
- Validate input early to avoid deep error handling

## Avoid Common Pitfalls

- Mutable default arguments: `def func(arg=[]): # Dangerous!`
- Deep nesting: Refactor code with more than 3 levels of indentation
- Magic numbers: Use constants or config variables instead
- Reinventing built-in functionality

Remember: Code is read much more often than it's written. Optimize for readability and maintainability.