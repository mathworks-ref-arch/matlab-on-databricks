# Python Unit Tests

This directory contains unit tests for Python modules under
`resources/notebooks/mwhelpers/`.

Tests use [pytest](https://docs.pytest.org/).

## Prerequisites

- Python 3.11+
- Dependencies in `tests/unit/python/requirements.txt`

## Local Setup

From the repository root:

```bash
python3 -m pip install -r tests/unit/python/requirements.txt
```

## Running Tests

Run all Python unit tests with coverage:

```bash
python3 -m pytest --cov=resources/notebooks/ tests/unit/python
```

Run a single test module:

```bash
python3 -m pytest tests/unit/python/test_matlab.py
```

## Developing Tests

- **Location:** Add tests to `tests/unit/python/`.
- **Naming:** Use `test_*.py` naming.
- **Fixtures:** Reuse fixtures in `tests/unit/python/conftest.py` where possible.
- **Mocking:** Use `pytest-mock` (`mocker` fixture) for external dependencies and subprocess calls.

---------------

Copyright 2026 The MathWorks, Inc.
