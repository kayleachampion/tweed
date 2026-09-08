import typer

from tweed.config import Config
from tweed.services.event import create_event
from tweed.vault import Vault

app = typer.Typer(help="Manage events.")


@app.command("add")
def add(
    owner_name: str,
    date: str,
    start_time: str,
    event_type: str = typer.Option("meeting", "--type"),
    end_time: str | None = typer.Option(None),
    location: str | None = typer.Option(None),
    vault: str | None = typer.Option(None),
):
    """Create an event attached to an item."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        owner = v.resolve(owner_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    event = create_event(
        v,
        owner,
        date,
        start_time,
        event_type,
        end_time,
        location,
    )

    typer.echo(f"Created event: {event.title}")


@app.command("list")
def list_events(
    owner_name: str,
    vault: str | None = typer.Option(None),
):
    """List events attached to an item."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        owner = v.resolve(owner_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    for link_id in owner.get("links", []):
        if link_id.startswith("event:"):
            event = v.load_by_id(link_id)
            typer.echo(event.title)
