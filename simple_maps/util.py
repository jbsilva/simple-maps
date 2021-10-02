"""Util functions."""
import logging
from typing import Any, Dict, Literal, Optional

import requests

ContentType = Literal["application/json"]
RequestType = Literal["get", "put", "post", "delete"]

logger = logging.getLogger(__name__)


def request_json(
    request_type: RequestType,
    url: str,
    headers: Dict[str, Any] = None,
    params: Optional[Dict[str, Any]] = None,
) -> str:  # ) -> Dict[str, Any]:
    """Do a HTTP request that returns a JSON."""
    response = requests.request(
        request_type, url, headers=headers, params=params
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error("Request error: %s", e)
        raise

    return response.text
    # return response.json()
