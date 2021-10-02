"""CLI frontend to cartes.io API."""
from typing import Optional

import typer
from requests.exceptions import HTTPError

from .cartes import Cartes, Permission, Privacy

app = typer.Typer()

map_app = typer.Typer()
app.add_typer(map_app, name="map")

marker_app = typer.Typer()
app.add_typer(marker_app, name="marker")

api = Cartes()


@map_app.command("get")
def map_get(map_id: str = typer.Option(..., help="Id of the map")):
    """Get a single map."""
    try:
        response = api.map_get(map_id)
        typer.echo(response)
    except HTTPError:
        typer.secho(
            f'Error getting map "{map_id}"', fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)


@map_app.command("create")
def create_map(
    title: Optional[str] = typer.Option(None, help="The title of the map"),
    slug: Optional[str] = typer.Option(
        None, help="The map slug. Currently un-used"
    ),
    description: Optional[str] = typer.Option(
        None, help="The description of the map and its purpose"
    ),
    privacy: Optional[Privacy] = typer.Option(
        None, help="The privacy level of the map: public, unlisted, private"
    ),
    users_can_create_markers: Optional[Permission] = typer.Option(
        None, help="The setting that defines who can create markers"
    ),
):
    """Create a map."""
    try:
        response = api.map_create(
            title, slug, description, privacy, users_can_create_markers
        )
        typer.echo(response)
    except HTTPError:
        typer.secho(
            f'Error creating map "{title}"', fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)


@map_app.command("delete")
def map_delete(
    token: str = typer.Option(..., help="Token"),
    map_id: str = typer.Option(..., help="Map id"),
):
    """Delete a single map."""
    try:
        response = api.map_delete(token, map_id)
        typer.echo(response)
    except HTTPError:
        typer.secho(
            f'Error deleting map "{map_id}"', fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)


@marker_app.command("list")
def marker_list(
    map_id: str = typer.Option(..., help="Map id"),
    show_expired: Optional[bool] = typer.Option(
        None, help="Show markers that have already expired"
    ),
):
    """Get all markers on a map."""
    try:
        response = api.marker_list(map_id)
        typer.echo(response)
    except HTTPError:
        typer.secho("Error listing markers", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@marker_app.command("create")
def marker_create(
    map_token: str = typer.Option(..., help="Map token"),
    map_id: str = typer.Option(..., help="Map id"),
    lat: float = typer.Option(
        ..., min=-90, max=90, help="The lat position of the marker"
    ),
    lng: float = typer.Option(
        ..., min=-90, max=90, help="The lng position of the marker"
    ),
    category: Optional[int] = typer.Option(
        None,
        help="Category ID. Use category_name if you don't know the ID",
    ),
    category_name: str = typer.Option(None, help="Category name"),
    description: str = typer.Option(None, help="Marker description"),
):
    """Create a marker on a map."""
    try:
        response = api.marker_create(
            map_token,
            map_id,
            lat,
            lng,
            category,
            category_name,
            description,
        )
        typer.echo(response)
    except (HTTPError, ValueError):
        typer.secho(
            f"Error creating marker at ({lat}, {lng}).",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)


@marker_app.command("edit")
def marker_edit(
    token: str = typer.Option(..., help="Marker token"),
    map_id: str = typer.Option(..., help="Map id"),
    marker_id: str = typer.Option(..., help="Marker id"),
    description: str = typer.Option(None, help="Marker description"),
):
    """Edit a marker on a map."""
    try:
        response = api.marker_edit(token, map_id, marker_id, description)
        typer.echo(response)
    except HTTPError:
        typer.secho(
            f"Error editing marker {marker_id}.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)


@marker_app.command("delete")
def marker_delete(
    token: str = typer.Option(..., help="Token"),
    map_id: str = typer.Option(..., help="Map id"),
    marker_id: str = typer.Option(..., help="Marker id"),
):
    """Delete a marker on a map."""
    try:
        response = api.marker_delete(token, map_id, marker_id)
        typer.echo(response)
    except HTTPError:
        typer.secho(
            f"Error deleting marker {marker_id}.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
