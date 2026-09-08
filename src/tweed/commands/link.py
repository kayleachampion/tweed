import typer

from tweed.config import Config
from tweed.services.link import link
from tweed.vault import Vault

app = typer.Typer(help="Create links.")


@app.command()
def link_command(
    name1: str,
    name2: str,
    vault: str | None = typer.Option(None),
):
    config = Config()
    vault = vault or config.vault

    v = Vault(vault)

    a = v.resolve(name1)
    b = v.resolve(name2)

    link(a, b)

    typer.echo("Linked.")
