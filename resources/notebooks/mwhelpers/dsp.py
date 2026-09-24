# Copyright 2026 The MathWorks, Inc.
"""Functions related to the MATLAB Interface for Databricks Support Package (DSP).

Provides helpers for extracting, locating, and initializing the DSP on a
Databricks cluster. Functions that accept a *username* argument raise
``ValueError`` when the value is empty.
"""

import base64
import os
import subprocess
import zipfile
from pathlib import Path

from . import user


def get_mwi_unzip_location(username: str) -> Path:
    """Return the directory where the DSP is extracted on the cluster.

    The path is ``/local_disk0/<username>/matlab-interface-for-databricks``.
    Content at this path indicates that some version of the DSP has already
    been extracted.

    Args:
        username: The OS user whose local-disk area is used.

    Returns:
        Path: The extraction directory.

    Raises:
        ValueError: If *username* is empty.
    """
    if not username:
        raise ValueError("Aborting, no username provided.")
    return Path(f"/local_disk0/{username}/matlab-interface-for-databricks")


def unzip(username: str, zip_file_path: str) -> bool:
    """Extract the DSP ZIP file to the user's extraction directory.

    The target directory is determined by :func:`get_mwi_unzip_location`.
    The OS user does not need to exist at extraction time; it must be
    created before MATLAB is started (via ``matlab -batch`` or
    ``matlab-proxy-app``).

    Args:
        username: The OS user whose local-disk area is used.
        zip_file_path: Path to the DSP ZIP file.

    Returns:
        bool: ``True`` if extraction succeeded, ``False`` otherwise.

    Raises:
        ValueError: If *username* or *zip_file_path* is empty.
    """

    if not username:
        raise ValueError("Aborting, no username provided.")
    if not zip_file_path:
        raise ValueError("Aborting, zipfile path not provided.")

    try:
        extract_to = get_mwi_unzip_location(username)
        # Create the OS user (and their local_disk0 directory) if they do not already exist.
        user.uid(username, create_if_not_exists=True)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        subprocess.run(["chown", "-R", username, str(extract_to)], check=True)
        return True
    except Exception as e:
        print(f"Error extracting support package: {e}")
        return False


def is_dsp_available(username: str) -> bool:
    """Check whether the DSP has been extracted on the cluster.

    Verifies that the extraction directory exists and contains the
    ``matlab-databricks/VERSION`` file.

    Args:
        username: The OS user whose local-disk area is checked.

    Returns:
        bool: ``True`` if the DSP is present and valid, ``False`` otherwise.

    Raises:
        ValueError: If *username* is empty.
    """
    if not username:
        raise ValueError("Aborting, no username provided.")
    dsp_path = get_mwi_unzip_location(username)
    return dsp_path.exists() and Path(f"{dsp_path}/matlab-databricks/VERSION").is_file()


def read_installed_version(username: str) -> str:
    """Read the version of the DSP currently installed on disk.

    Args:
        username: The OS user whose local-disk area is checked.

    Returns:
        str: The version string, or empty string if not installed or unreadable.
    """
    if not username:
        return ""
    version_file = get_mwi_unzip_location(username) / "matlab-databricks" / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return ""


def get_dsp_startup_options_env_var() -> str:
    """Return the name of the environment variable for DSP startup options.

    The variable (``DSP_STARTUP_OPTIONS``) supplies extra arguments to
    the ``onDatabricksSetup`` MATLAB function during session initialization.

    Returns:
        str: The environment variable name.
    """
    return "DSP_STARTUP_OPTIONS"


def get_dsp_startup_script(username: str) -> str:
    """Return MATLAB code that initializes the DSP for the current session.

    The generated code saves the current directory, ``cd``s to the
    ``onDatabricksSetup`` function's location, and calls it with the
    saved directory as ``startupFolder``. Additional options are appended
    from the ``DSP_STARTUP_OPTIONS`` environment variable when set.

    Args:
        username: The OS user whose extraction directory is used.

    Returns:
        str: A MATLAB statement string suitable for ``matlab -batch``.

    Raises:
        ValueError: If *username* is empty.
    """
    if not username:
        raise ValueError("Aborting, no username provided.")
    dsp_path = get_mwi_unzip_location(username)
    setup_function_path = f"{dsp_path}/matlab-databricks/Software/MATLAB/app/functions"

    # onDatabricksSetup takes multiple options as arguments.
    # These can be configured through an environment variable or through a config file in the future.
    options = os.getenv(get_dsp_startup_options_env_var(), "")
    options = f", {options}" if options else ""
    return f"startupFolder=pwd; cd {setup_function_path}; onDatabricksSetup(startupFolder=startupFolder {options})"


def read_version_from_zip(zip_file_path: Path) -> str:
    """Read the DSP version string from the ``matlab-databricks/VERSION`` file inside the ZIP.

    Args:
        zip_file_path: Path to the DSP ZIP file.

    Returns:
        str: The version string (UTF-8 decoded contents of the VERSION file).

    Raises:
        ValueError: If *zip_file_path* is empty.
        KeyError: If the VERSION file is not found in the archive.
        zipfile.BadZipFile: If the file is not a valid ZIP archive.
    """

    if not zip_file_path:
        raise ValueError("Aborting, zipfile path not provided.")

    version_file = "matlab-databricks/VERSION"
    with zipfile.ZipFile(zip_file_path, "r") as myzipfile:
        # Read the file's content into a bytes object
        file_contents_bytes = myzipfile.read(version_file)
        file_contents_str = file_contents_bytes.decode("utf-8")
        return file_contents_str


def _parse_semver(version_str: str) -> tuple[int, ...] | None:
    """Parse a semantic version string into a tuple of integers.

    Args:
        version_str: A version string like "1.2.3" or "6.1.5".

    Returns:
        A tuple of integers, or None if parsing fails.
    """
    try:
        return tuple(int(part) for part in version_str.split("."))
    except (ValueError, AttributeError):
        return None


def resolve_latest_dsp_from_interface_directory() -> tuple[str, str]:
    """Find the latest DSP zip file from the interface directory on Volumes.

    Reads the ``MW_INTERFACE_DIRECTORY_DEFAULT`` environment variable and
    looks for versioned zip files under ``<interface_dir>/Versions/<semver>/``.
    Each version subdirectory must contain exactly one ``.zip`` file.

    Returns:
        A tuple of (zip_path, error_message). On success, zip_path is the
        full path to the latest zip and error_message is empty. On failure,
        zip_path is empty and error_message describes the issue.
    """
    try:
        interface_dir = os.environ.get("MW_INTERFACE_DIRECTORY_DEFAULT", "")
        if not interface_dir:
            return ("", "")

        versions_dir = Path(interface_dir) / "Versions"
        if not versions_dir.is_dir():
            return (
                "",
                f"MW_INTERFACE_DIRECTORY_DEFAULT is set to '{interface_dir}' "
                f"but '{versions_dir}' directory does not exist.",
            )

        version_entries = []
        for entry in versions_dir.iterdir():
            if entry.is_dir():
                parsed = _parse_semver(entry.name)
                if parsed is not None:
                    version_entries.append((parsed, entry))

        if not version_entries:
            return ("", f"No valid version directories found in '{versions_dir}'.")

        # Sort by parsed semver, descending, and pick the latest
        version_entries.sort(key=lambda x: x[0], reverse=True)

        for parsed_ver, version_dir in version_entries:
            zip_files = list(version_dir.glob("*.zip"))
            if len(zip_files) == 1:
                return (str(zip_files[0]), "")
            elif len(zip_files) > 1:
                return (
                    "",
                    f"Multiple zip files found in '{version_dir}'. Expected exactly one.",
                )

        return (
            "",
            f"No zip files found in any version directory under '{versions_dir}'.",
        )
    except Exception as e:
        return ("", f"Error while resolving latest DSP: {e}")


def _should_auto_install(resolved_zip_path: str, installed_version: str) -> bool:
    """Decide whether to auto-install the DSP resolved from the interface directory.

    Auto-install should happen only when a package was resolved and its version
    differs from what is already installed.

    Args:
        resolved_zip_path: Path to the resolved DSP zip, or "" if none resolved.
        installed_version: The currently installed DSP version, or "" if none.

    Returns:
        bool: True if the resolved package should be installed, else False.
    """
    if not resolved_zip_path:
        return False
    try:
        resolved_version = read_version_from_zip(Path(resolved_zip_path)).strip()
    except Exception:
        return False
    return bool(resolved_version) and resolved_version != installed_version


def install_if_needed(username: str, resolved_zip_path: str) -> tuple[bool, str]:
    """Install the resolved DSP when it is newer than the installed version.

    Args:
        username: The OS user.
        resolved_zip_path: Path to the resolved DSP zip, or "" if none resolved.

    Returns:
        A tuple of (installed_newer, installed_version) where ``installed_newer``
        is ``True`` only when a newer version was successfully extracted, and
        ``installed_version`` is the installed DSP version after the operation
        (empty string if not installed).

    Raises:
        RuntimeError: If an install failed.
    """
    installed_version = read_installed_version(username=username)
    if not _should_auto_install(resolved_zip_path, installed_version):
        return (False, installed_version)

    if not unzip(username=username, zip_file_path=resolved_zip_path):
        raise RuntimeError("Failed to extract the MATLAB Interface for Databricks.")

    installed_version = read_installed_version(username=username)
    if not installed_version:
        raise RuntimeError(
            "MATLAB Interface for Databricks was extracted but no version was found."
        )
    return (True, installed_version)


def required_env_vars(dbx_context) -> dict[str, str]:
    """Return the environment variables required by the DSP at runtime.

    Uses the supplied Databricks context to populate:

    - ``MW_ORG_ID`` — the workspace ID.
    - ``MW_HOST`` — the workspace URL (prefixed with ``https://``).
    - ``MW_CLUSTER_ID`` — the cluster ID.
    - ``MW_API_URL`` — the Databricks API URL.
    - ``MW_API_TOKEN_B64`` — the API token, base64-encoded.
    - ``MW_DBX_USERNAME`` — the Databricks user name.

    Args:
        dbx_context: A Databricks REPL context object. Required because
            the REPL context is only available on the main notebook thread
            and cannot be obtained from widget callback threads.

    Returns:
        dict[str, str]: A mapping of environment variable names to their values.
    """
    if dbx_context is None:
        raise ValueError("Databricks Context must be passed in.")
    dsp_envs = {
        "MW_ORG_ID": dbx_context.workspaceId,
        "MW_HOST": f"https://{dbx_context.workspaceUrl}",
        "MW_CLUSTER_ID": dbx_context.clusterId,
        "MW_API_URL": dbx_context.apiUrl,
        "MW_API_TOKEN_B64": base64.b64encode(
            dbx_context.apiToken.encode("utf-8")
        ).decode("utf-8"),
        "MW_DBX_USERNAME": dbx_context.user,
        "SPARK_CONNECT_MODE_ENABLED": "1",
    }
    return dsp_envs
