# Copyright 2026 The MathWorks, Inc.

"""Functions related to web operations"""

import os
from urllib.parse import urlparse

import requests


def _set_status(status_html, message: str):
    """Safely update the status widget if it is not None."""
    if status_html is not None:
        status_html.value = message


def download_file(url, status_html=None, save_path=None) -> str:
    """Download a file from a URL with optional progress reporting.

    Args:
        url: The URL to download from (must start with http:// or https://).
        status_html: Optional Jupyter HTML widget for progress updates. Can be None.
        save_path: Optional path to save the file. Defaults to CWD with filename from URL.
    """
    try:
        # Validate URL
        if not url.lower().startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid URL : {url}. <br> <b>URL must start with http:// or https://</b>"
            )

        # Get filename from URL if save_path not provided
        if save_path is None:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or "downloaded_file"
            save_path = os.path.join(os.getcwd(), filename)

        # Stream download to handle large files
        with requests.get(url, stream=True, timeout=15) as response:
            response.raise_for_status()  # Raise error for bad status codes
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0

            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size:
                            percent = (downloaded_size / total_size) * 100
                            _set_status(
                                status_html,
                                f"<span style='color: #616161;'>Downloading... {percent:.2f}% completed.</span>",
                            )

        _set_status(
            status_html, "<span style='color: #616161;'>Download completed.</span>"
        )
        return save_path

    except requests.exceptions.RequestException as e:
        _set_status(
            status_html, f"<span style='color: #616161;'>❌ Network error: {e}</span>"
        )
    except ValueError as ve:
        _set_status(
            status_html, f"<span style='color: #616161;'>❌ Input error: {ve}</span>"
        )
    except Exception as ex:
        _set_status(
            status_html,
            f"<span style='color: #616161;'>❌ Unexpected error: {ex}</span>",
        )

    return None


def send_http_request(url: str, method: str = "GET", data=None, headers=None):
    """Send an HTTP request to the specified URL."""

    def request_with_timeout(func, *args, **kwargs):
        # default timeout set to 10 seconds
        kwargs["timeout"] = kwargs.get("timeout", 10)
        return func(*args, **kwargs)

    try:
        if method == "GET":
            response = request_with_timeout(requests.get, url)
        elif method == "POST":
            response = request_with_timeout(
                requests.post, url, data=data, headers=headers
            )
        elif method == "DELETE":
            response = request_with_timeout(requests.delete, url)
        else:
            raise ValueError("Unsupported HTTP method: {}".format(method))

        return response
    except requests.Timeout:
        print(f"HTTP request timed out: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None
