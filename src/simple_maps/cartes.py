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
import logging
from enum import Enum
from typing import Any, Dict, Optional

from .util import request_json


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

    def map_delete(self, token: str, map_id: str) -> Dict[str, Any]:
        """
        Delete a single map.

        DELETE /api/maps/{map-id}
        """
        return request_json(
            request_type="delete",
            url=f"{self.base_url}/maps/{map_id}",
            params={
                "token": token,
            },
        )

    def marker_list(
        self, map_id: str, show_expired: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get all markers on a map.

        GET /api/maps/{map-id}/markers
        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps/{map_id}/markers",
            params={
                "show_expired": show_expired,
            },
        )

    def marker_create(
        self,
        map_token: str,
        map_id: str,
        lat: float,
        lng: float,
        category: Optional[int] = None,
        category_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a marker on a map.

        POST /api/maps/{map-id}/markers
        """
        if (
            (-90 <= lat <= 90)
            and (-90 <= lng <= 90)
            and (category is not None or category_name is not None)
        ):
            return request_json(
                request_type="post",
                url=f"{self.base_url}/maps/{map_id}/markers",
                params={
                    "map_token": map_token,
                    "category": category,
                    "lat": lat,
                    "lng": lng,
                    "description": description,
                    "category_name": category_name,
                },
            )
        else:
            logging.error(
                "Invalid coordinate value for marker: (%s, %s).", lat, lng
            )
            raise ValueError

    def marker_edit(
        self,
        token: str,
        map_id: str,
        marker_id: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Edit a marker on a map.

        PUT /api/maps/{map-id}/markers/{marker-id}
        """
        return request_json(
            request_type="put",
            url=f"{self.base_url}/maps/{map_id}/markers/{marker_id}",
            params={"token": token, "description": description},
        )

    def marker_delete(
        self, token: str, map_id: str, marker_id: str
    ) -> Dict[str, Any]:
        """
        Delete a marker on a map.

        DELETE /api/maps/{map-id}/markers/{marker-id}
        """
        return request_json(
            request_type="delete",
            url=f"{self.base_url}/maps/{map_id}/markers/{marker_id}",
            params={
                "token": token,
            },
        )
