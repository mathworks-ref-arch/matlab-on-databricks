# Databricks notebook source
# Copyright 2026 The MathWorks, Inc.

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 1: Set Up MATLAB License
# MAGIC
# MAGIC Reads the license content from Databricks secrets, writes it to a file,
# MAGIC creates a test user, sets MLM_LICENSE_FILE, and validates MATLAB can start.

# COMMAND ----------

import os
from pathlib import Path

from mwhelpers import matlab, user

# COMMAND ----------

LICENSE_FILE_PATH = os.environ["MW_LICENSE_FILE_PATH"]

# COMMAND ----------

# Read license content from Databricks secrets
license_content = dbutils.secrets.get(scope="matlab", key="license")  # noqa: F821
assert license_content, "Secret 'matlab/license' is empty"

# COMMAND ----------

# Write license to file
Path(LICENSE_FILE_PATH).write_text(license_content, encoding="utf-8")
os.environ["MLM_LICENSE_FILE"] = LICENSE_FILE_PATH
print(f"License written to: {LICENSE_FILE_PATH}")

# COMMAND ----------

# Verify license by running MATLAB
username = os.environ["MW_TEST_USERNAME"]
user.uid(username, create_if_not_exists=True)

success, output = matlab.run_code_with_matlab_batch(
    username=username,
    code='disp("license_ok"); ver;',
    license_server_address=LICENSE_FILE_PATH,
)
print(output)
assert success, f"MATLAB license check failed:\n{output}"
assert "license_ok" in output, "MATLAB did not produce expected output"

# COMMAND ----------

print("License setup PASSED")
dbutils.notebook.exit("PASS")  # noqa: F821
