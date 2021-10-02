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
from enum import Enum
from typing import Any, Dict, Optional

from util import request_json


class Privacy(str, Enum):
    """Privacy level for map creation."""

    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class Permission(str, Enum):
    """Who can create markers."""

    YES = "yes"
    NO = "no"
    LOGGED = "only_logged_in"


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

    def map_create(
        self,
        title: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        privacy: Optional[Privacy] = None,
        users_can_create_markers: Optional[Permission] = None,
    ) -> Dict[str, Any]:
        """
        Create a map.

        POST /api/maps
        """
        return request_json(
            request_type="post",
            url=f"{self.base_url}/maps",
            params={
                "title": title,
                "slug": slug,
                "description": description,
                "privacy": privacy,
                "users_can_create_markers": users_can_create_markers,
            },
        )
