import typer

from tweed.config import Config
from tweed.vault import Vault

app = typer.Typer(help="Lists everything matching that query")


@app.command()
def list_items(
    query: list[str] = typer.Argument(None),
    vault: str | None = typer.Option(None),
):
    """List items matching a query."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    for note in v.find(query or []):
        title = note.get("title", note.path.stem)
        kind = note.get("type", "?")
        typer.echo(f"{kind:10} {title}")
