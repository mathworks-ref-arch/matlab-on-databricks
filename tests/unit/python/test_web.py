# Copyright 2026 The MathWorks, Inc.

import pytest

from resources.notebooks.mwhelpers import web


class TestSendHttpRequest:
    def test_sends_get_request(self, mocker):
        mock_response = mocker.MagicMock()
        mocker.patch(
            "resources.notebooks.mwhelpers.web.requests.get",
            return_value=mock_response,
        )
        result = web.send_http_request("http://example.com", method="GET")
        assert result == mock_response

    def test_sends_post_request(self, mocker):
        mock_response = mocker.MagicMock()
        mocker.patch(
            "resources.notebooks.mwhelpers.web.requests.post",
            return_value=mock_response,
        )
        result = web.send_http_request(
            "http://example.com", method="POST", data={"key": "value"}
        )
        assert result == mock_response

    def test_sends_delete_request(self, mocker):
        mock_response = mocker.MagicMock()
        mocker.patch(
            "resources.notebooks.mwhelpers.web.requests.delete",
            return_value=mock_response,
        )
        result = web.send_http_request("http://example.com", method="DELETE")
        assert result == mock_response

    def test_raises_value_error_for_unsupported_method(self):
        with pytest.raises(ValueError, match="Unsupported HTTP method"):
            web.send_http_request("http://example.com", method="PATCH")

    def test_returns_none_on_timeout(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.web.requests.get",
            side_effect=web.requests.Timeout("timed out"),
        )
        result = web.send_http_request("http://example.com", method="GET")
        assert result is None

    def test_returns_none_on_request_exception(self, mocker):
        mocker.patch(
            "resources.notebooks.mwhelpers.web.requests.get",
            side_effect=web.requests.exceptions.RequestException("connection error"),
        )
        result = web.send_http_request("http://example.com", method="GET")
        assert result is None


class TestDownloadFile:
    def test_returns_none_for_invalid_url(self, mocker):
        mock_status_html = mocker.MagicMock()
        result = web.download_file(
            "ftp://invalid.com/file", status_html=mock_status_html
        )
        assert result is None
        assert "Invalid URL" in mock_status_html.value
