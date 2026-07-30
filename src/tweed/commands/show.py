import typer

from tweed.config import Config
from tweed.vault import Vault
from tweed.commands.new import register_item_commands

app=typer.Typer()


@app.command()
def show(
    name: str,
    vault: str | None = typer.Option(None),
):

    """Display the contents"""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    note = v.resolve(name)

    typer.echo(f"# {note.title}")
    typer.echo()

    typer.echo(f"Type: {note.kind}")
    typer.echo(f"ID:   {note.id}")


    backlinks = v.backlinks(note)

    if backlinks:
        typer.echo()
        typer.echo("## Backlinks")
        typer.echo()

        for other in backlinks: 
            typer.echo(f"- {other.kind}: {other.title}")


register_item_commands(app)
