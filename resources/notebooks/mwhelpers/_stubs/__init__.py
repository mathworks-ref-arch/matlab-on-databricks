# Copyright 2026 The MathWorks, Inc.

"""Auto-installing stubs for Databricks-specific packages.

These stubs provide minimal mock implementations of `databricks.sdk` and
`dbruntime` so that the notebook and mwhelpers modules can be imported and
run locally without a real Databricks cluster.

Stubs are registered into `sys.modules` only when the real packages are not
installed. On a Databricks cluster the real packages take precedence and
this module is never activated.

Usage:
    Call `install()` to register the stubs. This is done automatically by
    `mwhelpers/__init__.py` when the real packages are missing.
"""

from . import _databricks_sdk_stub, _dbruntime_stub


def install():
    """Register stub modules into sys.modules for all Databricks dependencies."""
    _databricks_sdk_stub.register()
    _dbruntime_stub.register()

    print("[mwhelpers] Databricks stub packages activated (local development mode)")
