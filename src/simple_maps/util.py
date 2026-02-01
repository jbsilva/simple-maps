"""Util functions."""
import logging
from json.decoder import JSONDecodeError
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
) -> Dict[str, Any]:
    """Do a HTTP request that returns a JSON."""
    response = requests.request(
        request_type, url, headers=headers, params=params
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error("Request error: %s", e)
        raise

    try:
        return response.json()
    except JSONDecodeError:
        logging.exception("API response was not a valid JSON.")
        return {"response": response.text}
