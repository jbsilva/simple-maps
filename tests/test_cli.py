"""Tests for the CLI commands."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from simple_maps.cli import app


def _make_http_error(message: str = "Server error") -> httpx.HTTPStatusError:
    """Create an HTTPStatusError for testing."""
    mock_request = MagicMock(spec=httpx.Request)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500
    return httpx.HTTPStatusError(message, request=mock_request, response=mock_response)


if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_api() -> Generator[MagicMock]:
    """Mock the Cartes API with default successful responses."""
    with patch("simple_maps.cli.api") as mock:
        # Map endpoints
        mock.map_list.return_value = {"data": []}
        mock.map_search.return_value = {"data": []}
        mock.map_get.return_value = {"uuid": "test-uuid", "title": "Test"}
        mock.map_static_image.return_value = {"url": "http://example.com/image.png"}
        mock.map_create.return_value = {"uuid": "new-uuid", "token": "new-token"}
        mock.map_edit.return_value = {"uuid": "test-uuid"}
        mock.map_delete.return_value = {}
        mock.map_claim.return_value = {}
        mock.map_unclaim.return_value = {}
        mock.map_user_list.return_value = {"data": []}
        mock.map_user_add.return_value = {}
        mock.map_user_delete.return_value = {}
        # Marker endpoints
        mock.marker_list.return_value = []
        mock.marker_create.return_value = {"id": 1, "token": "marker-token"}
        mock.marker_edit.return_value = {}
        mock.marker_delete.return_value = {}
        mock.marker_spam.return_value = {}
        mock.marker_location_list.return_value = []
        mock.marker_location_create.return_value = {}
        # Category endpoints
        mock.category_list.return_value = {"data": []}
        mock.category_search.return_value = {"data": []}
        mock.category_related.return_value = {"data": []}
        # User endpoints
        mock.user_list.return_value = {"data": []}
        mock.user_get.return_value = {"username": "testuser"}
        mock.me_get.return_value = {"username": "me"}
        mock.me_update.return_value = {"username": "newname"}
        yield mock


# =============================================================================
# Map Command Tests
# =============================================================================


class TestMapList:
    """Tests for map list command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map list."""
        result = runner.invoke(app, ["map", "list"])
        assert result.exit_code == 0
        mock_api.map_list.assert_called_once()

    def test_with_options(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map list with query options."""
        result = runner.invoke(
            app,
            ["map", "list", "--order-by", "created_at", "--query", "test"],
        )
        assert result.exit_code == 0
        mock_api.map_list.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map list error handling."""
        mock_api.map_list.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["map", "list"])
        assert result.exit_code == 1
        assert "Error listing maps" in result.output


class TestMapSearch:
    """Tests for map search command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map search."""
        result = runner.invoke(app, ["map", "search", "--query", "sharks"])
        assert result.exit_code == 0
        mock_api.map_search.assert_called_once_with("sharks")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map search error handling."""
        mock_api.map_search.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["map", "search", "--query", "sharks"])
        assert result.exit_code == 1
        assert "Error searching maps" in result.output


class TestMapGet:
    """Tests for map get command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map get."""
        result = runner.invoke(app, ["map", "get", "--map-id", "test-uuid"])
        assert result.exit_code == 0
        mock_api.map_get.assert_called_once_with("test-uuid")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map get error handling."""
        mock_api.map_get.side_effect = _make_http_error("Not found")
        result = runner.invoke(app, ["map", "get", "--map-id", "invalid"])
        assert result.exit_code == 1
        assert "Error getting map" in result.output


class TestMapStaticImage:
    """Tests for map static-image command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful static image retrieval."""
        result = runner.invoke(
            app,
            ["map", "static-image", "--map-id", "test-uuid", "--zoom", "10"],
        )
        assert result.exit_code == 0
        mock_api.map_static_image.assert_called_once_with("test-uuid", 10)

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test static image error handling."""
        mock_api.map_static_image.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            ["map", "static-image", "--map-id", "test-uuid"],
        )
        assert result.exit_code == 1
        assert "Error getting static image" in result.output


class TestMapCreate:
    """Tests for map create command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map creation."""
        result = runner.invoke(
            app,
            ["map", "create", "--title", "My Map", "--description", "A test map"],
        )
        assert result.exit_code == 0
        mock_api.map_create.assert_called_once()

    def test_with_privacy(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map creation with privacy option."""
        result = runner.invoke(
            app,
            ["map", "create", "--title", "Private Map", "--privacy", "private"],
        )
        assert result.exit_code == 0
        mock_api.map_create.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map creation error handling."""
        mock_api.map_create.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["map", "create", "--title", "My Map"])
        assert result.exit_code == 1
        assert "Error creating map" in result.output


class TestMapEdit:
    """Tests for map edit command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map edit."""
        result = runner.invoke(
            app,
            [
                "map",
                "edit",
                "--map-id",
                "test-uuid",
                "--title",
                "Updated Title",
                "--map-token",
                "token",
            ],
        )
        assert result.exit_code == 0
        mock_api.map_edit.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map edit error handling."""
        mock_api.map_edit.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            ["map", "edit", "--map-id", "test-uuid", "--title", "New Title"],
        )
        assert result.exit_code == 1
        assert "Error editing map" in result.output


class TestMapDelete:
    """Tests for map delete command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map delete."""
        result = runner.invoke(
            app,
            ["map", "delete", "--map-id", "test-uuid", "--map-token", "token"],
        )
        assert result.exit_code == 0
        mock_api.map_delete.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map delete error handling."""
        mock_api.map_delete.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            ["map", "delete", "--map-id", "test-uuid", "--map-token", "token"],
        )
        assert result.exit_code == 1
        assert "Error deleting map" in result.output


class TestMapClaim:
    """Tests for map claim command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map claim."""
        result = runner.invoke(
            app,
            [
                "map",
                "claim",
                "--map-id",
                "test-uuid",
                "--map-token",
                "token",
                "--api-key",
                "key",
            ],
        )
        assert result.exit_code == 0
        mock_api.map_claim.assert_called_once_with("test-uuid", "token", "key")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map claim error handling."""
        mock_api.map_claim.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "map",
                "claim",
                "--map-id",
                "test-uuid",
                "--map-token",
                "token",
                "--api-key",
                "key",
            ],
        )
        assert result.exit_code == 1
        assert "Error claiming map" in result.output


class TestMapUnclaim:
    """Tests for map unclaim command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map unclaim."""
        result = runner.invoke(
            app,
            ["map", "unclaim", "--map-id", "test-uuid", "--api-key", "key"],
        )
        assert result.exit_code == 0
        mock_api.map_unclaim.assert_called_once_with("test-uuid", "key")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map unclaim error handling."""
        mock_api.map_unclaim.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            ["map", "unclaim", "--map-id", "test-uuid", "--api-key", "key"],
        )
        assert result.exit_code == 1
        assert "Error un-claiming map" in result.output


class TestMapUserList:
    """Tests for map user-list command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map user list."""
        result = runner.invoke(
            app,
            ["map", "user-list", "--map-id", "test-uuid", "--api-key", "key"],
        )
        assert result.exit_code == 0
        mock_api.map_user_list.assert_called_once_with("test-uuid", "key")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map user list error handling."""
        mock_api.map_user_list.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            ["map", "user-list", "--map-id", "test-uuid", "--api-key", "key"],
        )
        assert result.exit_code == 1
        assert "Error listing users" in result.output


class TestMapUserAdd:
    """Tests for map user-add command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map user add."""
        result = runner.invoke(
            app,
            [
                "map",
                "user-add",
                "--map-id",
                "test-uuid",
                "--username",
                "newuser",
                "--api-key",
                "key",
            ],
        )
        assert result.exit_code == 0
        mock_api.map_user_add.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map user add error handling."""
        mock_api.map_user_add.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "map",
                "user-add",
                "--map-id",
                "test-uuid",
                "--username",
                "newuser",
                "--api-key",
                "key",
            ],
        )
        assert result.exit_code == 1
        assert "Error adding user" in result.output


class TestMapUserDelete:
    """Tests for map user-delete command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful map user delete."""
        result = runner.invoke(
            app,
            [
                "map",
                "user-delete",
                "--map-id",
                "test-uuid",
                "--username",
                "olduser",
                "--api-key",
                "key",
            ],
        )
        assert result.exit_code == 0
        mock_api.map_user_delete.assert_called_once_with("test-uuid", "olduser", "key")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test map user delete error handling."""
        mock_api.map_user_delete.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "map",
                "user-delete",
                "--map-id",
                "test-uuid",
                "--username",
                "olduser",
                "--api-key",
                "key",
            ],
        )
        assert result.exit_code == 1
        assert "Error removing user" in result.output


# =============================================================================
# Marker Command Tests
# =============================================================================


class TestMarkerList:
    """Tests for marker list command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful marker list."""
        result = runner.invoke(app, ["marker", "list", "--map-id", "test-uuid"])
        assert result.exit_code == 0
        mock_api.marker_list.assert_called_once()

    def test_with_options(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test marker list with options."""
        result = runner.invoke(
            app,
            [
                "marker",
                "list",
                "--map-id",
                "test-uuid",
                "--show-expired",
                "--response-format",
                "geojson",
            ],
        )
        assert result.exit_code == 0
        mock_api.marker_list.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test marker list error handling."""
        mock_api.marker_list.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["marker", "list", "--map-id", "test-uuid"])
        assert result.exit_code == 1
        assert "Error listing markers" in result.output


class TestMarkerCreate:
    """Tests for marker create command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful marker creation."""
        result = runner.invoke(
            app,
            [
                "marker",
                "create",
                "--map-id",
                "test-uuid",
                "--map-token",
                "token",
                "--lat",
                "45.0",
                "--lng",
                "10.0",
                "--category-name",
                "Test",
            ],
        )
        assert result.exit_code == 0
        mock_api.marker_create.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test marker creation error handling."""
        mock_api.marker_create.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "marker",
                "create",
                "--map-id",
                "test-uuid",
                "--map-token",
                "token",
                "--lat",
                "45.0",
                "--lng",
                "10.0",
                "--category-name",
                "Test",
            ],
        )
        assert result.exit_code == 1
        assert "Error creating marker" in result.output


class TestMarkerEdit:
    """Tests for marker edit command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful marker edit."""
        result = runner.invoke(
            app,
            [
                "marker",
                "edit",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--marker-token",
                "token",
                "--description",
                "Updated",
            ],
        )
        assert result.exit_code == 0
        mock_api.marker_edit.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test marker edit error handling."""
        mock_api.marker_edit.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "marker",
                "edit",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--marker-token",
                "token",
            ],
        )
        assert result.exit_code == 1
        assert "Error editing marker" in result.output


class TestMarkerDelete:
    """Tests for marker delete command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful marker delete."""
        result = runner.invoke(
            app,
            [
                "marker",
                "delete",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--marker-token",
                "token",
            ],
        )
        assert result.exit_code == 0
        mock_api.marker_delete.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test marker delete error handling."""
        mock_api.marker_delete.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "marker",
                "delete",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--marker-token",
                "token",
            ],
        )
        assert result.exit_code == 1
        assert "Error deleting marker" in result.output


class TestMarkerSpam:
    """Tests for marker spam command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful spam report."""
        result = runner.invoke(
            app,
            [
                "marker",
                "spam",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--is-spam",
            ],
        )
        assert result.exit_code == 0
        mock_api.marker_spam.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test spam report error handling."""
        mock_api.marker_spam.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "marker",
                "spam",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--is-spam",
            ],
        )
        assert result.exit_code == 1
        assert "Error marking marker" in result.output


class TestMarkerLocationList:
    """Tests for marker location-list command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful location list."""
        result = runner.invoke(
            app,
            ["marker", "location-list", "--map-id", "test-uuid", "--marker-id", "123"],
        )
        assert result.exit_code == 0
        mock_api.marker_location_list.assert_called_once_with("test-uuid", "123")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test location list error handling."""
        mock_api.marker_location_list.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            ["marker", "location-list", "--map-id", "test-uuid", "--marker-id", "123"],
        )
        assert result.exit_code == 1
        assert "Error listing locations" in result.output


class TestMarkerLocationCreate:
    """Tests for marker location-create command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful location creation."""
        result = runner.invoke(
            app,
            [
                "marker",
                "location-create",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--lat",
                "45.0",
                "--lng",
                "10.0",
            ],
        )
        assert result.exit_code == 0
        mock_api.marker_location_create.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test location creation error handling."""
        mock_api.marker_location_create.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            [
                "marker",
                "location-create",
                "--map-id",
                "test-uuid",
                "--marker-id",
                "123",
                "--lat",
                "45.0",
                "--lng",
                "10.0",
            ],
        )
        assert result.exit_code == 1
        assert "Error creating location" in result.output


# =============================================================================
# Category Command Tests
# =============================================================================


class TestCategoryList:
    """Tests for category list command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful category list."""
        result = runner.invoke(app, ["category", "list"])
        assert result.exit_code == 0
        mock_api.category_list.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test category list error handling."""
        mock_api.category_list.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["category", "list"])
        assert result.exit_code == 1
        assert "Error listing categories" in result.output


class TestCategorySearch:
    """Tests for category search command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful category search."""
        result = runner.invoke(app, ["category", "search", "--query", "shark"])
        assert result.exit_code == 0
        mock_api.category_search.assert_called_once_with("shark")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test category search error handling."""
        mock_api.category_search.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["category", "search", "--query", "shark"])
        assert result.exit_code == 1
        assert "Error searching categories" in result.output


class TestCategoryRelated:
    """Tests for category related command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful related categories."""
        result = runner.invoke(app, ["category", "related", "--category-id", "123"])
        assert result.exit_code == 0
        mock_api.category_related.assert_called_once_with(123)

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test related categories error handling."""
        mock_api.category_related.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["category", "related", "--category-id", "123"])
        assert result.exit_code == 1
        assert "Error getting related categories" in result.output


# =============================================================================
# User Command Tests
# =============================================================================


class TestUserList:
    """Tests for user list command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful user list."""
        result = runner.invoke(app, ["user", "list"])
        assert result.exit_code == 0
        mock_api.user_list.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test user list error handling."""
        mock_api.user_list.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["user", "list"])
        assert result.exit_code == 1
        assert "Error listing users" in result.output


class TestUserGet:
    """Tests for user get command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful user get."""
        result = runner.invoke(app, ["user", "get", "--username", "testuser"])
        assert result.exit_code == 0
        mock_api.user_get.assert_called_once_with("testuser")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test user get error handling."""
        mock_api.user_get.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["user", "get", "--username", "testuser"])
        assert result.exit_code == 1
        assert "Error getting user" in result.output


# =============================================================================
# Me (Self) Command Tests
# =============================================================================


class TestMeGet:
    """Tests for me get command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful me get."""
        result = runner.invoke(app, ["me", "get", "--api-key", "key"])
        assert result.exit_code == 0
        mock_api.me_get.assert_called_once_with("key")

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test me get error handling."""
        mock_api.me_get.side_effect = _make_http_error("Server error")
        result = runner.invoke(app, ["me", "get", "--api-key", "key"])
        assert result.exit_code == 1
        assert "Error getting current user" in result.output


class TestMeUpdate:
    """Tests for me update command."""

    def test_success(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test successful me update."""
        result = runner.invoke(
            app,
            ["me", "update", "--api-key", "key", "--username", "newname"],
        )
        assert result.exit_code == 0
        mock_api.me_update.assert_called_once()

    def test_with_public_flag(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test me update with is_public flag."""
        result = runner.invoke(
            app,
            ["me", "update", "--api-key", "key", "--is-public"],
        )
        assert result.exit_code == 0
        mock_api.me_update.assert_called_once()

    def test_error(self, runner: CliRunner, mock_api: MagicMock) -> None:
        """Test me update error handling."""
        mock_api.me_update.side_effect = _make_http_error("Server error")
        result = runner.invoke(
            app,
            ["me", "update", "--api-key", "key", "--username", "newname"],
        )
        assert result.exit_code == 1
        assert "Error updating current user" in result.output
