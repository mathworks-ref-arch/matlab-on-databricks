# Shell Unit Tests

This directory contains unit tests for shell helper scripts in
`resources/notebooks/mwhelpers/scripts/`.

Tests are written with
[Bats (Bash Automated Testing System)](https://github.com/bats-core/bats-core).

## Prerequisites

To run these tests locally, install:

- [Bats](https://bats-core.readthedocs.io/en/stable/installation.html)
- [Pre-commit](https://pre-commit.com/#install)
- [ShellCheck](https://github.com/koalaman/shellcheck#installing)
- [shfmt](https://github.com/mvdan/sh)

## Local Setup

These tests use Bats helper libraries (`bats-support` and `bats-assert`).

From the repository root:

```bash
mkdir -p .bats
git clone https://github.com/bats-core/bats-support.git .bats/bats-support
git clone https://github.com/bats-core/bats-assert.git .bats/bats-assert
```

## Running Tests

Run from the repository root:

```bash
SOURCE_SCRIPTS_DIR="$(pwd)/resources/notebooks/mwhelpers/scripts" \
BATS_LIB_PATH="$(pwd)/.bats" \
bats tests/unit/shell/
```

Run a single file:

```bash
SOURCE_SCRIPTS_DIR="$(pwd)/resources/notebooks/mwhelpers/scripts" \
BATS_LIB_PATH="$(pwd)/.bats" \
bats tests/unit/shell/CreateUser.bats
```

## Developing Tests

- **Location:** Add tests to `tests/unit/shell/`.
- **Naming:** Use a `.bats` extension.
- **Structure:** Use `setup_file()` and `teardown_file()` for shared setup/cleanup.
- **Isolation:** Prefer mocks/stubs for system commands instead of relying on host state.
- **Script loading:** Use `SOURCE_SCRIPTS_DIR` when loading scripts under test.

---------------

Copyright 2026 The MathWorks, Inc.
