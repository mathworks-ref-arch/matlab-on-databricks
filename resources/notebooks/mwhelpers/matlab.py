# Copyright 2026 The MathWorks, Inc.

"""Functions related to MATLAB"""

import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from . import dsp, subprocess_shim, user


def root() -> str:
    """Get the root directory of MATLAB.

    Returns:
        str: The root directory of MATLAB.
             Returns empty string if MATLAB is not on PATH.
    """
    resolved_path = ""
    try:
        matlab_exe_on_path = shutil.which("matlab")
        if matlab_exe_on_path is None:
            # We could either throw an exception or return an empty string.
            # Returning an empty string enables the UI to render in cases where the MATLAB is not on PATH.
            return ""

        resolved_path = str(Path(matlab_exe_on_path).resolve())

        if resolved_path.endswith("/bin/matlab"):
            resolved_path = resolved_path.replace("/bin/matlab", "")
    except Exception as e:
        print(f"Error while resolving MATLAB root path: {e}")

    return resolved_path


def version() -> str:
    """Get the version of MATLAB by reading VersionInfo.xml from the MATLAB root.

    Returns:
        str: The MATLAB version string (e.g. "R2025a Update 1 (25.1.0.2973910)"),
            or "Unknown" if the version cannot be determined.
    """
    try:
        matlabroot = root()
        if not matlabroot:
            return "Unknown"
        tree = ET.parse(Path(matlabroot) / "VersionInfo.xml")
        root_el = tree.getroot()
        release = root_el.findtext("release", "")
        description = root_el.findtext("description", "")
        ver = root_el.findtext("version", "")
        parts = [release]
        if description:
            parts.append(description)
        if ver:
            parts.append(f"({ver})")
        return " ".join(parts)
    except Exception as e:
        print(f"Error getting MATLAB version: {str(e)}")
        return "Unknown"


def _list_installed_products(matlabroot: str) -> list[str]:
    """List installed MATLAB products by scanning ``Contents.m`` files.

    Mimics the algorithm used by the MATLAB ``ver`` command: finds
    ``Contents.m`` files under ``<matlabroot>/toolbox``, reads the first
    two lines, and extracts the product name when the second line starts
    with ``% Version``.  Directories named ``toolbox/local``,
    ``toolbox/matlab``, ``mcr/``, and paths containing ``+`` or ``@``
    are excluded.  ``MATLAB`` is always listed first if present.

    Args:
        matlabroot: The MATLAB root directory.

    Returns:
        list[str]: Sorted list of unique product names with MATLAB first.
    """
    toolbox_dir = Path(matlabroot) / "toolbox"
    if not toolbox_dir.is_dir():
        return []

    exclude_prefixes = (
        str(toolbox_dir / "local") + os.sep,
        str(toolbox_dir / "matlab") + os.sep,
    )
    mcr_prefix = str(Path(matlabroot) / "mcr") + os.sep

    has_matlab = (toolbox_dir / "matlab" / "general" / "Contents.m").is_file()
    products = set()

    for contents_file in toolbox_dir.rglob("Contents.m"):
        path_str = str(contents_file)
        if path_str.startswith(exclude_prefixes) or path_str.startswith(mcr_prefix):
            continue
        if any(
            part.startswith("+") or part.startswith("@") for part in contents_file.parts
        ):
            continue
        try:
            with open(contents_file, "r", encoding="utf-8", errors="replace") as f:
                first_line = f.readline()
                second_line = f.readline()
            if second_line.startswith("% Version"):
                name = first_line.lstrip("% ").strip()
                if name:
                    products.add(name)
        except OSError:
            continue

    result = sorted(products)
    if has_matlab:
        result.insert(0, "MATLAB")
    return result


def installed_toolboxes(username: str) -> list[str]:
    """Get the list of installed toolboxes in MATLAB.

    Scans ``Contents.m`` files under the MATLAB root directory and
    appends "Databricks Support Package" if it is available for the
    given user.

    Args:
        username: The user to check DSP availability for.

    Returns:
        list[str]: List of installed toolbox names, or an empty list on failure.

    Raises:
        ValueError: If username is empty.
    """
    if not username:
        raise ValueError("Username is required to get installed toolboxes")

    try:
        matlabroot = root()
        if not matlabroot:
            return []
        installed_products = _list_installed_products(matlabroot)
        if dsp.is_dsp_available(username):
            installed_products.append("Databricks Support Package")
        return installed_products
    except Exception as e:
        print(f"{str(e)}")
        return []


def run_code_with_matlab_batch(
    username: str, code: str, env: dict[str, str] = {}, license_server_address: str = ""
) -> tuple[bool, str]:
    """Run MATLAB code via ``matlab -batch`` as the specified user.

    Creates the user if it does not already exist, resolves the license
    server address (explicit argument takes precedence over the
    ``MLM_LICENSE_FILE`` environment variable), and executes the code.

    Args:
        username: OS user to run the MATLAB process as.
        code: MATLAB code to execute.
        env: Optional environment variable dict. If empty, ``os.environ``
            is used.
        license_server_address: Optional license server address
            (e.g. ``"port@host"``). Overrides ``MLM_LICENSE_FILE`` in the
            environment when provided.

    Returns:
        tuple[bool, str]: ``(True, stdout)`` on success (return code 0),
            or ``(False, stderr)`` on failure.

    Raises:
        ValueError: If *username* or *code* is empty, or if no license
            information is available.
    """

    if not username:
        raise ValueError("Username cannot be empty.")
    if not code:
        raise ValueError("No code to run provided.")

    # Create the user if it does not exist, as the installation process requires a valid user to run the MATLAB session and install the support package.
    user.uid(username, create_if_not_exists=True)

    _env = env if env else os.environ.copy()

    # explicitly provided license server address takes precedence over environment variable
    _env["MLM_LICENSE_FILE"] = (
        license_server_address
        if license_server_address
        else _env.get("MLM_LICENSE_FILE", "")
    )

    if not _env["MLM_LICENSE_FILE"]:
        raise ValueError(
            "This function requires licensing information either through the license_server_address argument, or the MLM_LICENSE_FILE environment variable"
        )

    command = f"matlab -batch '{code}'"
    print(f"Starting MATLAB as user: {username}")
    output = subprocess_shim.run_runuser(
        command=command,
        username=username,
        env=_env,
        whitelist_env_vars="MLM_LICENSE_FILE,PYSPARK_PYTHON",
    )
    if output and output.returncode == 0:
        print(f"MATLAB execution completed successfully with output:\n {output.stdout}")
        return (True, output.stdout)
    else:
        print(
            f"MATLAB installation failed with return code {output.returncode}. \n stdout: {output.stdout} \n stderr: {output.stderr}"
        )
        return (False, output.stderr)
