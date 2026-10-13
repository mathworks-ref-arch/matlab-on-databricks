# Copyright 2026 The MathWorks, Inc.
#
# Makefile for MATLAB on Databricks system tests.
#
# Assumes the Docker image already exists in a container registry.
#
# Bundle variables are passed via environment using the BUNDLE_VAR_<name> convention.
# The Databricks CLI automatically maps these to bundle variables.
#
# Required:
#   BUNDLE_VAR_docker_image       - full image URL (e.g., ghcr.io/org/repo/matlab:R2026b-17.3)
#   BUNDLE_VAR_docker_username    - username for pull authentication (e.g., github.actor)
#   BUNDLE_VAR_docker_password    - token for pull authentication (e.g., GITHUB_TOKEN)
#
# Optional:
#   BUNDLE_VAR_matlab_release     - defaults to R2026b (in databricks.yml)
#   BUNDLE_VAR_databricks_runtime - defaults to 17.3 (in databricks.yml)
#   BUNDLE_VAR_node_type_id       - defaults to Standard_DS3_v2 for Azure (in databricks.yml)
#   BUNDLE_VAR_run_id             - unique identifier for this deployment (e.g., CI run ID)
#   MATLAB_LICENSE                - MATLAB license file content (for upload-license target)
#
# Usage:
#   make all              - Full pipeline: deploy, test, destroy
#                           (upload-license is separate; it needs MATLAB_LICENSE)
#   make upload-license   - Upload MATLAB license to Databricks secrets
#   make deploy           - Deploy DAB bundle (creates job + cluster)
#   make test             - Run verification job on Databricks
#   make destroy          - Tear down all DAB resources
#   make clean            - Remove generated files

.PHONY: all deploy test destroy upload-license check-env sync-mwhelpers clean

SHELL := /bin/bash

REPO_ROOT := $(shell cd ../.. && pwd)

# --- Full pipeline ---

all: deploy test destroy

# --- Infrastructure targets ---

deploy: check-env sync-mwhelpers
	@echo "=== Deploying DAB bundle ==="
	@databricks bundle deploy -t ci
	@echo "=== Bundle deployed ==="

destroy: check-env
	@echo "=== Destroying DAB bundle ==="
	@databricks bundle destroy -t ci --auto-approve
	@echo "=== Bundle destroyed ==="

# --- Test target ---

test: check-env
	@echo "=== Running verification job ==="
	@databricks bundle run -t ci system_test

# --- License ---

upload-license:
ifndef MATLAB_LICENSE
	$(error MATLAB_LICENSE is not set)
endif
	@echo "=== Uploading MATLAB license to Databricks secrets ==="
	@printenv MATLAB_LICENSE | databricks secrets put-secret matlab license
	@echo "=== License uploaded ==="

# --- Utilities ---

sync-mwhelpers:
	@echo "=== Copying mwhelpers into notebooks/ ==="
	rm -rf notebooks/mwhelpers
	cp -r $(REPO_ROOT)/resources/notebooks/mwhelpers notebooks/mwhelpers

check-env:
ifndef BUNDLE_VAR_docker_image
	$(error BUNDLE_VAR_docker_image is not set)
endif
ifndef BUNDLE_VAR_docker_username
	$(error BUNDLE_VAR_docker_username is not set)
endif
ifndef BUNDLE_VAR_docker_password
	$(error BUNDLE_VAR_docker_password is not set)
endif

clean:
	rm -rf notebooks/mwhelpers
