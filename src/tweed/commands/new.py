import typer
from tweed.services.create import create_item
from tweed.config import Config
from tweed.registry import REGISTRY
from tweed.vault import Vault

app = typer.Typer(help="Create new items.")

def register_item_commands(app: typer.Typer):
    for kind in REGISTRY:

        def command(
            name: str,
            vault: str | None = typer.Option(
                None,
                help="Override configured vault.",
            ),
            *,
            _kind=kind,
        ):

            config = Config()

            vault = vault or config.vault

            if vault is None:
                typer.echo(
                "No vault configured.\n"
                "Create ~/.config/tweed/config.toml "
                "or specify --vault."
            )
                raise typer.Exit(1)

            v = Vault(vault)

            try:
                note = create_item(v, _kind, name)
            except ValueError as e:
                typer.echo(str(e))
                raise typer.Exit(1)

            typer.echo(f"Created {note.path}")

        command.__name__ = kind
        command.__doc__ = f"Create a new {kind}."
    
        app.command(name=kind)(command)

register_item_commands(app)
