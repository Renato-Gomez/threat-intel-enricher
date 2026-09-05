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
