# Copyright 2026 The MathWorks, Inc.

"""Stub for `databricks.sdk` and `databricks.sdk.service.compute`.

Provides the minimal interfaces consumed by `mwhelpers.dbx`:
  - WorkspaceClient (clusters.get, command_execution.create/execute/destroy)
  - compute.Language.PYTHON
"""

import sys
import types


# ---------------------------------------------------------------------------
# compute.Language
# ---------------------------------------------------------------------------
class Language:
    PYTHON = "python"


# ---------------------------------------------------------------------------
# Cluster info returned by WorkspaceClient.clusters.get()
# ---------------------------------------------------------------------------
class _ClusterInfo:
    def __init__(self):
        self.cluster_name = "stub-cluster"
        self.autotermination_minutes = 0


# ---------------------------------------------------------------------------
# Result wrappers for command_execution
# ---------------------------------------------------------------------------
class _CommandResult:
    def __init__(self):
        self.id = "stub-context-id"
        self.status = "Finished"

    def result(self):
        return self


# ---------------------------------------------------------------------------
# WorkspaceClient stub
# ---------------------------------------------------------------------------
class _ClustersAPI:
    def get(self, cluster_id):
        return _ClusterInfo()


class _CommandExecutionAPI:
    def create(self, cluster_id, language):
        return _CommandResult()

    def execute(self, cluster_id, context_id, command, language):
        return _CommandResult()

    def destroy(self, cluster_id, context_id):
        pass


class WorkspaceClient:
    def __init__(self, host=None, token=None):
        self.clusters = _ClustersAPI()
        self.command_execution = _CommandExecutionAPI()


# ---------------------------------------------------------------------------
# Register into sys.modules
# ---------------------------------------------------------------------------
def register():
    """Install the databricks SDK stub modules into sys.modules."""
    # databricks (top-level namespace)
    databricks = types.ModuleType("databricks")
    databricks.__path__ = []

    # databricks.sdk
    sdk = types.ModuleType("databricks.sdk")
    sdk.WorkspaceClient = WorkspaceClient

    # databricks.sdk.service
    service = types.ModuleType("databricks.sdk.service")

    # databricks.sdk.service.compute
    compute = types.ModuleType("databricks.sdk.service.compute")
    compute.Language = Language

    # Wire up hierarchy
    databricks.sdk = sdk
    sdk.service = service
    service.compute = compute

    sys.modules.setdefault("databricks", databricks)
    sys.modules.setdefault("databricks.sdk", sdk)
    sys.modules.setdefault("databricks.sdk.service", service)
    sys.modules.setdefault("databricks.sdk.service.compute", compute)
