# This file marks the directory as a Python package.

import re

__version__ = "1.0.0"


def version() -> str:
    """Return the mwhelpers package version."""
    return __version__


def sanitize_url(url: str) -> str:
    """Return the URL unchanged. Stubs override this for local development."""
    return url


def _sanitize_url_for_local_testing(url: str) -> str:
    """Rewrite a Databricks driver-proxy URL to a localhost URL."""
    match = re.search(r"/driver-proxy/o/[^/]+/[^/]+/(\d+)/(.*)", url)
    if match:
        port = match.group(1)
        rest = match.group(2)
        return f"http://localhost:{port}/{rest}"
    return url


# Auto-install lightweight stubs for Databricks-specific packages when they
# are not available (i.e. running locally outside a Databricks cluster).
# On a real cluster the real packages are already installed and the stubs
# are never activated.
try:
    import databricks.sdk  # noqa: F401
    import dbruntime  # noqa: F401
except ImportError:
    from ._stubs import install as _install_stubs

    _install_stubs()
    sanitize_url = _sanitize_url_for_local_testing
