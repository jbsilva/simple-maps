"""
Command-line interface for the Cartes.io API.

This module provides a CLI frontend for interacting with the Cartes.io mapping
platform. It supports all API operations including creating maps, adding markers,
and managing user permissions.

Example:
    $ simple_maps map list
    $ simple_maps map create --title "My Map" --privacy public
    $ simple_maps marker create --map-id UUID --lat 40.7 --lng -74.0

"""
# ruff: noqa: PLR0913

import httpx
import typer

from .cartes import (
    Cartes,
    MapCreatePayload,
    MapListParams,
    MarkerCreatePayload,
    MarkerLocationPayload,
    Permission,
    Privacy,
)


# =============================================================================
# Shared option definitions
# =============================================================================

MAP_ID_HELP = "Map UUID"
API_KEY_HELP = "API key for authentication"
USERNAME_HELP = "Username"

MAP_GET_ID_OPTION = typer.Option(..., help="UUID of the map to retrieve")
MAP_ID_OPTION = typer.Option(..., help=MAP_ID_HELP)
MAP_TOKEN_OPTION = typer.Option(..., "--map-token", "--token", help="Map edit token")
MAP_TOKEN_OPTIONAL = typer.Option(None, "--map-token", "--token", help="Map edit token")
MARKER_TOKEN_OPTION = typer.Option(..., "--marker-token", "--token", help="Marker edit token")
MARKER_TOKEN_OPTIONAL = typer.Option(None, "--marker-token", help="Marker edit token")
API_KEY_OPTION = typer.Option(None, help=API_KEY_HELP)
API_KEY_REQUIRED = typer.Option(..., help=API_KEY_HELP)
MAP_TITLE_OPTION = typer.Option(None, help="Title of the map")
MAP_SLUG_OPTION = typer.Option(None, help="URL slug for the map (currently unused)")
MAP_DESCRIPTION_OPTION = typer.Option(None, help="Description of the map")
MAP_PRIVACY_OPTION = typer.Option(None, help="Privacy level: public, unlisted, private")
MAP_USERS_CAN_CREATE_MARKERS_OPTION = typer.Option(
    None,
    help="Who can create markers: yes, no, only_logged_in",
)
MARKER_SHOW_EXPIRED_OPTION = typer.Option(None, help="Include expired markers")
MARKER_RESPONSE_FORMAT_OPTION = typer.Option(None, help="Response format (e.g., 'geojson')")
MARKER_LAT_OPTION = typer.Option(..., min=-90, max=90, help="Latitude (-90 to 90)")
MARKER_LNG_OPTION = typer.Option(..., min=-180, max=180, help="Longitude (-180 to 180)")
MARKER_CATEGORY_OPTION = typer.Option(None, help="Category ID")
MARKER_CATEGORY_NAME_OPTION = typer.Option(None, help="Category name")
MARKER_DESCRIPTION_OPTION = typer.Option(None, help="Marker description")
MARKER_ID_OPTION = typer.Option(..., help="Marker ID")
USERNAME_OPTION = typer.Option(..., help=USERNAME_HELP)
QUERY_OPTION = typer.Option(..., help="Search query")

# =============================================================================
# CLI Application Setup
# =============================================================================

app = typer.Typer(help="CLI for the Cartes.io mapping platform.")

map_app = typer.Typer(help="Map management commands.")
app.add_typer(map_app, name="map")

marker_app = typer.Typer(help="Marker management commands.")
app.add_typer(marker_app, name="marker")

category_app = typer.Typer(help="Category commands.")
app.add_typer(category_app, name="category")

user_app = typer.Typer(help="User commands.")
app.add_typer(user_app, name="user")

me_app = typer.Typer(help="Authenticated user commands.")
app.add_typer(me_app, name="me")

api = Cartes()


def _error(message: str) -> None:
    """Print an error message to stderr."""
    typer.secho(message, fg=typer.colors.RED, err=True)


# =============================================================================
# Map Commands
# =============================================================================


@map_app.command("list")
def map_list(
    order_by: str | None = typer.Option(None, help="Sort field"),
    query: str | None = typer.Option(None, help="Filter query"),
    response_format: str | None = typer.Option(None, help="Response format"),
    api_key: str | None = API_KEY_OPTION,
    *,
    with_mine: bool | None = typer.Option(None, help="Include your maps"),
) -> None:
    """List all public maps."""
    try:
        response = api.map_list(
            MapListParams(
                order_by=order_by,
                query=query,
                response_format=response_format,
                with_mine=with_mine,
            ),
            api_key,
        )
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error listing maps")
        raise typer.Exit(code=1) from err


@map_app.command("search")
def map_search(query: str = QUERY_OPTION) -> None:
    """Search public maps by query."""
    try:
        response = api.map_search(query)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error searching maps")
        raise typer.Exit(code=1) from err


@map_app.command("get")
def map_get(map_id: str = MAP_GET_ID_OPTION) -> None:
    """Get a single map by UUID."""
    try:
        response = api.map_get(map_id)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error getting map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("static-image")
def map_static_image(
    map_id: str = MAP_ID_OPTION,
    zoom: int | None = typer.Option(None, min=2, max=19, help="Zoom level (2-19)"),
) -> None:
    """Get a map's static image URL."""
    try:
        response = api.map_static_image(map_id, zoom)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error getting static image for map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("create")
def map_create(
    title: str | None = MAP_TITLE_OPTION,
    slug: str | None = MAP_SLUG_OPTION,
    description: str | None = MAP_DESCRIPTION_OPTION,
    privacy: Privacy | None = MAP_PRIVACY_OPTION,
    users_can_create_markers: Permission | None = MAP_USERS_CAN_CREATE_MARKERS_OPTION,
    api_key: str | None = API_KEY_OPTION,
) -> None:
    """Create a new map."""
    try:
        response = api.map_create(
            MapCreatePayload(
                title=title,
                slug=slug,
                description=description,
                privacy=privacy,
                users_can_create_markers=users_can_create_markers,
            ),
            api_key,
        )
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error creating map "{title}"')
        raise typer.Exit(code=1) from err


@map_app.command("edit")
def map_edit(
    map_id: str = MAP_ID_OPTION,
    map_token: str | None = MAP_TOKEN_OPTIONAL,
    title: str | None = MAP_TITLE_OPTION,
    slug: str | None = MAP_SLUG_OPTION,
    description: str | None = MAP_DESCRIPTION_OPTION,
    privacy: Privacy | None = MAP_PRIVACY_OPTION,
    users_can_create_markers: Permission | None = MAP_USERS_CAN_CREATE_MARKERS_OPTION,
    api_key: str | None = API_KEY_OPTION,
) -> None:
    """Edit an existing map."""
    try:
        response = api.map_edit(
            map_id,
            MapCreatePayload(
                title=title,
                slug=slug,
                description=description,
                privacy=privacy,
                users_can_create_markers=users_can_create_markers,
            ),
            map_token,
            api_key,
        )
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error editing map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("delete")
def map_delete(
    map_token: str = MAP_TOKEN_OPTION,
    map_id: str = MAP_ID_OPTION,
    api_key: str | None = API_KEY_OPTION,
) -> None:
    """Delete a map."""
    try:
        response = api.map_delete(map_token, map_id, api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error deleting map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("claim")
def map_claim(
    map_id: str = MAP_ID_OPTION,
    map_token: str = MAP_TOKEN_OPTION,
    api_key: str = API_KEY_REQUIRED,
) -> None:
    """Claim an anonymous map to your account."""
    try:
        response = api.map_claim(map_id, map_token, api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error claiming map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("unclaim")
def map_unclaim(
    map_id: str = MAP_ID_OPTION,
    api_key: str = API_KEY_REQUIRED,
) -> None:
    """Release ownership of a map."""
    try:
        response = api.map_unclaim(map_id, api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error un-claiming map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("user-list")
def map_user_list(
    map_id: str = MAP_ID_OPTION,
    api_key: str = API_KEY_REQUIRED,
) -> None:
    """List users with access to a map."""
    try:
        response = api.map_user_list(map_id, api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error listing users for map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("user-add")
def map_user_add(
    map_id: str = MAP_ID_OPTION,
    username: str = USERNAME_OPTION,
    api_key: str = API_KEY_REQUIRED,
    *,
    can_create_markers: bool | None = typer.Option(None, help="Allow marker creation"),
) -> None:
    """Add a user to a map."""
    try:
        response = api.map_user_add(
            map_id,
            username,
            api_key,
            can_create_markers=can_create_markers,
        )
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error adding user "{username}" to map "{map_id}"')
        raise typer.Exit(code=1) from err


@map_app.command("user-delete")
def map_user_delete(
    map_id: str = MAP_ID_OPTION,
    username: str = USERNAME_OPTION,
    api_key: str = API_KEY_REQUIRED,
) -> None:
    """Remove a user from a map."""
    try:
        response = api.map_user_delete(map_id, username, api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error removing user "{username}" from map "{map_id}"')
        raise typer.Exit(code=1) from err


# =============================================================================
# Marker Commands
# =============================================================================


@marker_app.command("list")
def marker_list(
    map_id: str = MAP_ID_OPTION,
    *,
    show_expired: bool | None = MARKER_SHOW_EXPIRED_OPTION,
    response_format: str | None = MARKER_RESPONSE_FORMAT_OPTION,
) -> None:
    """List all markers on a map."""
    try:
        response = api.marker_list(
            map_id,
            show_expired=show_expired,
            response_format=response_format,
        )
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error listing markers")
        raise typer.Exit(code=1) from err


@marker_app.command("create")
def marker_create(
    map_token: str = MAP_TOKEN_OPTION,
    map_id: str = MAP_ID_OPTION,
    lat: float = MARKER_LAT_OPTION,
    lng: float = MARKER_LNG_OPTION,
    category: int | None = MARKER_CATEGORY_OPTION,
    category_name: str | None = MARKER_CATEGORY_NAME_OPTION,
    description: str | None = MARKER_DESCRIPTION_OPTION,
    api_key: str | None = API_KEY_OPTION,
) -> None:
    """Create a marker on a map."""
    try:
        response = api.marker_create(
            map_id,
            MarkerCreatePayload(
                map_token=map_token,
                lat=lat,
                lng=lng,
                category=category,
                category_name=category_name,
                description=description,
            ),
            api_key,
        )
        typer.echo(response)
    except (httpx.HTTPStatusError, ValueError) as err:
        _error(f"Error creating marker at ({lat}, {lng})")
        raise typer.Exit(code=1) from err


@marker_app.command("edit")
def marker_edit(
    marker_token: str = MARKER_TOKEN_OPTION,
    map_id: str = MAP_ID_OPTION,
    marker_id: str = MARKER_ID_OPTION,
    description: str | None = MARKER_DESCRIPTION_OPTION,
    api_key: str | None = API_KEY_OPTION,
) -> None:
    """Edit a marker's description."""
    try:
        response = api.marker_edit(marker_token, map_id, marker_id, description, api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f"Error editing marker {marker_id}")
        raise typer.Exit(code=1) from err


@marker_app.command("delete")
def marker_delete(
    marker_token: str = MARKER_TOKEN_OPTION,
    map_id: str = MAP_ID_OPTION,
    marker_id: str = MARKER_ID_OPTION,
    api_key: str | None = API_KEY_OPTION,
) -> None:
    """Delete a marker."""
    try:
        response = api.marker_delete(marker_token, map_id, marker_id, api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f"Error deleting marker {marker_id}")
        raise typer.Exit(code=1) from err


@marker_app.command("spam")
def marker_spam(
    map_id: str = MAP_ID_OPTION,
    marker_id: str = MARKER_ID_OPTION,
    map_token: str | None = MAP_TOKEN_OPTIONAL,
    api_key: str | None = API_KEY_OPTION,
    *,
    is_spam: bool = typer.Option(..., help="Mark as spam"),
) -> None:
    """Mark or unmark a marker as spam."""
    try:
        response = api.marker_spam(
            map_id,
            marker_id,
            is_spam=is_spam,
            map_token=map_token,
            api_key=api_key,
        )
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f"Error marking marker {marker_id} as spam")
        raise typer.Exit(code=1) from err


@marker_app.command("location-list")
def marker_location_list(
    map_id: str = MAP_ID_OPTION,
    marker_id: str = MARKER_ID_OPTION,
) -> None:
    """Get location history for a marker."""
    try:
        response = api.marker_location_list(map_id, marker_id)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f"Error listing locations for marker {marker_id}")
        raise typer.Exit(code=1) from err


@marker_app.command("location-create")
def marker_location_create(
    map_id: str = MAP_ID_OPTION,
    marker_id: str = MARKER_ID_OPTION,
    lat: float = MARKER_LAT_OPTION,
    lng: float = MARKER_LNG_OPTION,
    marker_token: str | None = MARKER_TOKEN_OPTIONAL,
    zoom: float | None = typer.Option(None, min=0, max=20, help="Zoom level"),
    elevation: float | None = typer.Option(None, help="Elevation in meters"),
    heading: float | None = typer.Option(None, min=0, max=359, help="Heading (0-359)"),
    pitch: float | None = typer.Option(None, min=-90, max=90, help="Pitch (-90 to 90)"),
    roll: float | None = typer.Option(None, min=-180, max=180, help="Roll (-180 to 180)"),
    speed: float | None = typer.Option(None, help="Speed in m/s"),
    api_key: str | None = API_KEY_OPTION,
) -> None:
    """Add a location to a marker's history."""
    try:
        response = api.marker_location_create(
            map_id,
            marker_id,
            MarkerLocationPayload(
                lat=lat,
                lng=lng,
                zoom=zoom,
                elevation=elevation,
                heading=heading,
                pitch=pitch,
                roll=roll,
                speed=speed,
            ),
            marker_token,
            api_key,
        )
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f"Error creating location for marker {marker_id}")
        raise typer.Exit(code=1) from err


# =============================================================================
# Category Commands
# =============================================================================


@category_app.command("list")
def category_list() -> None:
    """List all categories."""
    try:
        response = api.category_list()
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error listing categories")
        raise typer.Exit(code=1) from err


@category_app.command("search")
def category_search(query: str = QUERY_OPTION) -> None:
    """Search categories by name."""
    try:
        response = api.category_search(query)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error searching categories")
        raise typer.Exit(code=1) from err


@category_app.command("related")
def category_related(
    category_id: int = typer.Option(..., help="Category ID"),
) -> None:
    """Get related categories."""
    try:
        response = api.category_related(category_id)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f"Error getting related categories for {category_id}")
        raise typer.Exit(code=1) from err


# =============================================================================
# User Commands
# =============================================================================


@user_app.command("list")
def user_list() -> None:
    """List all public users."""
    try:
        response = api.user_list()
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error listing users")
        raise typer.Exit(code=1) from err


@user_app.command("get")
def user_get(username: str = USERNAME_OPTION) -> None:
    """Get a public user's profile."""
    try:
        response = api.user_get(username)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error(f'Error getting user "{username}"')
        raise typer.Exit(code=1) from err


# =============================================================================
# Self (Me) Commands
# =============================================================================


@me_app.command("get")
def me_get(api_key: str = API_KEY_REQUIRED) -> None:
    """Get your profile."""
    try:
        response = api.me_get(api_key)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error getting current user")
        raise typer.Exit(code=1) from err


@me_app.command("update")
def me_update(
    api_key: str = API_KEY_REQUIRED,
    username: str | None = typer.Option(None, help="New username"),
    *,
    is_public: bool | None = typer.Option(None, help="Make profile public"),
) -> None:
    """Update your profile."""
    try:
        response = api.me_update(api_key, username=username, is_public=is_public)
        typer.echo(response)
    except httpx.HTTPStatusError as err:
        _error("Error updating current user")
        raise typer.Exit(code=1) from err
