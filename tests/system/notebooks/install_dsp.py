# Databricks notebook source
# Copyright 2026 The MathWorks, Inc.

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 2: Install DSP Support Package
# MAGIC
# MAGIC Downloads the DSP from MathWorks and extracts it using mwhelpers.

# COMMAND ----------

import os
from pathlib import Path

from mwhelpers import dsp, web

# COMMAND ----------

USERNAME = os.environ["MW_TEST_USERNAME"]

DSP_DOWNLOAD_URL = "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/products/reference-architectures/matlab-databricks-latest.zip"

# COMMAND ----------

# Download DSP zip from MathWorks
zip_path = web.download_file(
    DSP_DOWNLOAD_URL, save_path="/tmp/matlab-databricks-latest.zip"
)
assert zip_path, f"Failed to download DSP from {DSP_DOWNLOAD_URL}"
print(f"DSP zip downloaded to: {zip_path}")

# COMMAND ----------

# Read version from zip
version = dsp.read_version_from_zip(Path(zip_path))
print(f"DSP version: {version}")

# COMMAND ----------

# Extract DSP using mwhelpers
success = dsp.unzip(USERNAME, zip_path)
assert success, f"Failed to extract DSP from {zip_path}"

# Verify installation
assert dsp.is_dsp_available(USERNAME), "DSP not available after extraction"
installed_version = dsp.read_installed_version(USERNAME)
print(f"DSP installed version: {installed_version}")

# COMMAND ----------

# Verify startup script can be generated
startup_script = dsp.get_dsp_startup_script(USERNAME)
assert "onDatabricksSetup" in startup_script
print(f"DSP startup script: {startup_script}")

# COMMAND ----------

print("DSP installation PASSED")
dbutils.notebook.exit("PASS")  # noqa: F821
