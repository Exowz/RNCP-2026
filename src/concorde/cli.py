import typer

app = typer.Typer(help="Concorde CLI")


@app.command()
def version() -> None:
    """Affiche la version."""
    from concorde import __version__

    print(__version__)
