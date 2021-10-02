"""Tool to create maps with markers using cartes.io API."""
import typer
from requests.exceptions import HTTPError

from cartes import Cartes

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


if __name__ == "__main__":  # pragma: no cover
    app()
