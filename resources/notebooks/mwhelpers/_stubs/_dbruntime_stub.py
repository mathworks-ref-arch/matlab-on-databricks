# Copyright 2026 The MathWorks, Inc.

"""Stub for `dbruntime.databricks_repl_context`.

Provides a mock `get_context()` that returns a context object with the
same attributes used by `mwhelpers.dbx`.
"""

import os
import sys
import types


class _StubContext:
    """Mimics the Databricks REPL context with safe local defaults."""

    def __init__(self):
        self.apiToken = os.environ.get("DATABRICKS_TOKEN", "stub-token")
        self.apiUrl = "localhost"
        self.browserHostName = os.environ.get("DATABRICKS_HOST", "localhost")
        self.clusterId = os.environ.get("DATABRICKS_CLUSTER_ID", "stub-cluster-id")
        self.isInJob = False
        self.runtimeVersion = "0.0.0-stub"
        self.user = os.environ.get("USER", "localuser")
        self.workspaceId = "0"
        self.workspaceUrl = "localhost"


_context = _StubContext()


def get_context():
    return _context


# ---------------------------------------------------------------------------
# Register into sys.modules
# ---------------------------------------------------------------------------
def register():
    """Install the dbruntime stub modules into sys.modules."""
    dbruntime = types.ModuleType("dbruntime")
    dbruntime.__path__ = []

    repl_context = types.ModuleType("dbruntime.databricks_repl_context")
    repl_context.get_context = get_context

    dbruntime.databricks_repl_context = repl_context

    sys.modules.setdefault("dbruntime", dbruntime)
    sys.modules.setdefault("dbruntime.databricks_repl_context", repl_context)
