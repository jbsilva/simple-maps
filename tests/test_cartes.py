"""Tests for the Cartes API wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from simple_maps.cartes import (
    Cartes,
    MapCreatePayload,
    MapListParams,
    MarkerCreatePayload,
    MarkerLocationPayload,
    Permission,
    Privacy,
)


if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def api() -> Cartes:
    """Create a Cartes API instance."""
    return Cartes()


@pytest.fixture
def mock_request() -> Generator[MagicMock]:
    """Create a mock for request_json."""
    with patch("simple_maps.cartes.request_json") as mock:
        mock.return_value = {"status": "ok"}
        yield mock


# =============================================================================
# Initialization Tests
# =============================================================================


class TestCartesInit:
    """Tests for Cartes initialization."""

    def test_default_base_url(self) -> None:
        """Default base URL is set correctly."""
        instance = Cartes()
        assert instance.base_url == "https://cartes.io/api"

    def test_custom_base_url(self) -> None:
        """Custom base URL is set correctly."""
        instance = Cartes(base_url="https://custom.api.com")
        assert instance.base_url == "https://custom.api.com"


class TestAuthHeaders:
    """Tests for _auth_headers method."""

    def test_with_api_key(self) -> None:
        """Returns Bearer token header when API key provided."""
        headers = Cartes._auth_headers("test-key")  # noqa: SLF001
        assert headers == {"Authorization": "Bearer test-key"}

    def test_without_api_key(self) -> None:
        """Returns None when no API key provided."""
        headers = Cartes._auth_headers(None)  # noqa: SLF001
        assert headers is None

    def test_with_empty_string(self) -> None:
        """Returns None when API key is empty string."""
        headers = Cartes._auth_headers("")  # noqa: SLF001
        assert headers is None


# =============================================================================
# Map List Tests
# =============================================================================


class TestMapList:
    """Tests for map_list method."""

    def test_no_params(self, api: Cartes, mock_request: MagicMock) -> None:
        """Calls API with default parameters."""
        result = api.map_list()

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/maps"
        assert result == {"status": "ok"}

    def test_with_params(self, api: Cartes, mock_request: MagicMock) -> None:
        """Calls API with all parameters."""
        params = MapListParams(
            ids=["id1", "id2"],
            category_ids=[1, 2],
            with_mine=True,
            with_relations=["markers"],
            order_by="created_at",
            query="test",
            response_format="geojson",
        )
        api.map_list(params, api_key="test-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["params"]["ids[]"] == ["id1", "id2"]
        assert call_kwargs["params"]["category_ids[]"] == [1, 2]
        assert call_kwargs["params"]["withMine"] is True
        assert call_kwargs["params"]["with[]"] == ["markers"]
        assert call_kwargs["params"]["orderBy"] == "created_at"
        assert call_kwargs["headers"] == {"Authorization": "Bearer test-key"}


# =============================================================================
# Map Search Tests
# =============================================================================


class TestMapSearch:
    """Tests for map_search method."""

    def test_search_query(self, api: Cartes, mock_request: MagicMock) -> None:
        """Sends search query to correct endpoint."""
        api.map_search("sharks")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/search"
        assert call_kwargs["params"] == {"q": "sharks"}


# =============================================================================
# Map Get Tests
# =============================================================================


class TestMapGet:
    """Tests for map_get method."""

    def test_get_by_uuid(self, api: Cartes, mock_request: MagicMock) -> None:
        """Retrieves map by UUID."""
        api.map_get("test-uuid")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/test-uuid"


# =============================================================================
# Map Create Tests
# =============================================================================


class TestMapCreate:
    """Tests for map_create method."""

    def test_no_payload(self, api: Cartes, mock_request: MagicMock) -> None:
        """Creates map with no payload."""
        api.map_create()

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "post"
        assert call_kwargs["url"] == "https://cartes.io/api/maps"

    def test_with_payload(self, api: Cartes, mock_request: MagicMock) -> None:
        """Creates map with full payload."""
        payload = MapCreatePayload(
            title="Test Map",
            slug="test-map",
            description="A test map",
            privacy=Privacy.PUBLIC,
            users_can_create_markers=Permission.YES,
        )
        api.map_create(payload, api_key="test-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["params"]["title"] == "Test Map"
        assert call_kwargs["params"]["slug"] == "test-map"
        assert call_kwargs["params"]["privacy"] == Privacy.PUBLIC
        assert call_kwargs["headers"] == {"Authorization": "Bearer test-key"}


# =============================================================================
# Map Edit Tests
# =============================================================================


class TestMapEdit:
    """Tests for map_edit method."""

    def test_edit_with_token(self, api: Cartes, mock_request: MagicMock) -> None:
        """Edits map using map token."""
        payload = MapCreatePayload(title="Updated Title")
        api.map_edit("map-id", payload, map_token="token", api_key="key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "put"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id"
        assert call_kwargs["params"]["title"] == "Updated Title"
        assert call_kwargs["params"]["map_token"] == "token"


# =============================================================================
# Map Delete Tests
# =============================================================================


class TestMapDelete:
    """Tests for map_delete method."""

    def test_delete_with_token(self, api: Cartes, mock_request: MagicMock) -> None:
        """Deletes map using token."""
        api.map_delete("token", "map-id", api_key="key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "delete"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id"
        assert call_kwargs["params"]["map_token"] == "token"


# =============================================================================
# Map Static Image Tests
# =============================================================================


class TestMapStaticImage:
    """Tests for map_static_image method."""

    def test_with_zoom(self, api: Cartes, mock_request: MagicMock) -> None:
        """Gets static image with zoom level."""
        zoom_level = 10
        api.map_static_image("map-id", zoom=zoom_level)

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/images/static"
        assert call_kwargs["params"]["zoom"] == zoom_level


# =============================================================================
# Map Claim Tests
# =============================================================================


class TestMapClaim:
    """Tests for map_claim method."""

    def test_claim(self, api: Cartes, mock_request: MagicMock) -> None:
        """Claims map with token and API key."""
        api.map_claim("map-id", "map-token", "api-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "post"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/claim"
        assert call_kwargs["params"]["map_token"] == "map-token"
        assert call_kwargs["headers"] == {"Authorization": "Bearer api-key"}


class TestMapUnclaim:
    """Tests for map_unclaim method."""

    def test_unclaim(self, api: Cartes, mock_request: MagicMock) -> None:
        """Unclaims map with API key."""
        api.map_unclaim("map-id", "api-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "delete"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/claim"


# =============================================================================
# Map User Tests
# =============================================================================


class TestMapUserList:
    """Tests for map_user_list method."""

    def test_list_users(self, api: Cartes, mock_request: MagicMock) -> None:
        """Lists users on a map."""
        api.map_user_list("map-id", "api-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/users"


class TestMapUserAdd:
    """Tests for map_user_add method."""

    def test_add_user(self, api: Cartes, mock_request: MagicMock) -> None:
        """Adds user to map."""
        api.map_user_add("map-id", "username", "api-key", can_create_markers=True)

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "post"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/users"
        assert call_kwargs["params"]["username"] == "username"
        assert call_kwargs["params"]["can_create_markers"] is True


class TestMapUserDelete:
    """Tests for map_user_delete method."""

    def test_delete_user(self, api: Cartes, mock_request: MagicMock) -> None:
        """Removes user from map."""
        api.map_user_delete("map-id", "username", "api-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "delete"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/users/username"


# =============================================================================
# Marker List Tests
# =============================================================================


class TestMarkerList:
    """Tests for marker_list method."""

    def test_with_options(self, api: Cartes, mock_request: MagicMock) -> None:
        """Lists markers with options."""
        api.marker_list("map-id", show_expired=True, response_format="geojson")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/markers"
        assert call_kwargs["params"]["show_expired"] is True
        assert call_kwargs["params"]["format"] == "geojson"


# =============================================================================
# Marker Create Tests
# =============================================================================


class TestMarkerCreate:
    """Tests for marker_create method."""

    def test_valid_coordinates(self, api: Cartes, mock_request: MagicMock) -> None:
        """Creates marker with valid coordinates."""
        payload = MarkerCreatePayload(
            map_token="token",
            lat=45.0,
            lng=10.0,
            category=1,
            description="Test marker",
        )
        api.marker_create("map-id", payload, api_key="key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "post"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/markers"
        assert call_kwargs["params"]["lat"] == pytest.approx(45.0)
        assert call_kwargs["params"]["lng"] == pytest.approx(10.0)
        assert call_kwargs["params"]["category"] == 1

    def test_with_category_name(self, api: Cartes, mock_request: MagicMock) -> None:
        """Creates marker with category name."""
        payload = MarkerCreatePayload(
            map_token="token",
            lat=45.0,
            lng=10.0,
            category_name="Sharks",
        )
        api.marker_create("map-id", payload)

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["params"]["category_name"] == "Sharks"

    def test_invalid_latitude(self) -> None:
        """Raises ValidationError for latitude > 90."""
        with pytest.raises(ValidationError, match="less than or equal to 90"):
            MarkerCreatePayload(
                map_token="token",
                lat=100.0,
                lng=10.0,
                category=1,
            )

    def test_invalid_longitude(self) -> None:
        """Raises ValidationError for longitude > 180."""
        with pytest.raises(ValidationError, match="less than or equal to 180"):
            MarkerCreatePayload(
                map_token="token",
                lat=45.0,
                lng=200.0,
                category=1,
            )

    def test_no_category(self) -> None:
        """Raises ValidationError when neither category nor category_name provided."""
        with pytest.raises(ValidationError, match=r"category.*category_name"):
            MarkerCreatePayload(
                map_token="token",
                lat=45.0,
                lng=10.0,
            )


# =============================================================================
# Marker Edit Tests
# =============================================================================


class TestMarkerEdit:
    """Tests for marker_edit method."""

    def test_edit_description(self, api: Cartes, mock_request: MagicMock) -> None:
        """Edits marker description."""
        api.marker_edit("token", "map-id", "marker-id", "New description", "api-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "put"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/markers/marker-id"
        assert call_kwargs["params"]["description"] == "New description"


# =============================================================================
# Marker Delete Tests
# =============================================================================


class TestMarkerDelete:
    """Tests for marker_delete method."""

    def test_delete(self, api: Cartes, mock_request: MagicMock) -> None:
        """Deletes marker."""
        api.marker_delete("token", "map-id", "marker-id", "api-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "delete"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/markers/marker-id"
        assert call_kwargs["params"]["token"] == "token"


# =============================================================================
# Marker Spam Tests
# =============================================================================


class TestMarkerSpam:
    """Tests for marker_spam method."""

    def test_report_spam(self, api: Cartes, mock_request: MagicMock) -> None:
        """Reports marker as spam."""
        api.marker_spam("map-id", "marker-id", is_spam=True, api_key="key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "put"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/markers/marker-id"
        assert call_kwargs["params"]["is_spam"] is True


# =============================================================================
# Marker Location Tests
# =============================================================================


class TestMarkerLocationList:
    """Tests for marker_location_list method."""

    def test_list_locations(self, api: Cartes, mock_request: MagicMock) -> None:
        """Lists marker locations."""
        api.marker_location_list("map-id", "marker-id")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/markers/marker-id/locations"


class TestMarkerLocationCreate:
    """Tests for marker_location_create method."""

    def test_create_location(self, api: Cartes, mock_request: MagicMock) -> None:
        """Creates marker location."""
        payload = MarkerLocationPayload(
            lat=45.0,
            lng=10.0,
            zoom=5.0,
            elevation=100.0,
        )
        api.marker_location_create("map-id", "marker-id", payload, "token", "key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "post"
        assert call_kwargs["url"] == "https://cartes.io/api/maps/map-id/markers/marker-id/locations"
        assert call_kwargs["params"]["lat"] == pytest.approx(45.0)
        assert call_kwargs["params"]["lng"] == pytest.approx(10.0)
        assert call_kwargs["params"]["zoom"] == pytest.approx(5.0)
        assert call_kwargs["params"]["elevation"] == pytest.approx(100.0)


# =============================================================================
# Category Tests
# =============================================================================


class TestCategoryList:
    """Tests for category_list method."""

    def test_list(self, api: Cartes, mock_request: MagicMock) -> None:
        """Lists all categories."""
        api.category_list()

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/categories"


class TestCategorySearch:
    """Tests for category_search method."""

    def test_search(self, api: Cartes, mock_request: MagicMock) -> None:
        """Searches categories."""
        api.category_search("shark")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/categories/search"
        assert call_kwargs["params"] == {"q": "shark"}


class TestCategoryRelated:
    """Tests for category_related method."""

    def test_get_related(self, api: Cartes, mock_request: MagicMock) -> None:
        """Gets related categories."""
        api.category_related(123)

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/categories/123/related"


# =============================================================================
# User Tests
# =============================================================================


class TestUserList:
    """Tests for user_list method."""

    def test_list(self, api: Cartes, mock_request: MagicMock) -> None:
        """Lists all public users."""
        api.user_list()

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/users"


class TestUserGet:
    """Tests for user_get method."""

    def test_get_by_username(self, api: Cartes, mock_request: MagicMock) -> None:
        """Gets user by username."""
        api.user_get("testuser")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/users/testuser"

    def test_with_relations(self, api: Cartes, mock_request: MagicMock) -> None:
        """Gets user with relations."""
        api.user_get("testuser", with_relations=["maps"])

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["params"]["with[]"] == ["maps"]


# =============================================================================
# Me (Self) Tests
# =============================================================================


class TestMeGet:
    """Tests for me_get method."""

    def test_get_self(self, api: Cartes, mock_request: MagicMock) -> None:
        """Gets current authenticated user."""
        api.me_get("api-key")

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "get"
        assert call_kwargs["url"] == "https://cartes.io/api/user"
        assert call_kwargs["headers"] == {"Authorization": "Bearer api-key"}


class TestMeUpdate:
    """Tests for me_update method."""

    def test_update_username(self, api: Cartes, mock_request: MagicMock) -> None:
        """Updates current user's username."""
        api.me_update("api-key", username="newname", is_public=True)

        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["request_type"] == "put"
        assert call_kwargs["url"] == "https://cartes.io/api/user"
        assert call_kwargs["params"]["username"] == "newname"
        assert call_kwargs["params"]["is_public"] is True
