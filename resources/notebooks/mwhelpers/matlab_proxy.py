# Copyright 2026 The MathWorks, Inc.

import os
import threading
from typing import Optional
from urllib.parse import urlparse, urlunparse

from . import dbx, dsp, subprocess_shim, user, web


def version(username: str) -> Optional[str]:
    """
    Returns the output of calling "matlab-proxy-app --version" as the specified user.
    """

    _env = os.environ.copy()
    output = subprocess_shim.run(
        uid=user.uid(username),
        command=["matlab-proxy-app", "--version"],
        env=_env,
    )

    if output.returncode != 0:
        return None

    if _version := output.stdout.strip():
        return _version
    else:
        return None


def _list_servers(username: str) -> dict[str, str]:
    """This function looks at the file system & not the process tree to find the running matlab-proxy servers."""
    if not username:
        return {}

    try:
        home_folder = str(user.home_folder(username))
    except RuntimeError:
        #  User does not exist, this function does not create the user
        #  because this function can be called before any MATLAB sessions are ever started with a user.
        return {}

    envs = os.environ.copy()

    # This environment variable is used by the matlab-proxy-app-list-servers command to find the running servers for the user.
    envs.update({"HOME": home_folder})
    output = subprocess_shim.run(
        uid=user.uid(username),
        command=["matlab-proxy-app-list-servers", "--quiet"],
        env=envs,
    )
    if output and output.returncode == 0:
        running_servers = output.stdout.strip().splitlines()
        parsed_servers = [urlparse(server) for server in running_servers]
        server_dict = {
            str(server.port): str(urlunparse(server))
            for server in parsed_servers
            if server.port
        }
        return server_dict
    else:
        return {}


def list_servers_ports(username: str) -> list[str]:
    return list(_list_servers(username).keys())


def list_servers_with_idle_timeout(username: str) -> list[str]:
    """List running matlab-proxy servers for the user that have idle timeout configured."""

    servers = _list_servers(username=username)
    servers_with_timeout = []
    if servers:
        for server_url in servers.values():
            env_config_url = server_url + "/get_env_config"
            response = web.send_http_request(env_config_url, method="GET")
            if response and response.status_code == 200:
                config = response.json()
                if config.get("idleTimeoutDuration"):
                    servers_with_timeout.append(server_url)
    return servers_with_timeout


def _prepare_mwi_matlab_startup_script(
    username: str, mwi_matlab_startup_script: str
) -> str:
    """Build the full MATLAB startup script for a matlab-proxy session.

    Prepends ``cd(userpath)`` so that MATLAB starts in the user's path
    (created by ``CreateUser.sh``).  When the Databricks Support Package
    (DSP) is available, DSP initialization commands are appended next.
    Finally, any caller-supplied startup script is appended.

    Args:
        username: OS username whose DSP availability is checked.
        mwi_matlab_startup_script: Additional MATLAB commands supplied
            via the ``MWI_MATLAB_STARTUP_SCRIPT`` environment variable.

    Returns:
        A semicolon-separated MATLAB command string.
    """
    # Change directory to userpath, created in CreateUser.sh
    startup_script = "cd(userpath); "
    if dsp.is_dsp_available(username):
        startup_script += dsp.get_dsp_startup_script(username) + "; "
    startup_script += mwi_matlab_startup_script

    return startup_script


def start(
    username: str,
    env: dict[str, str] | None = None,
    dbx_context=None,
) -> str:
    """Start a MATLAB Desktop session using matlab-proxy.

    Args:
        username (str): The OS username to run the session as.
        env (dict): Additional environment variables to be set for the matlab-proxy instance.
        dbx_context: A Databricks REPL context object, captured on the main
            notebook thread. Passed through to :func:`dsp.required_env_vars`
            so that DSP environment variables can be resolved from widget
            callback threads where the REPL context is unavailable.

    Returns:
        str: The port number of the started session as a string, or empty string on failure.
             Returns str (not int) because the port is used as an opaque session identifier
             throughout the notebook UI (displayed in buttons, stored in lists, etc.).
    """
    if not username:
        print("No username provided, aborting...")
        return ""

    # Avoid mutable default argument — a shared default {} would persist
    # mutations across calls, causing subtle bugs.
    if env is None:
        env = {}

    home_folder = user.home_folder(username, create_if_not_exists=True)
    uid = user.uid(username)

    port = dbx.find_next_open_port()
    if port is None:
        print("No ports available, aborting...")
        return ""

    session_env = os.environ.copy()
    session_env["HOME"] = str(home_folder)
    session_env["USER"] = username
    session_env["MWI_APP_PORT"] = str(port)
    session_env["MWI_ENABLE_TOKEN_AUTH"] = "False"
    session_env["MWI_USE_COOKIE_CACHE"] = "True"
    session_env["MWI_BASE_URL"] = "/matlab"

    startup_script = _prepare_mwi_matlab_startup_script(
        username=username,
        mwi_matlab_startup_script=session_env.get("MWI_MATLAB_STARTUP_SCRIPT", ""),
    )
    session_env["MWI_MATLAB_STARTUP_SCRIPT"] = startup_script

    # DSP env vars are always set, this enables manual installation even after MATLAB starts
    session_env.update(dsp.required_env_vars(dbx_context=dbx_context))
    # Additional variables passed in take highest precedence, overwriting any existing values.
    session_env.update(env)

    # Run the command as the specified user
    subprocess_shim.spawn(command=["matlab-proxy-app"], uid=uid, env=session_env)

    # Starting a MATLAB session with idle timeout configured immediately triggers a keep-alive
    # command, which resets the cluster's idle timer. This eliminates a race condition where
    # the cluster could auto-terminate before the periodic keep-alive loop starts monitoring,
    # ensuring a more stable user experience.
    if "MWI_SHUTDOWN_ON_IDLE_TIMEOUT" in env:
        try:
            threading.Thread(
                target=dbx.run_keep_alive_command,
                kwargs={"cluster_id": dbx_context.clusterId},
            ).start()
        except Exception as e:
            print(
                "Warning: MATLAB session started, but the keep-alive could not "
                f"be initialized ({e}). The cluster may auto-terminate on idle."
            )

    return str(port)


def stop(username: str, port: int, context=None):
    """Stop a MATLAB session running for the specified user and port."""
    if context and context.isInJob:
        print("Running inside a job, aborting...")
        return False
    if port is None:
        print("No port provided, aborting...")
        return False
    if username is None:
        print("No username provided, aborting...")
        return False

    servers = _list_servers(username=username)
    # Get the server URL for the given port
    if not servers:
        print(f"No servers found for {username}, aborting...")
        return False
    server_url = servers.get(str(port), None)

    # Find the URL to the session
    if server_url is None:
        print(f"No server found with port {port}, aborting...")
        return False

    # Send a DELETE request to the SHUTDOWN_INTEGRATION endpoint
    shutdown_url = server_url + "/shutdown_integration"
    print(f"Stopping MATLAB session with ID: {port}")
    print(f"Sending shutdown request to URL: {shutdown_url}")

    web.send_http_request(shutdown_url, method="DELETE")
    return True
