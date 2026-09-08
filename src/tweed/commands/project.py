import typer

from tweed.config import Config
from tweed.services.create import create_item
from tweed.services.link import link
from tweed.vault import Vault
from tweed.cli_completion import complete_projects, complete_modules, complete_project_statuses
from tweed.constants import PROJECT_STATUSES

app = typer.Typer()


@app.command("add")
def add(
    project_name: str = typer.Argument(...),
    vault: str | None = typer.Option(None),
):
    """Create a project."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        project = create_item(v, "project", project_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    typer.echo(f"Created project '{project.title}'.")
    


@app.command("list")
def list_projects(
    status: str | None = typer.Option(
        None,
        "--status",
        shell_complete=complete_project_statuses,
    ),
    vault: str | None = typer.Option(None),
):
    """List projects."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    projects = [
        note
        for note in v.find()
        if note.get("type") == "project"
    ]

    if status is not None:
        canonical_status = PROJECT_STATUSES.get(status.lower())

        if canonical_status is None:
            typer.echo(
                "Invalid status. Choose from: "
                + ", ".join(PROJECT_STATUSES.keys())
            )
            raise typer.Exit(1)

        projects = [
            project
            for project in projects
            if project.get("status") == canonical_status
        ]

    projects.sort(key=lambda project: project.title.lower())

    for project in projects:
        typer.echo(
            f"{project.title}\t"
            f"{project.get('status', '')}"
        )


@app.command("show")
def show(
    project_name: str = typer.Argument(
        ...,
        shell_complete=complete_projects,
    ),
    vault: str | None = typer.Option(None),
):
    """Show a project."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        project = v.resolve(project_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if project.get("type") != "project":
        typer.echo(f"'{project_name}' is not a project.")
        raise typer.Exit(1)

    typer.echo(f"Title:  {project.title}")
    typer.echo(f"Status: {project.get('status', '')}")

    module_ids = [
        link_id
        for link_id in (project.get("links") or [])
        if link_id.startswith("module:")
    ]

    modules = []

    for module_id in module_ids:
        try:
            modules.append(v.load_by_id(module_id))
        except FileNotFoundError:
            # Ignore stale links to deleted modules.
            continue

    if modules:
        typer.echo()
        typer.echo("Modules:")

        for module in sorted(modules, key=lambda m: m.title.lower()):
            typer.echo(f"  {module.title}")

    tasks = []

    for module in modules:
        task_ids = [
            link_id
            for link_id in (module.get("links") or [])
            if link_id.startswith("task:")
        ]

        for task_id in task_ids:
            try:
                tasks.append(v.load_by_id(task_id))
            except FileNotFoundError:
                continue

    if tasks:
        typer.echo()
        typer.echo("Tasks:")

        for task in tasks:
            typer.echo(
                f"  {task.title}\t"
                f"{task.get('status', '')}\t"
                f"{task.get('due', '')}"
            )


@app.command("add-module")
def add_module(
    project_name: str = typer.Argument(
        ...,
        shell_complete=complete_projects,
    ),
    module_name: str = typer.Argument(
        ...,
        shell_complete=complete_modules,
    ),
    vault: str | None = typer.Option(None),
):
    """Attach a module to a project."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        project = v.resolve(project_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if project.get("type") != "project":
        typer.echo(f"'{project_name}' is not a project.")
        raise typer.Exit(1)

    try:
        module = v.resolve(module_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if module.get("type") != "module":
        typer.echo(f"'{module_name}' is not a module.")
        raise typer.Exit(1)

    link(project, module)

    typer.echo(
        f"Added module '{module.title}' "
        f"to project '{project.title}'."
    )


@app.command("status")
def update_status(
    project_name: str = typer.Argument(
        ...,
        shell_complete=complete_projects,
    ),
    status: str = typer.Argument(
        ...,
        shell_complete=complete_project_statuses,
    ),
    vault: str | None = typer.Option(None),
):
    """Set a project's status."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        project = v.resolve(project_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if project.get("type") != "project":
        typer.echo(f"'{project_name}' is not a project.")
        raise typer.Exit(1)

    canonical_status = PROJECT_STATUSES.get(status.lower())

    if canonical_status is None:
        typer.echo(
            "Invalid status. Choose from: "
            + ", ".join(PROJECT_STATUSES.keys())
        )
        raise typer.Exit(1)

    project["status"] = canonical_status
    project.save()

    typer.echo(f"{project.title}: {canonical_status}")


