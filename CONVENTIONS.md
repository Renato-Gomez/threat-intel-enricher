# 🔍 General Principles

- The source code is written using Python 3.11+.
- Follow best practices for maintainability, readability, and efficiency.
- Use `black` for formatting and `ruff` for linting and import sorting.
- Enforce style checks via pre-commit hooks.
- Prefer `pytest` as the testing framework.

# 📦 Naming Conventions

- **Class Names (CamelCase)**: Example: `ThreatExtractor`, `AbuseIPDBProvider`.
- **Functions and Methods (snake_case)**: Example: `extract_iocs()`, `enrich_alert()`.
- **Private Methods**: Use `__` prefix for private methods (e.g., `__handle_rate_limit()`).
- **Protected Methods**: Use `_` prefix for methods intended for internal use (e.g., `_make_request()`).

# 🧩 Object-Oriented Design Principles (OOP)

- Follow the **Single Responsibility Principle (SRP)**: Each class should have a single responsibility.
- Follow the **Open/Closed Principle (OCP)**: New Threat Intel providers should be added by extending a base class.
- Use abstract base classes (`ABC`) to define interfaces for API providers.
- Prefer **composition over inheritance**.
- **Data Validation**: Use `pydantic` to model and validate data structures (e.g., the extracted IoCs) ensuring strict typing before processing.

# 💡 Error Handling

- Use exceptions rather than error codes for handling errors.
- **Robustness:** Provide explicit handling for API timeouts, network failures, and HTTP 429 Rate Limits. The automation must not fail silently or leave processes hanging.
- Provide clear error messages that guide the user or the SIEM/SOAR platform.

# ⚙️ Functional Core, Imperative Shell (FCIS)

- Separate parsing/extraction logic (Pure Functions) from API calls (Imperative Shell).
- `ThreatExtractor` should only parse strings and return `pydantic` models, making it 100% testable without mocking HTTP requests.

# 🧪 Testing Rules

- All tests must reside in the `tests/` directory at the root of the project.
- Inside `tests/`, use the `unit/` directory for unit tests. (Later, an `integration/` directory can be added for integration tests).
- All test files must start with the `test_` prefix (e.g., `test_config.py`).
- All test methods or functions within a class must start with the `test_` prefix.
- **Unit Test Isolation:** Each test must be independent, kept simple, and test specific and granular parts of the code.
- **No Side Effects:** Tests must never have side effects; the system must remain in the exact same state as before the test execution.
- **Pytest Ecosystem:** Leverage `pytest` features appropriately (e.g., `@pytest.mark.skip` to skip, `@pytest.mark.parametrize` to reuse inputs across different tests, and `pytest.MonkeyPatch` for safely mocking environment variables or system states without side effects).
