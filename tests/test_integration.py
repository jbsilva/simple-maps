"""
Integration tests for the Cartes.io API.

These tests make real API calls and require the CARTES_API_KEY environment variable.
Run with: pytest -m integration tests/test_integration.py -n0 --no-cov

Note: Integration tests are excluded from regular test runs and must be run with -m integration
flag. They are also run sequentially (-n0) to avoid rate limiting.
"""

import os
import time
import uuid

import pytest
from httpx import HTTPStatusError
from inline_snapshot import snapshot
from pydantic import ValidationError

from simple_maps.cartes import (
    Cartes,
    MapCreatePayload,
    MarkerCreatePayload,
    Privacy,
)


# Mark all tests as integration tests
pytestmark = pytest.mark.integration

# Rate limit delay between API calls (in seconds)
# Authenticated requests have more permissive rate limits
RATE_LIMIT_DELAY = 0.5


def wait_for_rate_limit() -> None:
    """Wait to avoid rate limiting."""
    time.sleep(RATE_LIMIT_DELAY)


@pytest.fixture(scope="module")
def api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("CARTES_API_KEY", "")
    if not key:
        msg = "CARTES_API_KEY environment variable not set"
        raise ValueError(msg)
    return key


@pytest.fixture(scope="module")
def api() -> Cartes:
    """Create a Cartes API instance."""
    return Cartes()


# =============================================================================
# Category Tests (Read-only, no auth needed)
# =============================================================================


class TestCategoryIntegration:
    """Integration tests for category endpoints."""

    def test_category_list(self, api: Cartes, api_key: str) -> None:
        """Test listing all categories."""
        result = api.category_list(api_key)

        # The API returns a list of categories
        assert isinstance(result, list)
        if result:
            first_category = result[0]
            assert isinstance(first_category, dict)
            assert "id" in first_category
            assert "name" in first_category

    def test_category_search(self, api: Cartes, api_key: str) -> None:
        """Test searching categories."""
        wait_for_rate_limit()
        result = api.category_search("restaurant", api_key)

        # The API returns a list of matching categories
        assert isinstance(result, list)


# =============================================================================
# User Tests (Read-only)
# =============================================================================


class TestUserIntegration:
    """Integration tests for user endpoints."""

    def test_user_list(self, api: Cartes, api_key: str) -> None:
        """Test listing public users."""
        wait_for_rate_limit()
        result = api.user_list(api_key)

        # Should return some kind of response
        assert isinstance(result, dict)
        assert "data" in result

    def test_me_get(self, api: Cartes, api_key: str) -> None:
        """Test getting current authenticated user."""
        wait_for_rate_limit()
        result = api.me_get(api_key)

        # Should return user data
        assert isinstance(result, dict)


# =============================================================================
# Map Tests (Read-only first, then write operations)
# =============================================================================


class TestMapIntegration:
    """Integration tests for map endpoints."""

    def test_map_list(self, api: Cartes, api_key: str) -> None:
        """Test listing all public maps."""
        wait_for_rate_limit()
        result = api.map_list(api_key=api_key)

        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_map_search(self, api: Cartes, api_key: str) -> None:
        """Test searching maps."""
        wait_for_rate_limit()
        result = api.map_search("test", api_key)

        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_map_lifecycle(self, api: Cartes, api_key: str) -> None:
        """Test the full map lifecycle: create, get, edit, delete."""
        wait_for_rate_limit()

        # 1. Create a map
        unique_id = uuid.uuid4().hex[:8]
        payload = MapCreatePayload(
            title=f"Integration Test Map {unique_id}",
            description="A map created by integration tests - safe to delete",
            privacy=Privacy.UNLISTED,
        )
        created = api.map_create(payload, api_key=api_key)

        assert isinstance(created, dict)
        assert "uuid" in created
        assert "token" in created
        map_uuid = str(created["uuid"])
        map_token = str(created["token"])

        try:
            # 2. Get the map
            wait_for_rate_limit()
            fetched = api.map_get(map_uuid, api_key)
            assert isinstance(fetched, dict)
            assert fetched["uuid"] == map_uuid

            # 3. Edit the map
            wait_for_rate_limit()
            new_description = f"Updated description {uuid.uuid4().hex[:8]}"
            edit_payload = MapCreatePayload(description=new_description)
            edited = api.map_edit(
                map_uuid,
                edit_payload,
                map_token=map_token,
                api_key=api_key,
            )
            assert isinstance(edited, dict)
            assert edited["description"] == new_description

        finally:
            # 4. Delete the map (cleanup)
            wait_for_rate_limit()
            api.map_delete(map_token, map_uuid, api_key)


# =============================================================================
# Marker Tests
# =============================================================================


class TestMarkerIntegration:
    """Integration tests for marker endpoints."""

    def test_marker_lifecycle(self, api: Cartes, api_key: str) -> None:
        """Test the full marker lifecycle: create, list, edit, delete."""
        wait_for_rate_limit()

        # First create a map for markers
        unique_id = uuid.uuid4().hex[:8]
        map_payload = MapCreatePayload(
            title=f"Marker Test Map {unique_id}",
            privacy=Privacy.UNLISTED,
        )
        created_map = api.map_create(map_payload, api_key=api_key)
        assert isinstance(created_map, dict)
        map_uuid = str(created_map["uuid"])
        map_token = str(created_map["token"])

        try:
            # 1. Create a marker
            wait_for_rate_limit()
            marker_payload = MarkerCreatePayload(
                map_token=map_token,
                lat=40.7128,
                lng=-74.0060,
                category_name="Test Category",
                description="Integration test marker",
            )
            created = api.marker_create(map_uuid, marker_payload, api_key=api_key)

            assert isinstance(created, dict)
            assert "id" in created
            assert "token" in created
            marker_id = str(created["id"])
            marker_token = str(created["token"])

            # 2. List markers on the map
            wait_for_rate_limit()
            markers = api.marker_list(map_uuid, api_key=api_key)
            # The API returns a dict that may have marker data
            assert markers is not None

            # 3. Edit the marker
            wait_for_rate_limit()
            new_description = "Updated marker description"
            api.marker_edit(
                marker_token,
                map_uuid,
                marker_id,
                new_description,
                api_key=api_key,
            )

            # 4. Delete the marker
            wait_for_rate_limit()
            api.marker_delete(marker_token, map_uuid, marker_id, api_key=api_key)

        finally:
            # Cleanup: delete the map
            wait_for_rate_limit()
            api.map_delete(map_token, map_uuid, api_key)


# =============================================================================
# Snapshot Tests (Verify response structure)
# =============================================================================


class TestSnapshotIntegration:
    """Integration tests using inline-snapshot for response structure verification."""

    def test_user_list_structure(self, api: Cartes, api_key: str) -> None:
        """Verify user list response structure."""
        wait_for_rate_limit()
        result = api.user_list(api_key)

        assert isinstance(result, dict)
        assert "data" in result
        data = result["data"]
        assert isinstance(data, list)

        # Pagination info may be in "meta" key
        if "meta" in result:
            meta = result["meta"]
            assert isinstance(meta, dict)
            assert "current_page" in meta
            assert "per_page" in meta
            assert "total" in meta

    def test_map_list_structure(self, api: Cartes, api_key: str) -> None:
        """Verify map list response structure."""
        wait_for_rate_limit()
        result = api.map_list(api_key=api_key)

        assert isinstance(result, dict)
        # Check that essential keys exist
        assert "data" in result
        # Pagination info may be in "meta" key
        if "meta" in result:
            meta = result["meta"]
            assert isinstance(meta, dict)
            assert "current_page" in meta

    def test_map_create_response_keys(self, api: Cartes, api_key: str) -> None:
        """Verify map create response has expected fields."""
        wait_for_rate_limit()
        unique_id = uuid.uuid4().hex[:8]
        payload = MapCreatePayload(
            title=f"Snapshot Test {unique_id}",
            privacy=Privacy.UNLISTED,
        )
        result = api.map_create(payload, api_key=api_key)

        try:
            assert isinstance(result, dict)
            # Verify expected keys exist
            assert "uuid" in result
            assert "token" in result
            assert "title" in result
            assert "privacy" in result

            # Verify privacy value using snapshot
            assert result["privacy"] == snapshot("unlisted")

        finally:
            # Cleanup
            wait_for_rate_limit()
            if "token" in result and "uuid" in result:
                api.map_delete(str(result["token"]), str(result["uuid"]), api_key)


# =============================================================================
# Map Claim Tests (Requires authentication)
# =============================================================================


class TestMapClaimIntegration:
    """Integration tests for map claiming functionality."""

    def test_map_claim_and_unclaim(self, api: Cartes, api_key: str) -> None:
        """Test claiming and unclaiming a map."""
        wait_for_rate_limit()

        # Create a new map to claim
        unique_id = uuid.uuid4().hex[:8]
        payload = MapCreatePayload(
            title=f"Claim Test Map {unique_id}",
            privacy=Privacy.UNLISTED,
        )
        new_map = api.map_create(payload)
        assert isinstance(new_map, dict)
        map_uuid = str(new_map["uuid"])
        map_token = str(new_map["token"])

        try:
            # Claim the map
            wait_for_rate_limit()
            api.map_claim(map_uuid, map_token, api_key)

            # Unclaim the map
            wait_for_rate_limit()
            api.map_unclaim(map_uuid, api_key)

        finally:
            # Clean up: delete the map
            wait_for_rate_limit()
            api.map_delete(map_token, map_uuid, api_key)


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    def test_map_get_not_found(self, api: Cartes, api_key: str) -> None:
        """Test getting a non-existent map returns error."""
        wait_for_rate_limit()
        with pytest.raises(HTTPStatusError):
            api.map_get("non-existent-uuid-12345", api_key)

    def test_marker_create_invalid_coordinates(self) -> None:
        """Test creating a marker with invalid coordinates raises validation error."""
        with pytest.raises(ValidationError):
            MarkerCreatePayload(
                map_token="fake-token",
                lat=200.0,  # Invalid latitude
                lng=0.0,
                category_name="Test",
            )
