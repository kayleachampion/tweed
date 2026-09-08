import typer

from tweed.config import Config
from tweed.vault import Vault
from tweed.cli_completion import complete_courses, complete_offerings

app = typer.Typer(help="Manage course offerings.")

@app.command("list")
def list_offerings(
    course_name: str = typer.Argument(
       ...,
        shell_complete=complete_courses,
    ),
    vault: str | None = typer.Option(None),
):
    """List offerings of a course."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        course = v.resolve(course_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    for link_id in course.get("links", []):
        if link_id.startswith("offering:"):
            offering = v.load_by_id(link_id)
            typer.echo(offering.title)


@app.command("show")
def show_offering(
    offering_name: str = typer.Argument(
        ...,
        shell_complete=complete_offerings,
    ),
    vault: str | None = typer.Option(None),
):
    """Show an offering, its modules, and their tasks."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        offering = v.resolve(offering_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if offering.get("type") != "offering":
        typer.echo(f"'{offering_name}' is not an offering.")
        raise typer.Exit(1)

    typer.echo(f"Title:  {offering.title}")
    typer.echo(f"Status: {offering.get('status', '')}")

    module_ids = [
        link_id
        for link_id in (offering.get("links") or [])
        if link_id.startswith("module:")
    ]

    modules = []

    for module_id in module_ids:
        try:
            modules.append(v.load_by_id(module_id))
        except FileNotFoundError:
            continue

    if modules:
        typer.echo()
        typer.echo("Modules:")

    for module in modules:
        typer.echo()
        typer.echo(f"  {module.title}")

        tasks = [
            task
            for task in v.find()
            if (
                task.get("type") == "task"
                and task.get("owner") == offering.id
                and task.get("module") == module.id
            )
        ]

        root_tasks = [
            task
            for task in tasks
            if not task.get("parent")
        ]

        for task in root_tasks:
            show_task_tree(v, task.id, indent=4)



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
