# Copyright 2026 The MathWorks, Inc.

"""Functions related to diagnostics"""

import os
from importlib import metadata

import requests

from . import dbx, dsp, matlab, matlab_proxy, mpm, user, version

################################################
## Diagnostics Related
################################################


def get(username: str, dbx_context=None) -> str:
    """Return the full diagnostics output as a single string.

    Convenience wrapper around :func:`stream` for callers that do not
    need incremental output.

    Args:
        username: The OS user to run diagnostics for.
        dbx_context: A Databricks REPL context object. Passed through to
            :func:`stream` so that diagnostics can be run from widget
            callback threads where the REPL context is unavailable.

    Returns:
        str: The complete diagnostics output.
    """
    return "\n".join(stream(username, dbx_context=dbx_context))


def stream(username: str, dbx_context=None):
    """Generate diagnostics of the current environment line by line.

    Checks the following dependencies and yields each result as it
    becomes available so callers can stream output incrementally:

    - MATLAB
    - Databricks Runtime
    - MATLAB Proxy
    - Internet Connection

    It also yields the environment variables and installed Python packages.

    Args:
        username: The OS user to run diagnostics for.
        dbx_context: A Databricks REPL context object, captured on the main
            notebook thread. When ``None``, falls back to
            :func:`dbx.get_context`.

    Yields:
        str: A single line of diagnostics output.
    """
    if dbx_context is None:
        dbx_context = dbx.get_context()
    yield f"Notebook version: {version()}"

    if not user.exists(username=username):
        yield f"User {username} does not exist, running as root"
        username = "root"

    yield _get_matlab_info()
    yield _get_mpm_info(username=username)
    yield _get_databricks_info(dbx_context=dbx_context)
    yield _get_matlab_proxy_info(username=username)

    url = "https://mathworks.com"
    if check_internet_connection(url):
        yield f"Internet Connection OK: Connection to {url} succeeded"
    else:
        yield f"Internet Connection Failed: Connection to {url} failed"

    env_keys = [
        "DATABRICKS_ROOT_VIRTUALENV_ENV",
        "JAVA_HOME",
        "JUPYTER_WIDGETS_ECHO",
        "MATHWORKS_SERVICE_HOST_MANAGED_INSTALL_ROOT",
        "MW_CONTEXT_TAGS",
        "PYSPARK_PYTHON",
        "PYTHONPATH",
        "SPARK_SCALA_VERSION",
        "SCALA_VERSION",
    ]
    env_keys.extend(_get_mwi_environment_variable_keys())

    yield "************************"
    yield "MATLAB Interface for Databricks Environment Variables: "
    yield "************************"
    yield from _get_dsp_environment_variables(dbx_context=dbx_context)
    yield "************************"

    yield "Cluster Environment Variables: "
    yield "************************"
    yield from _get_environment_variables(env_keys)
    yield "************************"

    yield "Python Packages Installed: "
    yield "************************"
    yield from _get_installed_python_packages()
    yield "************************"


def _get_matlab_info() -> str:
    """
    Get the MATLAB related diagnostics information.
    Returns:
        str: The MATLAB diagnostics information.
    """
    try:
        matlab_root = matlab.root()
        matlab_version = matlab.version()
        if matlab_root and matlab_version:
            # Use the already-fetched local variables instead of calling again
            matlab_info = []
            matlab_info.append(f"MATLAB Installed: {matlab_root}")
            matlab_info.append(f"MATLAB Version: {matlab_version}")
            return "\n".join(matlab_info)
        else:
            return "MATLAB is not installed"
    except Exception:
        return "MATLAB is not installed"


def _get_mpm_info(username: str) -> str:
    """Returns the MATLAB Package Manager related diagnostics information."""
    return mpm.info(username=username)[1]


def _get_databricks_info(dbx_context) -> str:
    """
    Get the Databricks related diagnostics information including runtime version and data security mode.
    Returns:
        str: The Databricks diagnostics information.
    """
    databricks_info = []
    # Get the runtime version
    runtime_version = dbx.runtime_version()
    runtime_version_full = dbx_context.runtimeVersion
    min_major_version = 13
    min_minor_version = 3
    # Returns true if the runtime version is greater than or equal to the minimum required version
    is_valid = runtime_version[:2] >= [min_major_version, min_minor_version]
    if is_valid:
        databricks_info.append(f"Databricks Runtime Version: {runtime_version_full}")
    else:
        databricks_info.append(
            f"Unsupported Databricks Runtime Version: {runtime_version_full}. \nMinimum required version is {min_major_version}.{min_minor_version}"
        )
    # Get the data security mode
    try:
        data_security_mode = dbx.get_cluster_data_security_mode()
        if data_security_mode == "SINGLE_USER":
            # Only SINGLE_USER security mode is supported in our workflow, other modes STANDARD/USER_ISOLATION/SHARED are not supported.
            databricks_info.append(f"Data Security Mode: {data_security_mode}")
        else:
            databricks_info.append(
                f"Unsupported Data Security Mode: {data_security_mode}"
            )
    except Exception as e:
        databricks_info.append(f"Unable to determine Data Security Mode: {e}")
    return "\n".join(databricks_info)


def _get_matlab_proxy_info(username: str) -> str:
    """Returns MATLAB Proxy related information"""
    try:
        if _version := matlab_proxy.version(username=username):
            return f"MATLAB Proxy Version: {_version}"
        else:
            return "MATLAB Proxy not found"
    except Exception:
        return "MATLAB Proxy not found"


def check_internet_connection(url: str, timeout: float = 5) -> bool:
    """
    Check if the current environment has a valid connection to the specified URL.
    Args:
        url (str): The URL to check.
        timeout (float): The timeout in seconds for the connection attempt.
    Returns:
        bool: True if the environment is valid, False otherwise.
    """
    try:
        response = requests.head(url, timeout=timeout)
        # Check if the status code indicates success (e.g., 200-399 range)
        if response.status_code < 400:
            return True
        return False
    except Exception:
        return False


def _get_dsp_environment_variables(dbx_context) -> list[str]:
    """Return DSP environment variables for diagnostics output.

    Calls :func:`dsp.required_env_vars` with the provided Databricks
    context to obtain the exact values that are passed to MATLAB sessions.
    Sensitive keys (e.g. ``MW_API_TOKEN_B64``) are shown as ``REDACTED``.
    """
    redacted_keys = {"MW_API_TOKEN_B64"}

    try:
        env_vars = dsp.required_env_vars(dbx_context=dbx_context)
    except Exception:
        return ["DSP environment variables could not be resolved"]

    pairs = [
        (name, "REDACTED" if name in redacted_keys else value)
        for name, value in env_vars.items()
    ]
    pad = max((len(name) for name, _ in pairs), default=0)
    return [f"{name.ljust(pad)} = {value}" for name, value in pairs]


def _get_mwi_environment_variable_keys() -> list[str]:
    """Return all environment variable names that start with 'MWI', sorted.

    Returns:
        list[str]: Sorted list of env var names whose names begin with ``MWI``.
    """
    return sorted(key for key in os.environ if key.startswith("MWI"))


def _get_environment_variables(env_keys) -> list[str]:
    """Get the list of environment variables.
    Args:
        env_keys (list[str]): The list of environment variable names to read.

    Returns:
        list[str]: A list of strings in the form "name = value".
    """
    # Read each requested environment variable, defaulting to empty string if unset
    pairs = [(name, os.environ.get(name, "")) for name in env_keys]
    pad = max((len(name) for name, _ in pairs), default=0)
    envs = [f"{name.ljust(pad)} = {value}" for name, value in pairs]
    return envs


def _get_installed_python_packages() -> list[str]:
    """
    Get the list of installed Python packages.
    Returns:
        list[str]: A list of strings in the form "package == version".
    Example:
    ['matplotlib == 3.10.1', 'numpy == 1.26.4', 'pandas == 2.2.3', 'scipy == 1.13.1']
    """

    # Get all installed distributions
    python_packages = []
    packages = metadata.distributions()
    for dist in sorted(packages, key=lambda x: x.metadata["Name"].lower()):
        name = dist.metadata["Name"]
        version = dist.version
        python_packages.append(f"{name} == {version}")
    return python_packages
