# Databricks notebook source
# Copyright 2026 The MathWorks, Inc.

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 3: Run Tests
# MAGIC
# MAGIC Starts MATLAB via matlab-proxy (which runs onDatabricksSetup), shares the
# MAGIC engine for Python access, then runs MATLAB system tests via pytest.
# MAGIC The `suite/` directory is synced to the workspace by DAB.

# COMMAND ----------

# MAGIC %pip install pytest

# COMMAND ----------

import os
import sys

# Start MATLAB via matlab-proxy with engine sharing enabled.
from mwhelpers import dbx, matlab_proxy, subprocess_shim, user

USERNAME = os.environ["MW_TEST_USERNAME"]
MATLAB_ENGINE_NAME = "MatlabSystemTest"

os.environ["MWI_MATLAB_STARTUP_SCRIPT"] = (
    f"matlab.engine.shareEngine('{MATLAB_ENGINE_NAME}')"
)

matlab_test_uid = user.uid(USERNAME)

port = matlab_proxy.start(
    username=USERNAME,
    dbx_context=dbx.get_context(),
    env={
        "MLM_LICENSE_FILE": os.environ["MW_LICENSE_FILE_PATH"],
    },
)
assert port, "Failed to start matlab-proxy"
print(f"matlab-proxy started on port {port}")

# COMMAND ----------
notebook_path = (
    dbutils.notebook.entry_point.getDbutils()  # noqa: F821
    .notebook()
    .getContext()
    .notebookPath()
    .get()
)
bundle_dir = "/Workspace" + "/".join(notebook_path.split("/")[:-2])
suite_dir = bundle_dir + "/suite"

# Run pytest as matlab_test_user so matlab.engine can discover the shared session.
result = subprocess_shim.run(
    uid=matlab_test_uid,
    command=[
        sys.executable,
        "-m",
        "pytest",
        suite_dir,
        "-v",
        "--tb=short",
        "-p",
        "no:cacheprovider",
    ],
    env={
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "MATLAB_ENGINE_NAME": MATLAB_ENGINE_NAME,
    },
)

print(result.stdout)
if result.returncode != 0:
    print(f"STDERR:\n{result.stderr}")

# COMMAND ----------

assert result.returncode == 0, f"Tests failed (rc={result.returncode})"

print("All tests PASSED")
dbutils.notebook.exit("PASS")  # noqa: F821
