# Copyright 2026 The MathWorks, Inc.

import logging
import os
from contextlib import contextmanager

import docker
import helper
import pytest
import testinfra

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """
    Register custom command-line options for pytest.

    These options allow specifying the Docker image, MATLAB release, and
    Databricks runtime version to be used during testing.
    """
    parser.addoption(
        "--image-name",
        action="store",
        default=None,
        help="Docker image to test (e.g., 'matlab-on-databricks:R2025b-16.4'). Overrides IMAGE_NAME env var.",
    )
    parser.addoption(
        "--matlab-release",
        action="store",
        default=None,
        help="MATLAB release version to test (e.g., 'R2025b'). Overrides MATLAB_RELEASE env var.",
    )
    parser.addoption(
        "--db-runtime",
        action="store",
        default=None,
        help="Databricks runtime version to test (e.g., '16.4'). Overrides DB_RUNTIME env var.",
    )
    parser.addoption(
        "--matlab-update",
        action="store",
        default=None,
        help="MATLAB update level to test (e.g., 'U7'). Overrides MATLAB_UPDATE env var.",
    )


def _get_config_value(request, option_name, env_var_name):
    """
    Helper function to retrieve configuration values.

    Prioritizes command-line arguments over environment variables.
    Fails the test if neither is provided.

    Args:
        request: The pytest request object.
        option_name (str): The name of the command-line option (without '--').
        env_var_name (str): The name of the environment variable.

    Returns:
        str: The configuration value.
    """
    value = request.config.getoption(f"--{option_name}")
    if value:
        logger.info(f"Configuration '{option_name}' loaded from CLI argument: {value}")
        return value
    value = os.environ.get(env_var_name)
    if value:
        logger.info(
            f"Configuration '{option_name}' loaded from environment variable {env_var_name}: {value}"
        )
        return value

    error_msg = f"Missing configuration. Provide either --{option_name} or set {env_var_name} environment variable."
    logger.error(error_msg)
    pytest.fail(error_msg)


@pytest.fixture(scope="session")
def image_name(request):
    """
    Fixture to get the Docker image name to test.
    """
    return _get_config_value(request, "image-name", "IMAGE_NAME")


@pytest.fixture(scope="session")
def matlab_release(request):
    """
    Fixture to get the MATLAB release version.
    """
    return _get_config_value(request, "matlab-release", "MATLAB_RELEASE")


@pytest.fixture(scope="session")
def databricks_runtime(request):
    """
    Fixture to get the Databricks runtime version.
    """
    return _get_config_value(request, "db-runtime", "DB_RUNTIME")


@pytest.fixture(scope="session")
def matlab_update(request):
    """
    Fixture to get the MATLAB update level (e.g., 'U7').

    Returns None if neither the CLI option nor the environment variable is set,
    allowing tests to skip when no update level is specified.
    """
    value = request.config.getoption("--matlab-update")
    if value:
        return value
    return os.environ.get("MATLAB_UPDATE")


@pytest.fixture(scope="session")
def license_file(tmp_path_factory):
    """
    Fixture to create a temporary license file from an environment variable.

    Reads the license content from 'MATLAB_LICENSE_FILE' env var and writes it
    to a temporary file. This file path is then returned for use in tests
    """
    logger.info("Setting up temporary license file...")
    license_string = os.environ.get("MATLAB_LICENSE_FILE")
    if not license_string:
        error_msg = "Missing license. Set MATLAB_LICENSE_FILE environment variable to license content."
        logger.error(error_msg)
        pytest.fail(error_msg)
    # Create temp directory for license
    license_dir = tmp_path_factory.mktemp("license")
    license_path = license_dir / "license.lic"
    license_path.write_text(license_string)
    logger.info(f"License file written to: {license_path}")
    return str(license_path)


@pytest.fixture(scope="session")
def databricks_python_path():
    """
    Fixture providing the standard path to the Python executable in Databricks containers.
    """
    return "/databricks/python3/bin"


@pytest.fixture(scope="session")
def docker_client():
    """
    Fixture to provide a Docker client instance.

    Ensures the client is properly closed after the test session.
    """
    client = docker.from_env()
    yield client
    client.close()


@pytest.fixture(scope="session")
def container_factory(docker_client):
    """
    Fixture that returns a context manager for running Docker containers.

    Usage:
        with container_factory(image="my-image", command="...") as container:
            # run tests against container
    """

    @contextmanager
    def _run_container(**kwargs):
        # Default to detach=True to run container in the background
        kwargs.setdefault("detach", True)

        logger.info(f"Starting container with configuration: {kwargs}")
        container = docker_client.containers.run(**kwargs)
        logger.info(f"Container started successfully with ID: {container.id}")

        try:
            yield container
        finally:
            try:
                logger.info(f"Stopping container with ID: {container.id}...")
                container.stop()
            except Exception:
                logger.warning(f"Failed to stop container with ID: {container.id}")

            try:
                logger.info(f"Removing container with ID: {container.id}...")
                container.remove(force=True)
            except Exception:
                logger.warning(f"Failed to remove container with ID: {container.id}")
            logger.info("Container cleanup complete")

    return _run_container


@pytest.fixture(scope="class")
def docker_host(
    request,
    image_name,
    container_factory,
):
    """
    Fixture that provisions a Docker container and returns a testinfra host.

    This fixture processes configuration parameters (via request.param) to
    set up volumes, environment variables, and specific flags like licensing
    or release versioning before starting the container.

    Yields:
        host (testinfra.host.Host): A handle to the running container.
    """
    cfg = getattr(request, "param", {}).copy()

    # Process special flags
    licensed = cfg.pop("licensed", False)
    set_release = cfg.pop("set_release", False)
    wait_for = cfg.pop("wait_for", None)

    # Build volumes/environment from flags
    volumes = {}
    environment = {}

    # Mount license if license flag is set
    if licensed:
        license_file_path = request.getfixturevalue("license_file")
        volumes[license_file_path] = {"bind": "/licenses/license.dat", "mode": "ro"}
        environment["MLM_LICENSE_FILE"] = "/licenses/license.dat"

    # Set MATLAB_RELEASE if release flag is set
    if set_release:
        release = request.getfixturevalue("matlab_release")
        environment["MATLAB_RELEASE"] = release

    volumes.update(cfg.pop("volumes", {}))
    environment.update(cfg.pop("environment", {}))

    container_config = {
        "image": image_name,
        "volumes": volumes or None,
        "environment": environment or None,
        **cfg,
    }
    # Remove None values
    container_config = {k: v for k, v in container_config.items() if v is not None}

    with container_factory(**container_config) as container:
        host = testinfra.get_host(f"docker://{container.id}")
        if wait_for:
            helper.wait_for_process(host, wait_for)
        yield host
