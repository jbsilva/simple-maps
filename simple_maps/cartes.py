"""
Interact with Cartes.io API.

https://github.com/M-Media-Group/Cartes.io/wiki/API

Cartes.io returns the following status codes in its API:

| Status Code | Description           |
| ----------- | --------------------- |
| 200         | OK                    |
| 201         | CREATED               |
| 400         | BAD REQUEST           |
| 404         | NOT FOUND             |
| 500         | INTERNAL SERVER ERROR |
"""
from typing import Any, Dict

from util import request_json


class Cartes:
    """Wrapper class for interacting with the Cartes.io API."""

    def __init__(self, base_url: str = "https://cartes.io/api"):
        """Set API base URL."""
        self.base_url = base_url

    def map_get(self, map_uuid: str) -> Dict[str, Any]:
        """
        Get a single map.

        GET /api/maps/{map-uuid}
        """
        return request_json(
            request_type="get", url=f"{self.base_url}/maps/{map_uuid}"
        )
