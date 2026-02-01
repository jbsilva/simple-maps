"""
HTTP utility functions for the Cartes.io API client.

This module provides low-level HTTP request handling with JSON serialization
and error handling. It is used internally by the `Cartes` API client.

Exports:
    request_json: Make an HTTP request that returns JSON.

"""

import logging
from json.decoder import JSONDecodeError
from typing import Literal, cast

import httpx


logger = logging.getLogger(__name__)

# =============================================================================
# Type aliases
# =============================================================================
type RequestType = Literal["get", "put", "post", "delete"]
type Headers = dict[str, str]
type Params = dict[str, str | int | float | bool | None | list[str] | list[int]]

# JSON response types
type JsonObject = dict[str, object]
type JsonArray = list[object]
type JsonResponse = JsonObject | JsonArray

# =============================================================================
# Helper functions
# =============================================================================


def _filter_none_values(data: Params | None) -> Params:
    """
    Filter out None values from a dictionary.

    Args:
        data: Dictionary that may contain None values.

    Returns:
        New dictionary with only non-None values.

    """
    return {k: v for k, v in (data or {}).items() if v is not None}


def _build_headers(extra_headers: Headers | None = None) -> Headers:
    """
    Build request headers with JSON content type.

    Args:
        extra_headers: Additional headers to merge.

    Returns:
        Headers dictionary with Content-Type and Accept set to JSON.

    """
    headers: Headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    return headers


def _parse_json_response(response: httpx.Response) -> JsonResponse:
    """
    Parse JSON from response, falling back to text on error.

    Args:
        response: HTTP response object.

    Returns:
        Parsed JSON dictionary or list, or {"response": text} if parsing fails.

    """
    try:
        return cast("JsonResponse", response.json())
    except JSONDecodeError:
        logger.exception("API response was not valid JSON.")
        return {"response": response.text}


# =============================================================================
# Public API
# =============================================================================


def request_json(
    request_type: RequestType,
    url: str,
    headers: Headers | None = None,
    params: Params | None = None,
    timeout: float | None = 10.0,
) -> JsonResponse:
    """
    Make an HTTP request that returns JSON.

    Args:
        request_type: HTTP method (get, put, post, delete).
        url: Target URL for the request.
        headers: Optional additional headers to include.
        params: Request parameters (query params for GET, JSON body otherwise).
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as a dictionary or list.

    Raises:
        httpx.HTTPStatusError: If the server returns an error status code.

    """
    cleaned_params = _filter_none_values(params)
    merged_headers = _build_headers(headers)

    response = httpx.request(
        request_type.upper(),
        url,
        headers=merged_headers,
        params=cleaned_params if request_type == "get" else None,
        json=cleaned_params if request_type != "get" else None,
        timeout=timeout,
    )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        logger.exception("Request error for %s %s", request_type.upper(), url)
        raise

    return _parse_json_response(response)
