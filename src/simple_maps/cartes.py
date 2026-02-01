"""
Cartes.io API client library.

This module provides a Python wrapper for the Cartes.io mapping platform API.
Cartes.io is a free, open-source mapping platform that allows users to create and share interactive
maps with markers.

API Documentation:
    https://docs.cartes.io

HTTP Status Codes:
    - 200: OK
    - 201: Created
    - 400: Bad Request
    - 404: Not Found
    - 500: Internal Server Error

Example:
    >>> api = Cartes()
    >>> maps = api.map_list()
    >>> new_map = api.map_create(MapCreatePayload(title="My Map"))

"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .util import JsonResponse, request_json


# =============================================================================
# Type aliases
# =============================================================================
type Latitude = Annotated[float, Field(ge=-90, le=90, description="Latitude (-90 to 90)")]
type Longitude = Annotated[float, Field(ge=-180, le=180, description="Longitude (-180 to 180)")]
type RequestParams = dict[str, str | int | float | bool | None | list[str] | list[int]]
type AuthHeaders = dict[str, str] | None


# =============================================================================
# Enums
# =============================================================================
class Privacy(StrEnum):
    """
    Privacy level for map visibility.

    Attributes:
        PUBLIC: Map is visible to everyone.
        UNLISTED: Map is accessible via direct link only.
        PRIVATE: Map is only visible to the owner.

    """

    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class Permission(StrEnum):
    """
    Permission level for marker creation on a map.

    Attributes:
        YES: Anyone can create markers.
        NO: Only the owner can create markers.
        LOGGED: Only logged-in users can create markers.

    """

    YES = "yes"
    NO = "no"
    LOGGED = "only_logged_in"


# =============================================================================
# Pydantic Models
# =============================================================================
class MapCreatePayload(BaseModel):
    """
    Payload for creating or editing a map.

    All fields are optional when creating a map. The API will use defaults for any unspecified
    fields.

    Attributes:
        title: Display title for the map.
        slug: URL-friendly identifier (currently unused by API).
        description: Detailed description of the map.
        privacy: Visibility level (public, unlisted, private).
        users_can_create_markers: Who can add markers to this map.

    """

    model_config = ConfigDict(frozen=True, use_enum_values=True)

    title: str | None = None
    slug: str | None = None
    description: str | None = None
    privacy: Privacy | None = None
    users_can_create_markers: Permission | None = None


class MarkerCreatePayload(BaseModel):
    """
    Payload for creating a marker on a map.

    Requires either `category` (ID) or `category_name` to be specified.
    The `map_token` is required for authentication on anonymous maps.

    Attributes:
        map_token: Authentication token for the map.
        lat: Latitude coordinate (-90 to 90).
        lng: Longitude coordinate (-180 to 180).
        category: Existing category ID.
        category_name: Name for a new or existing category.
        description: Optional marker description.

    """

    model_config = ConfigDict(frozen=True)

    map_token: str
    lat: Latitude
    lng: Longitude
    category: int | None = None
    category_name: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def check_category_provided(self) -> MarkerCreatePayload:
        """Validate that either category or category_name is provided."""
        if self.category is None and self.category_name is None:
            msg = "Either 'category' or 'category_name' must be provided"
            raise ValueError(msg)
        return self


class MapListParams(BaseModel):
    """
    Parameters for filtering and paginating map listings.

    All fields are optional. When not specified, the API returns all public maps with default
    ordering.

    Attributes:
        ids: Filter by specific map UUIDs.
        category_ids: Filter by category IDs.
        with_mine: Include maps owned by the authenticated user.
        with_relations: Related data to include (e.g., 'markers').
        order_by: Field to sort results by.
        query: Search query string.
        response_format: Response format (e.g., 'geojson').

    """

    model_config = ConfigDict(frozen=True)

    ids: list[str] | None = None
    category_ids: list[int] | None = None
    with_mine: bool | None = None
    with_relations: list[str] | None = None
    order_by: str | None = None
    query: str | None = None
    response_format: str | None = None


class MarkerLocationPayload(BaseModel):
    """
    Payload for adding a location to a marker's history.

    Markers can track location history over time. This payload adds a new location point with
    optional telemetry data.

    Attributes:
        lat: Latitude coordinate (-90 to 90).
        lng: Longitude coordinate (-180 to 180).
        zoom: Map zoom level (0-20).
        elevation: Altitude in meters.
        heading: Compass heading (0-359 degrees).
        pitch: Vertical angle (-90 to 90 degrees).
        roll: Roll angle (-180 to 180 degrees).
        speed: Movement speed in meters per second.

    """

    model_config = ConfigDict(frozen=True)

    lat: Latitude
    lng: Longitude
    zoom: Annotated[float, Field(ge=0, le=20)] | None = None
    elevation: float | None = None
    heading: Annotated[float, Field(ge=0, lt=360)] | None = None
    pitch: Annotated[float, Field(ge=-90, le=90)] | None = None
    roll: Annotated[float, Field(ge=-180, le=180)] | None = None
    speed: Annotated[float, Field(ge=0)] | None = None


# =============================================================================
# API Client
# =============================================================================


class Cartes:
    """
    Client for the Cartes.io mapping platform API.

    This class provides methods for all Cartes.io API endpoints including maps, markers, categories,
    and users.

    Attributes:
        base_url: Base URL for API requests.

    Example:
        >>> api = Cartes()
        >>> maps = api.map_list()
        >>> api.map_create(MapCreatePayload(title="New Map"))

    """

    def __init__(self, base_url: str = "https://cartes.io/api") -> None:
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the Cartes.io API.

        """
        self.base_url = base_url

    @staticmethod
    def _auth_headers(api_key: str | None) -> AuthHeaders:
        """Build authorization headers from an API key."""
        if not api_key:
            return None
        return {"Authorization": f"Bearer {api_key}"}

    # -------------------------------------------------------------------------
    # Maps
    # -------------------------------------------------------------------------

    def map_list(
        self,
        params: MapListParams | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Get all public maps.

        Args:
            params: Optional filtering and pagination parameters.
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing list of maps.

        Endpoint:
            GET /api/maps

        """
        p = params or MapListParams()
        request_params: RequestParams = {
            "orderBy": p.order_by,
            "query": p.query,
            "format": p.response_format,
            "withMine": p.with_mine,
        }
        if p.ids:
            request_params["ids[]"] = p.ids
        if p.category_ids:
            request_params["category_ids[]"] = p.category_ids
        if p.with_relations:
            request_params["with[]"] = p.with_relations
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps",
            headers=self._auth_headers(api_key),
            params=request_params,
        )

    def map_search(
        self,
        query: str,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Search public maps by query string.

        Args:
            query: Search term to match against map titles/descriptions.
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing matching maps.

        Endpoint:
            GET /api/maps/search?q=xxx

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps/search",
            headers=self._auth_headers(api_key),
            params={"q": query},
        )

    def map_get(
        self,
        map_uuid: str,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Get a single map by UUID.

        Args:
            map_uuid: Unique identifier of the map.
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing map details.

        Endpoint:
            GET /api/maps/{map-uuid}

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps/{map_uuid}",
            headers=self._auth_headers(api_key),
        )

    def map_create(
        self,
        payload: MapCreatePayload | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Create a new map.

        Args:
            payload: Map creation parameters.
            api_key: Optional API key to associate map with user.

        Returns:
            JSON response containing created map and edit token.

        Endpoint:
            POST /api/maps

        """
        request_payload = payload or MapCreatePayload()
        return request_json(
            request_type="post",
            url=f"{self.base_url}/maps",
            headers=self._auth_headers(api_key),
            params={
                "title": request_payload.title,
                "slug": request_payload.slug,
                "description": request_payload.description,
                "privacy": request_payload.privacy,
                "users_can_create_markers": request_payload.users_can_create_markers,
            },
        )

    def map_edit(
        self,
        map_id: str,
        payload: MapCreatePayload | None = None,
        map_token: str | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Edit an existing map.

        Args:
            map_id: UUID of the map to edit.
            payload: Updated map properties.
            map_token: Edit token (required for anonymous maps).
            api_key: API key (alternative to map_token for owned maps).

        Returns:
            JSON response containing updated map.

        Endpoint:
            PUT /api/maps/{map-uuid}

        """
        request_payload = payload or MapCreatePayload()
        return request_json(
            request_type="put",
            url=f"{self.base_url}/maps/{map_id}",
            headers=self._auth_headers(api_key),
            params={
                "map_token": map_token,
                "title": request_payload.title,
                "slug": request_payload.slug,
                "description": request_payload.description,
                "privacy": request_payload.privacy,
                "users_can_create_markers": request_payload.users_can_create_markers,
            },
        )

    def map_delete(
        self,
        map_token: str | None,
        map_id: str,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Delete a map.

        Args:
            map_token: Edit token (required for anonymous maps).
            map_id: UUID of the map to delete.
            api_key: API key (alternative to map_token for owned maps).

        Returns:
            JSON response confirming deletion.

        Endpoint:
            DELETE /api/maps/{map-id}

        """
        return request_json(
            request_type="delete",
            url=f"{self.base_url}/maps/{map_id}",
            headers=self._auth_headers(api_key),
            params={
                "map_token": map_token,
            },
        )

    def map_static_image(
        self,
        map_id: str,
        zoom: int | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Get a static image URL for a map.

        Args:
            map_id: UUID of the map.
            zoom: Zoom level (2-19).
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing static image URL.

        Endpoint:
            GET /api/maps/{map-uuid}/images/static

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps/{map_id}/images/static",
            headers=self._auth_headers(api_key),
            params={"zoom": zoom},
        )

    def map_claim(
        self,
        map_id: str,
        map_token: str,
        api_key: str,
    ) -> JsonResponse:
        """
        Claim an anonymous map to associate with your account.

        Args:
            map_id: UUID of the map to claim.
            map_token: Edit token for the map.
            api_key: Your API key.

        Returns:
            JSON response confirming claim.

        Endpoint:
            POST /api/maps/{map-uuid}/claim

        """
        return request_json(
            request_type="post",
            url=f"{self.base_url}/maps/{map_id}/claim",
            headers=self._auth_headers(api_key),
            params={"map_token": map_token},
        )

    def map_unclaim(
        self,
        map_id: str,
        api_key: str,
    ) -> JsonResponse:
        """
        Unclaim a map to make it anonymous again.

        Args:
            map_id: UUID of the map to unclaim.
            api_key: Your API key.

        Returns:
            JSON response confirming unclaim.

        Endpoint:
            DELETE /api/maps/{map-uuid}/claim

        """
        return request_json(
            request_type="delete",
            url=f"{self.base_url}/maps/{map_id}/claim",
            headers=self._auth_headers(api_key),
        )

    def map_user_list(
        self,
        map_id: str,
        api_key: str,
    ) -> JsonResponse:
        """
        List users with access to a map.

        Args:
            map_id: UUID of the map.
            api_key: Your API key (must be map owner).

        Returns:
            JSON response containing list of users.

        Endpoint:
            GET /api/maps/{map-uuid}/users

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps/{map_id}/users",
            headers=self._auth_headers(api_key),
        )

    def map_user_add(
        self,
        map_id: str,
        username: str,
        api_key: str,
        *,
        can_create_markers: bool | None = None,
    ) -> JsonResponse:
        """
        Add a user to a map.

        Args:
            map_id: UUID of the map.
            username: Username to add.
            api_key: Your API key (must be map owner).
            can_create_markers: Whether user can create markers.

        Returns:
            JSON response confirming user addition.

        Endpoint:
            POST /api/maps/{map-uuid}/users

        """
        return request_json(
            request_type="post",
            url=f"{self.base_url}/maps/{map_id}/users",
            headers=self._auth_headers(api_key),
            params={
                "username": username,
                "can_create_markers": can_create_markers,
            },
        )

    def map_user_delete(
        self,
        map_id: str,
        username: str,
        api_key: str,
    ) -> JsonResponse:
        """
        Remove a user from a map.

        Args:
            map_id: UUID of the map.
            username: Username to remove.
            api_key: Your API key (must be map owner).

        Returns:
            JSON response confirming user removal.

        Endpoint:
            DELETE /api/maps/{map-uuid}/users/{username}

        """
        return request_json(
            request_type="delete",
            url=f"{self.base_url}/maps/{map_id}/users/{username}",
            headers=self._auth_headers(api_key),
        )

    # -------------------------------------------------------------------------
    # Markers
    # -------------------------------------------------------------------------

    def marker_list(
        self,
        map_id: str,
        *,
        show_expired: bool | None = None,
        response_format: str | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Get all markers on a map.

        Args:
            map_id: UUID of the map.
            show_expired: Include expired markers.
            response_format: Response format (e.g., 'geojson').
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing list of markers.

        Endpoint:
            GET /api/maps/{map-id}/markers

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps/{map_id}/markers",
            headers=self._auth_headers(api_key),
            params={
                "show_expired": show_expired,
                "format": response_format,
            },
        )

    def marker_create(
        self,
        map_id: str,
        payload: MarkerCreatePayload,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Create a marker on a map.

        Args:
            map_id: UUID of the map.
            payload: Marker creation parameters.
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing created marker and edit token.

        Raises:
            ValueError: If coordinates are invalid or category is missing.

        Endpoint:
            POST /api/maps/{map-id}/markers

        Note:
            Coordinate and category validation is handled by Pydantic.

        """
        return request_json(
            request_type="post",
            url=f"{self.base_url}/maps/{map_id}/markers",
            headers=self._auth_headers(api_key),
            params={
                "map_token": payload.map_token,
                "category": payload.category,
                "lat": payload.lat,
                "lng": payload.lng,
                "description": payload.description,
                "category_name": payload.category_name,
            },
        )

    def marker_edit(
        self,
        marker_token: str | None,
        map_id: str,
        marker_id: str,
        description: str | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Edit a marker's description.

        Args:
            marker_token: Edit token (required for anonymous markers).
            map_id: UUID of the map.
            marker_id: ID of the marker to edit.
            description: New description.
            api_key: API key (alternative to marker_token).

        Returns:
            JSON response containing updated marker.

        Endpoint:
            PUT /api/maps/{map-id}/markers/{marker-id}

        """
        return request_json(
            request_type="put",
            url=f"{self.base_url}/maps/{map_id}/markers/{marker_id}",
            headers=self._auth_headers(api_key),
            params={"token": marker_token, "description": description},
        )

    def marker_delete(
        self,
        marker_token: str | None,
        map_id: str,
        marker_id: str,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Delete a marker from a map.

        Args:
            marker_token: Edit token (required for anonymous markers).
            map_id: UUID of the map.
            marker_id: ID of the marker to delete.
            api_key: API key (alternative to marker_token).

        Returns:
            JSON response confirming deletion.

        Endpoint:
            DELETE /api/maps/{map-id}/markers/{marker-id}

        """
        return request_json(
            request_type="delete",
            url=f"{self.base_url}/maps/{map_id}/markers/{marker_id}",
            headers=self._auth_headers(api_key),
            params={
                "token": marker_token,
            },
        )

    def marker_spam(
        self,
        map_id: str,
        marker_id: str,
        *,
        is_spam: bool,
        map_token: str | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Mark or unmark a marker as spam.

        Args:
            map_id: UUID of the map.
            marker_id: ID of the marker.
            is_spam: True to mark as spam, False to unmark.
            map_token: Map edit token.
            api_key: API key for authenticated requests.

        Returns:
            JSON response containing updated marker.

        Endpoint:
            PUT /api/maps/{map-uuid}/markers/{marker-id}

        """
        return request_json(
            request_type="put",
            url=f"{self.base_url}/maps/{map_id}/markers/{marker_id}",
            headers=self._auth_headers(api_key),
            params={
                "map_token": map_token,
                "is_spam": is_spam,
            },
        )

    def marker_location_list(
        self,
        map_id: str,
        marker_id: str,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Get location history for a marker.

        Args:
            map_id: UUID of the map.
            marker_id: ID of the marker.
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing list of locations.

        Endpoint:
            GET /api/maps/{map-uuid}/markers/{marker-id}/locations

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/maps/{map_id}/markers/{marker_id}/locations",
            headers=self._auth_headers(api_key),
        )

    def marker_location_create(
        self,
        map_id: str,
        marker_id: str,
        payload: MarkerLocationPayload,
        marker_token: str | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Add a location to a marker's history.

        Args:
            map_id: UUID of the map.
            marker_id: ID of the marker.
            payload: Location data including coordinates and telemetry.
            marker_token: Marker edit token.
            api_key: API key for authenticated requests.

        Returns:
            JSON response containing created location.

        Endpoint:
            POST /api/maps/{map-uuid}/markers/{marker-id}/locations

        """
        return request_json(
            request_type="post",
            url=f"{self.base_url}/maps/{map_id}/markers/{marker_id}/locations",
            headers=self._auth_headers(api_key),
            params={
                "token": marker_token,
                "lat": payload.lat,
                "lng": payload.lng,
                "zoom": payload.zoom,
                "elevation": payload.elevation,
                "heading": payload.heading,
                "pitch": payload.pitch,
                "roll": payload.roll,
                "speed": payload.speed,
            },
        )

    # -------------------------------------------------------------------------
    # Categories
    # -------------------------------------------------------------------------

    def category_list(self, api_key: str | None = None) -> JsonResponse:
        """
        Get all available categories.

        Args:
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing list of categories.

        Endpoint:
            GET /api/categories

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/categories",
            headers=self._auth_headers(api_key),
        )

    def category_search(
        self,
        query: str,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Search categories by name.

        Args:
            query: Search term to match against category names.
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing matching categories.

        Endpoint:
            GET /api/categories/search?q=xxx

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/categories/search",
            headers=self._auth_headers(api_key),
            params={"q": query},
        )

    def category_related(
        self,
        category_id: int,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Get categories related to a specific category.

        Args:
            category_id: ID of the category.
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing related categories.

        Endpoint:
            GET /api/categories/{category-id}/related

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/categories/{category_id}/related",
            headers=self._auth_headers(api_key),
        )

    # -------------------------------------------------------------------------
    # Users
    # -------------------------------------------------------------------------

    def user_list(self, api_key: str | None = None) -> JsonResponse:
        """
        Get all public users.

        Args:
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing list of public users.

        Endpoint:
            GET /api/users

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/users",
            headers=self._auth_headers(api_key),
        )

    def user_get(
        self,
        username: str,
        with_relations: list[str] | None = None,
        api_key: str | None = None,
    ) -> JsonResponse:
        """
        Get a public user's profile.

        Args:
            username: Username to look up.
            with_relations: Related data to include (e.g., 'maps').
            api_key: Optional API key for authenticated requests.

        Returns:
            JSON response containing user profile.

        Endpoint:
            GET /api/users/{username}

        """
        params: RequestParams = {}
        if with_relations:
            params["with[]"] = with_relations
        return request_json(
            request_type="get",
            url=f"{self.base_url}/users/{username}",
            headers=self._auth_headers(api_key),
            params=params if params else None,
        )

    # -------------------------------------------------------------------------
    # Self (authenticated user)
    # -------------------------------------------------------------------------

    def me_get(self, api_key: str) -> JsonResponse:
        """
        Get the authenticated user's profile.

        Args:
            api_key: Your API key.

        Returns:
            JSON response containing your profile.

        Endpoint:
            GET /api/user

        """
        return request_json(
            request_type="get",
            url=f"{self.base_url}/user",
            headers=self._auth_headers(api_key),
        )

    def me_update(
        self,
        api_key: str,
        *,
        username: str | None = None,
        is_public: bool | None = None,
    ) -> JsonResponse:
        """
        Update the authenticated user's profile.

        Args:
            api_key: Your API key.
            username: New username.
            is_public: Whether to make profile public.

        Returns:
            JSON response containing updated profile.

        Endpoint:
            PUT /api/user

        """
        return request_json(
            request_type="put",
            url=f"{self.base_url}/user",
            headers=self._auth_headers(api_key),
            params={
                "username": username,
                "is_public": is_public,
            },
        )
