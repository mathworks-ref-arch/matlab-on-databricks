# Copyright 2026 The MathWorks, Inc.

import logging
import os
import socket
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute
from dbruntime.databricks_repl_context import get_context as get_databricks_context

from . import matlab_proxy, sanitize_url, user


class DatabricksExecutionContext:
    def __init__(
        self,
        cluster_id: str,
        lang=compute.Language.PYTHON,
        workspace_client: WorkspaceClient | None = None,
    ):
        self.workspace_client = workspace_client or WorkspaceClient()
        self.cluster_id = cluster_id
        self.lang = lang
        self.execution_ctx_id = None

    def __enter__(self):
        # Creates an execution context for the cluster and language specified.
        response = self.workspace_client.command_execution.create(
            cluster_id=self.cluster_id, language=self.lang
        ).result()
        self.execution_ctx_id = response.id
        return self

    def run_print_command(self, message):
        timestamp = datetime.now().isoformat()
        code = f"print({f'[{timestamp}] {message}'!r})"
        # Databricks terminates idle compute based on the last command run on it
        # (https://docs.databricks.com/aws/en/compute/clusters-manage#automatic-termination).
        # Running a command through the Command Execution API resets that timer.
        response = self.workspace_client.command_execution.execute(
            cluster_id=self.cluster_id,
            context_id=self.execution_ctx_id,
            command=code,
            language=self.lang,
        ).result()

        return response.status

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup the execution context.
        if self.execution_ctx_id:
            self.workspace_client.command_execution.destroy(
                cluster_id=self.cluster_id, context_id=self.execution_ctx_id
            )


################################################
## Databricks Related APIs
################################################
def get_context():
    return get_databricks_context()


def get_cluster_id():
    context = get_context()
    return context.clusterId


def get_cluster_name():
    context = get_context()
    if context.isInJob:
        return "Job Cluster"
    else:
        cluster_name = (
            WorkspaceClient(host=context.browserHostName, token=context.apiToken)
            .clusters.get(context.clusterId)
            .cluster_name
        )
        return cluster_name


def get_cluster_data_security_mode() -> str:
    context = get_context()
    data_security_mode = (
        WorkspaceClient(host=context.browserHostName, token=context.apiToken)
        .clusters.get(context.clusterId)
        .data_security_mode
    )
    return data_security_mode.value


def cluster_autotermination_minutes() -> int:
    """Get the cluster auto-termination minutes.

    Returns:
        int: The auto-termination minutes.(0 if autotermination is disabled)
    """
    context = get_context()
    if context.isInJob:
        return 0  # Assuming autotermination is disabled for job clusters.
    else:
        cluster_info = WorkspaceClient(
            host=context.browserHostName, token=context.apiToken
        ).clusters.get(context.clusterId)
        return cluster_info.autotermination_minutes


def current_user_name() -> str:
    """Return the Linux username for the current Databricks user."""
    return user.to_valid_linux_username(get_context().user)


def runtime_version() -> list[int]:
    """
    Gets the major.minor version of the Databricks runtime.
    Note: This function needs to be updated if Databricks changes the formatting of their Runtime Versions.
    Example:
    "16.4.x-scala2.13" -> [16, 4, 0]
    Serverless: "client.1.13-scala2.12" -> [0, 1, 13]

    Returns:
        version: A list containing the version information in the form [major, minor, patch]
    """
    version = [0] * 3
    full_runtime_version = get_context().runtimeVersion
    if not full_runtime_version:
        return version
    runtime_version = full_runtime_version.split("-").pop(0).split(".")
    for i in range(3):
        if runtime_version[i].isdigit():
            version[i] = int(runtime_version[i])
    return version


def _reserved_ports() -> list:
    """Get the list of ports that are reserved by Databricks and cannot be used for MATLAB Proxy."""
    # As of now, there is no public API to get the list of reserved ports from Databricks.
    # This is a hardcoded list based on the documentation at https://docs.databricks.com/aws/en/compute/#reserved-ports.
    return [
        1023,
        6059,
        6060,
        6061,
        6062,
        7071,
        7077,
        10000,
        15001,
        15002,
        36423,
        38841,
        39909,
        40000,
        40001,
        41063,
    ]


def find_next_open_port():
    """Find the next open port in the specified range.

    Databricks only proxies ports in the range 3000-9999.

    Note: There is an inherent TOCTOU (time-of-check-time-of-use) race condition here.
    The port is verified as free and then returned, but another process could claim it
    before matlab-proxy-app binds to it. This is acceptable because port collisions are
    rare on single-user clusters and matlab-proxy-app will fail fast if the port is taken.
    """
    host = "0.0.0.0"
    start_port: int = 3000
    end_port: int = 9999
    reserved_ports = _reserved_ports()
    for port in range(start_port, end_port + 1):
        if port in reserved_ports:
            continue
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attempt
        result = sock.connect_ex((host, port))
        if result != 0:  # 0 means the port is open
            sock.close()
            return port

    return None


def get_url_to_matlab(session_id: int, databricks_context) -> str:
    """Get the Driver Proxy URL to the MATLAB session."""

    if not session_id:
        raise ValueError("Session ID is required to get the URL to MATLAB session.")

    if databricks_context.isInJob:
        raise RuntimeError("Running inside a job, aborting...")

    else:
        workspace_url = f"https://{databricks_context.browserHostName}"
        workspace_id = databricks_context.workspaceId
        cluster_id = databricks_context.clusterId

        cluster_url = f"{workspace_url}/driver-proxy/o/{workspace_id}/{cluster_id}/"
        template_url = cluster_url + "{{port}}/{{base_url}}/index.html"

        assumed_base_url = "matlab"
        url = template_url.replace("{{port}}", str(session_id)).replace(
            "{{base_url}}", assumed_base_url
        )
        return sanitize_url(url)


def _get_keep_alive_logger(cluster_id: str) -> logging.Logger:
    """Return a logger that writes to a file in the mwhelpers/keep_alive_logs directory.

    The directory is in the workspace, where it is shared by every cluster that runs
    the notebook, so each cluster writes to its own file to avoid concurrent writers.
    A restarted cluster keeps its ID and so appends to its existing file.

    Logging is disabled by default. Set the environment variable
    ``MWI_ENABLE_MATLAB_KEEP_ALIVE_LOGGING=true`` to enable keep-alive logging.
    """
    logger = logging.getLogger("matlab-keep-alive")
    if (
        os.environ.get("MWI_ENABLE_MATLAB_KEEP_ALIVE_LOGGING", "false").lower()
        == "false"
    ):
        logger.disabled = True
        return logger
    if not logger.handlers:
        log_dir = Path(__file__).parent / "keep_alive_logs"
        log_dir.mkdir(exist_ok=True)
        handler = logging.FileHandler(log_dir / f"keep_alive_{cluster_id}.log")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def run_keep_alive_command(
    cluster_id: str,
    workspace_client: WorkspaceClient | None = None,
    active_sessions: str = "",
):
    """Run a keep-alive command on the cluster to prevent auto-termination.

    Executes a simple print command on the specified Databricks cluster to reset its
    idle timeout timer. Logs the command status or any errors encountered.

    Args:
        cluster_id: The ID of the Databricks cluster to keep alive.
        workspace_client: Client to run the command with. Defaults to a client using the
            SDK's default auth, which only works while the REPL context is available.
        active_sessions: Active MATLAB sessions as ``user:port`` pairs, printed in the
            driver logs by the keep-alive command.
    """
    if not cluster_id:
        raise ValueError("Cluster ID is required to run keep-alive command.")

    logger = _get_keep_alive_logger(cluster_id)
    try:
        with DatabricksExecutionContext(
            cluster_id=cluster_id, workspace_client=workspace_client
        ) as context:
            command_status = context.run_print_command(
                message=f"MATLAB sessions: {active_sessions}"
            )
            # Both the periodic check and matlab_proxy.start() send keep-alives through
            # here, so name the sessions to tell them apart in the log.
            logger.info(
                f"Command status: {command_status} (sessions: {active_sessions})"
            )
    except Exception as e:
        logger.error(f"Error running execution command: {e}")


def _active_sessions(servers_by_user: dict[str, list[str]]) -> str:
    """Describe the active MATLAB sessions as ``user:port`` pairs.

    For example, ``alice:31515, bob:31516``. Users without sessions are left out.
    """
    return ", ".join(
        f"{username}:{urlparse(server).port}"
        for username, servers in servers_by_user.items()
        for server in servers
    )


def _keep_alive_tick(
    cluster_id: str, workspace_client: WorkspaceClient, logger: logging.Logger
):
    """Send a keep-alive command if any MATLAB user has a session with idle timeout."""
    servers_by_user = matlab_proxy.list_servers_with_idle_timeout_by_user(logger)
    summary = "; ".join(
        f"{username}: {servers}" for username, servers in servers_by_user.items()
    )
    if any(servers_by_user.values()):
        logger.info(f"Active MATLAB session(s) ({summary}), sending keep-alive")
        run_keep_alive_command(
            cluster_id,
            workspace_client=workspace_client,
            active_sessions=_active_sessions(servers_by_user),
        )
    else:
        logger.info(
            f"No active MATLAB sessions with idle timeout ({summary or 'no MATLAB users'}), "
            "skipping keep-alive"
        )


def _log_keep_alive_start(
    cluster_id: str,
    workspace_client: WorkspaceClient,
    logger: logging.Logger,
    check_interval_minutes,
):
    """Log the start of the keep-alive loop, marking each cluster restart in the log.

    The cluster name makes the file easier to recognize than its ID alone. It is looked
    up on a best-effort basis, as failing to find it must not stop the keep-alive.
    """
    try:
        cluster_name = workspace_client.clusters.get(cluster_id).cluster_name
    except Exception:
        cluster_name = "unknown"
    logger.info(
        f"Keep-alive started (cluster {cluster_name}, ID {cluster_id}, "
        f"check interval {check_interval_minutes} min)"
    )


def start_cluster_keep_alive(check_interval_minutes=5):
    """Keep cluster alive while any MATLAB user on the cluster has an active session.

    Only sessions with idle timeout configured count, as they eventually shut
    themselves down. Logs are written to
    ``mwhelpers/keep_alive_logs/keep_alive_<cluster_id>.log`` instead of a widget
    output area to avoid clearing the notebook UI.
    """
    keep_alive_thread_name = "matlab-keep-alive"

    # Check if a keep-alive thread is already running by its name.
    # Note: Dead threads are automatically removed from threading.enumerate(),
    # so this check is safe — a new thread will be started if the previous one exited.
    for thread in threading.enumerate():
        if thread.name == keep_alive_thread_name and thread.is_alive():
            return thread

    # The SDK's default "runtime" auth reads the REPL context, which this thread loses
    # once the notebook command that started it finishes. Authenticate explicitly
    # while the context is still available.
    context = get_context()
    cluster_id = context.clusterId
    workspace_client = WorkspaceClient(
        host=context.browserHostName, token=context.apiToken
    )
    logger = _get_keep_alive_logger(cluster_id)

    def keep_alive_loop():
        _log_keep_alive_start(
            cluster_id, workspace_client, logger, check_interval_minutes
        )
        while True:
            try:
                _keep_alive_tick(cluster_id, workspace_client, logger)
                time.sleep(check_interval_minutes * 60)

            except Exception:
                logger.exception("Error during periodic keep-alive check")
                logger.info("Sleeping 60 seconds before retry...")
                time.sleep(60)

    thread = threading.Thread(
        target=keep_alive_loop, daemon=True, name=keep_alive_thread_name
    )
    thread.start()
    return thread
