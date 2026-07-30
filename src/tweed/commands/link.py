import typer

from tweed.config import Config
from tweed.vault import Vault
from tweed.commands.new import register_item_commands


def add_link(note, target_id):
    links = note.get("links", [])

    if target_id not in links:
        links.append(target_id)

    note["links"] = sorted(links)

app = typer.Typer(help="Create links.")

@app.command()
def link(
    name1: str,
    name2: str,
    vault: str | None = typer.Option(None),
):
    """Link two items."""

    config = Config()

    vault = vault or config.vault

    v = Vault(vault)

    a = v.load(name1)
    b = v.load(name2)

    add_link(a, b["id"])
    add_link(b, a["id"])

    a.save()
    b.save()

    typer.echo("Linked.")


register_item_commands(app)
