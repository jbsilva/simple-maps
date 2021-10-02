"""Tool to create maps with markers using cartes.io API."""
from typing import Optional

import typer
from requests.exceptions import HTTPError

from cartes import Cartes, Permission, Privacy

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


if __name__ == "__main__":  # pragma: no cover
    app()
