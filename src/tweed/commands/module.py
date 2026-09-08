import typer

from tweed.config import Config
from tweed.services.attach import attach_module
from tweed.cli_completion import complete_modules
from tweed.services.create import create_item
from tweed.vault import Vault

app = typer.Typer(help="Manage modules.")


@app.command("create")
def create(
    module_name: str,
    vault: str | None = typer.Option(None),
):
    """Create a new module."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        module = create_item(v, "module", module_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    typer.echo(f"Created module '{module.title}'.")


@app.command("add")
def add(
    owner_name: str,
    module_name: str,
    vault: str | None = typer.Option(None),
):
    """Attach a module to an item."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        owner = v.resolve(owner_name)
        module = v.resolve(module_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    added = attach_module(v, owner, module)

    if added:
        typer.echo(f"Attached module '{module.title}' to '{owner.title}'.")
    else: 
        typer.echo(f"Module '{module.title}' is already attached to '{owner.title}'.")




@app.command("list")
def list_modules(
    owner_name: str,
    vault: str | None = typer.Option(None),
):
    """List modules attached to an item."""

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

    for module_id in owner.get("modules", []):
        module = v.load_by_id(module_id)
        typer.echo(module.title)

def show_task_tree(vault, task_id, indent=2):
    """Display a task and its subtasks recursively."""

    try:
        task = vault.load_by_id(task_id)
    except FileNotFoundError:
        return

    status = task.get("status", "")
    due = task.get("due", "")

    typer.echo(
        f"{' ' * indent}{task.title}\t{status}\t{due}"
    )

    for note in vault.find():
        if (
            note.get("type") == "task"
            and note.get("parent") == task_id
        ):
            show_task_tree(
                vault,
                note["id"],
                indent + 2,
            )


def show_task_definitions(tasks, indent=2):
    for task in tasks:
        typer.echo(" " * indent + task["title"])

        children = task.get("tasks", [])
        if children:
            show_task_definitions(children, indent + 2)


@app.command("show")
def show_module(
    module_name: str = typer.Argument(
        ...,
        shell_complete=complete_modules,
    ),
    vault: str | None = typer.Option(None),
):
    """Show a module and its tasks."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        module = v.resolve(module_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if module.get("type") != "module":
        typer.echo(f"'{module_name}' is not a module.")
        raise typer.Exit(1)

    typer.echo(f"Title:  {module.title}")
    typer.echo(f"Status: {module.get('status', '')}")

    tasks = module.get("tasks", [])

    typer.echo()
    typer.echo("Tasks:")

    if tasks:
        show_task_definitions(tasks)
    else:
        typer.echo("  (none)")
