"""Tests for the util module."""

from __future__ import annotations

from json import JSONDecodeError
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import httpx
import pytest

from simple_maps.util import request_json


if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_response() -> Generator[MagicMock]:
    """Create a mock response object for successful requests."""
    with patch("simple_maps.util.httpx.request") as mock_request:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": "test"}
        mock_resp.text = "text response"
        mock_request.return_value = mock_resp
        yield mock_request


# =============================================================================
# Request Type Tests
# =============================================================================


class TestGetRequest:
    """Tests for GET request behavior."""

    def test_params_as_query(self, mock_response: MagicMock) -> None:
        """GET sends params as query parameters."""
        result = request_json(
            request_type="get",
            url="https://api.example.com/test",
            params={"key": "value"},
        )

        mock_response.assert_called_once()
        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["params"] == {"key": "value"}
        assert call_kwargs["json"] is None
        assert result == {"data": "test"}


class TestPostRequest:
    """Tests for POST request behavior."""

    def test_params_as_json_body(self, mock_response: MagicMock) -> None:
        """POST sends params as JSON body."""
        request_json(
            request_type="post",
            url="https://api.example.com/test",
            params={"key": "value"},
        )

        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["params"] is None
        assert call_kwargs["json"] == {"key": "value"}


class TestPutRequest:
    """Tests for PUT request behavior."""

    def test_params_as_json_body(self, mock_response: MagicMock) -> None:
        """PUT sends params as JSON body."""
        request_json(
            request_type="put",
            url="https://api.example.com/test",
            params={"key": "value"},
        )

        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["json"] == {"key": "value"}


class TestDeleteRequest:
    """Tests for DELETE request behavior."""

    def test_params_as_json_body(self, mock_response: MagicMock) -> None:
        """DELETE sends params as JSON body."""
        request_json(
            request_type="delete",
            url="https://api.example.com/test",
            params={"key": "value"},
        )

        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["json"] == {"key": "value"}


# =============================================================================
# Parameter Handling Tests
# =============================================================================


class TestParameterFiltering:
    """Tests for parameter filtering behavior."""

    def test_none_values_filtered(self, mock_response: MagicMock) -> None:
        """None values are filtered from params."""
        request_json(
            request_type="get",
            url="https://api.example.com/test",
            params={"key": "value", "empty": None},
        )

        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["params"] == {"key": "value"}
        assert "empty" not in call_kwargs["params"]


class TestHeaderHandling:
    """Tests for header handling."""

    def test_custom_headers_merged(self, mock_response: MagicMock) -> None:
        """Custom headers are merged with defaults."""
        request_json(
            request_type="get",
            url="https://api.example.com/test",
            headers={"Authorization": "Bearer token"},
        )

        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["headers"]["Authorization"] == "Bearer token"
        assert call_kwargs["headers"]["Accept"] == "application/json"
        assert call_kwargs["headers"]["Content-Type"] == "application/json"


# =============================================================================
# Timeout Tests
# =============================================================================


class TestTimeout:
    """Tests for request timeout behavior."""

    def test_default_timeout(self, mock_response: MagicMock) -> None:
        """Default timeout is 10 seconds."""
        request_json(
            request_type="get",
            url="https://api.example.com/test",
        )

        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["timeout"] == pytest.approx(10.0)

    def test_custom_timeout(self, mock_response: MagicMock) -> None:
        """Custom timeout is used when specified."""
        request_json(
            request_type="get",
            url="https://api.example.com/test",
            timeout=30.0,
        )

        call_kwargs = mock_response.call_args.kwargs
        assert call_kwargs["timeout"] == pytest.approx(30.0)


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_http_error_raised(self) -> None:
        """HTTP errors are propagated."""
        with patch("simple_maps.util.httpx.request") as mock_request:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found",
                request=MagicMock(),
                response=MagicMock(),
            )
            mock_request.return_value = mock_resp

            with pytest.raises(httpx.HTTPStatusError):
                request_json(
                    request_type="get",
                    url="https://api.example.com/test",
                )

    def test_json_decode_error_returns_text(self) -> None:
        """JSON decode errors return text response wrapped in dict."""
        with patch("simple_maps.util.httpx.request") as mock_request:
            mock_resp = MagicMock()
            mock_resp.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
            mock_resp.text = "Plain text response"
            mock_request.return_value = mock_resp

            result = request_json(
                request_type="get",
                url="https://api.example.com/test",
            )

            assert result == {"response": "Plain text response"}
