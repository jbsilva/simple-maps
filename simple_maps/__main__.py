"""Tool to create maps with markers using cartes.io API."""
import typer

from cartes import Cartes

app = typer.Typer()

map_app = typer.Typer()
app.add_typer(map_app, name="map")

marker_app = typer.Typer()
app.add_typer(marker_app, name="marker")

api = Cartes()


if __name__ == "__main__":  # pragma: no cover
    app()
