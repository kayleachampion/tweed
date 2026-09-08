import typer

from tweed.config import Config
from tweed.services.create import create_item
from tweed.services.link import link
from tweed.vault import Vault
from tweed.services.task import set_status, set_due, set_priority, set_owner
from datetime import date

from tweed.constants import TASK_STATUSES, TASK_PRIORITIES, ACTIONABLE_TASK_STATUSES

from tweed.cli_completion import (
    complete_tasks,
    complete_modules,
    complete_task_statuses,
    complete_task_priorities,
)

app = typer.Typer(help="Manage tasks.")



##display names here
STATUS_LABELS = {
    "waiting_for_resources": "waiting for resources",
    "in_progress": "in progress",
    "submitted": "submitted",
    "done": "done",
}


def find_task_definition(tasks, title):
    """Find a task definition recursively by title."""

    for task in tasks:
        if task["title"] == title:
            return task

        found = find_task_definition(
            task.get("tasks", []),
            title,
        )

        if found is not None:
            return found

    return None

@app.command("add")
def add(
    module_name: str = typer.Argument(
        ...,
        shell_complete=complete_modules,
    ),
    task_name: str = typer.Argument(...),
    description: str = typer.Option("", "--description", "-d"),
    parent: str | None = typer.Option(
        None,
        "--parent",
        shell_complete=complete_tasks,
    ),
    vault: str | None = typer.Option(None),
):


    """Add a task definition to a module."""

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

    if module["type"] != "module":
        typer.echo(f"'{module_name}' is not a module.")
        raise typer.Exit(1)

    parent_definition = None

    if parent is not None:
        parent_definition = find_task_definition(
            module.get("tasks", []),
            parent,
        )

        if parent_definition is None:
            typer.echo(
                f"No task definition named '{parent}' "
                f"in module '{module.title}'."
            )
            raise typer.Exit(1)

    tasks = module.get("tasks", [])

    new_task = {
        "title": task_name,
    }

    if description:
        new_task["description"] = description

    if parent_definition is None:
        if any(
            task_def["title"] == task_name
            for task_def in tasks
        ):
            typer.echo(
                f"'{task_name}' already exists in '{module.title}'."
            )
            raise typer.Exit(1)

        tasks.append(new_task)

        message = (
            f"Added task definition '{task_name}' "
            f"to '{module.title}'."
        )

    else:
        children = parent_definition.setdefault("tasks", [])

        if any(
            task_def["title"] == task_name
            for task_def in children
        ):
            typer.echo(
                f"'{task_name}' already exists under "
                f"'{parent_definition['title']}'."
            )
            raise typer.Exit(1)

        children.append(new_task)

        message = (
            f"Added task definition '{task_name}' "
            f"under '{parent_definition['title']}'."
        )

    module["tasks"] = tasks
    module.save()

    typer.echo(message)




def due_sort_key(task):
    due = task.get("due")

    if not due:
        return (1, "")

    return (0, due)



@app.command("list")
def list_tasks(
    module_name: str | None = typer.Option(
        None,
        "--module",
        shell_complete=complete_modules,
    ),
    owner_name: str | None = typer.Option(
        None,
        "--owner",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        shell_complete=complete_task_statuses,
    ),
    active: bool = typer.Option(False, "--active"),
    done: bool = typer.Option(False, "--done"),
    vault: str | None = typer.Option(None),
):
    """List instantiated tasks."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    module = None
    owner = None

    if module_name:
        try:
            module = v.resolve(module_name)
        except ValueError as e:
            typer.echo(str(e))
            raise typer.Exit(1)

        if module["type"] != "module":
            typer.echo(f"'{module_name}' is not a module.")
            raise typer.Exit(1)

    if owner_name:
        try:
            owner = v.resolve(owner_name)
        except ValueError as e:
            typer.echo(str(e))
            raise typer.Exit(1)

    tasks = [
        note
        for note in v.find()
        if note.get("type") == "task"
    ]

    if module is not None:
        tasks = [
            task
            for task in tasks
            if task.get("module") == module.id
        ]

    if owner is not None:
        tasks = [
            task
            for task in tasks
            if task.get("owner") == owner.id
        ]

    if active and done:
        typer.echo("Use either --active or --done, not both.")
        raise typer.Exit(1)

    if active:
        tasks = [
            task
            for task in tasks
            if task.get("status") != "done"
        ]

    if done:
        tasks = [
            task
            for task in tasks
            if task.get("status") == "done"
        ]

    if status is not None:
        canonical_status = TASK_STATUSES.get(status.lower())

        if canonical_status is None:
            typer.echo(
                "Invalid status. Choose from: "
                + ", ".join(TASK_STATUSES.keys())
            )
            raise typer.Exit(1)

        tasks = [
            task
            for task in tasks
            if task.get("status") == canonical_status
        ]

    # Only display roots here. list_task_tree() handles descendants.
    task_ids = {task.id for task in tasks}

    root_tasks = [
        task
        for task in tasks
        if task.get("parent") not in task_ids
    ]

    root_tasks.sort(key=due_sort_key)

    for task in root_tasks:
        list_task_tree(v, task)



@app.command("next")
def next_task(
    module_name: str | None = typer.Option(
        None,
        "--module",
        shell_complete=complete_modules,
    ),
    owner_name: str | None = typer.Option(
        None,
        "--owner",
    ),
    vault: str | None = typer.Option(None),
):
    """Show the next actionable task."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    module = None
    owner = None

    if module_name:
        try:
            module = v.resolve(module_name)
        except ValueError as e:
            typer.echo(str(e))
            raise typer.Exit(1)

        if module.get("type") != "module":
            typer.echo(f"'{module_name}' is not a module.")
            raise typer.Exit(1)

    if owner_name:
        try:
            owner = v.resolve(owner_name)
        except ValueError as e:
            typer.echo(str(e))
            raise typer.Exit(1)

    tasks = [
        note
        for note in v.find()
        if note.get("type") == "task"
    ]

    if module is not None:
        tasks = [
            task
            for task in tasks
            if task.get("module") == module.id
        ]

    if owner is not None:
        tasks = [
            task
            for task in tasks
            if task.get("owner") == owner.id
        ]

    # Only actionable tasks
    tasks = [
        task
        for task in tasks
        if task.get("status") in ACTIONABLE_TASK_STATUSES
    ]

    if not tasks:
        typer.echo("No actionable tasks.")
        return

    tasks.sort(key=due_sort_key)

    task = tasks[0]

    due = task.get("due", "")

    if due:
        try:
            due_date = date.fromisoformat(due)

            if due_date < date.today():
                due = f"{due} OVERDUE"

        except ValueError:
            pass

    typer.echo(
        f"{task.title}\t"
        f"{task.get('status', '')}\t"
        f"{due}"
    )



@app.command("status")
def update_status(
    task_name: str = typer.Argument(
        ...,
        shell_complete=complete_tasks,
    ),
    status: str = typer.Argument(
        ...,
        shell_complete=complete_task_statuses,
    ),
    vault: str | None = typer.Option(None),
):
    """Set a task's status."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        task = v.resolve(task_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if task["type"] != "task":
        typer.echo(f"'{task_name}' is not a task.")
        raise typer.Exit(1)

    status = TASK_STATUSES.get(status.lower())

    if status is None:
        typer.echo(
            "Invalid status. Choose from: "
            + ", ".join(TASK_STATUSES.keys())
        )
        raise typer.Exit(1)

    try:
        status = set_status(task, status)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    typer.echo(f"{task.title}: {status}")

@app.command("start")
def start(
    task_name: str,
    vault: str | None = typer.Option(None),
):
    """Mark a task as in progress."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    update_status(task_name, "in_progress", vault)


@app.command("done")
def done(
    task_name: str,
    vault: str | None = typer.Option(None),
):
    """Mark a task as done."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    update_status(task_name, "done", vault)


@app.command("show")
def show(
    task_name: str = typer.Argument(
        ...,
        shell_complete=complete_tasks,
    ),
    vault: str | None = typer.Option(None),
):
    """Show a task."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        task = v.resolve(task_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if task["type"] != "task":
        typer.echo(f"'{task_name}' is not a task.")
        raise typer.Exit(1)

    typer.echo(f"Title:  {task.title}")
    typer.echo(f"Status: {task.get('status', '')}")
    typer.echo(f"Due:    {task.get('due', '')}")
    typer.echo(f"Owner:  {task.get('owner', '')}")

    module_id = task.get("module")
    if module_id:
        try:
            module_note = v.load_by_id(module_id)
            typer.echo(f"Module: {module_note.title}")
        except (ValueError, FileNotFoundError):
            typer.echo(f"Module: {module_id}")

    parent = task.get("parent")
    if parent:
        try:
            parent_note = v.load_by_id(parent)
            typer.echo(f"Parent: {parent_note.title}")
        except (ValueError, FileNotFoundError):
            typer.echo(f"Parent: {parent}")

    children = [
        note
        for note in v.find()
        if (
            note.get("type") == "task"
            and note.get("parent") == task["id"]
        )
    ]

    if children:
        typer.echo()
        typer.echo("Subtasks:")

        for child in children:
            show_task_tree(v, child["id"], indent=2)



@app.command("due")
def set_task_due(
    task_name: str = typer.Argument(
        ...,
        shell_complete=complete_tasks,
    ),
    due: str | None = typer.Option(None, "--date"),
    clear: bool = typer.Option(False, "--clear"),
    vault: str | None = typer.Option(None),
):
    """Set or clear a task's due date."""

    if due is not None and clear:
        typer.echo("Use either --date or --clear, not both.")
        raise typer.Exit(1)

    if due is None and not clear:
        typer.echo("Provide --date YYYY-MM-DD or --clear.")
        raise typer.Exit(1)

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        task = v.resolve(task_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if task["type"] != "task":
        typer.echo(f"'{task_name}' is not a task.")
        raise typer.Exit(1)

    try:
        set_due(task, None if clear else due)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if clear:
        typer.echo(f"{task.title}: due date cleared")
    else:
        typer.echo(f"{task.title}: due {due}")


def get_task_tree(vault, task_id):
    """Return a task and all of its descendants."""

    try:
        task = vault.load_by_id(task_id)
    except FileNotFoundError:
        return []

    tasks = [task]

    for note in vault.find():
        if (
            note.get("type") == "task"
            and note.get("parent") == task_id
        ):
            tasks.extend(get_task_tree(vault, note["id"]))

    return tasks


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


def list_task_tree(vault, task, indent=0):
    """Display a task and its subtasks recursively."""

    due = task.get("due", "")
    status = task.get("status", "")

    typer.echo(
        f"{' ' * indent}{task.title}\t{status}\t{due}"
    )

    for note in vault.find():
        if (
            note.get("type") == "task"
            and note.get("parent") == task["id"]
        ):
            list_task_tree(vault, note, indent + 2)


@app.command("priority")
def update_priority(
    task_name: str = typer.Argument(
        ...,
        shell_complete=complete_tasks,
    ),
    priority: str = typer.Argument(
        ...,
        shell_complete=complete_task_priorities,
    ),
    vault: str | None = typer.Option(None),
):
    """Set a task's priority."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        task = v.resolve(task_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if task["type"] != "task":
        typer.echo(f"'{task_name}' is not a task.")
        raise typer.Exit(1)

    try:
        priority = set_priority(task, priority)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    typer.echo(f"{task.title}: {priority}")


@app.command("owner")
def set_task_owner(
    task_name: str = typer.Argument(
        ...,
        shell_complete=complete_tasks,
    ),
    owner: str = typer.Argument(...),
    vault: str | None = typer.Option(None),
):
    """Set a task's owner."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    v = Vault(vault)

    try:
        task = v.resolve(task_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    if task["type"] != "task":
        typer.echo(f"'{task_name}' is not a task.")
        raise typer.Exit(1)

    set_owner(task, owner)

    typer.echo(f"{task.title}: {owner}")


@app.command("add-batch")
def add_batch(
    module_name: str = typer.Argument(
        ...,
        shell_complete=complete_modules,
    ),
    parent: str | None = typer.Option(
        None,
        "--parent",
        shell_complete=complete_tasks,
    ),
    vault: str | None = typer.Option(None),
):
    """Create multiple tasks in a module, one task per line."""

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

    parent_id = None

    if parent is not None:
        try:
            parent_task = v.resolve(parent)
        except ValueError as e:
            typer.echo(str(e))
            raise typer.Exit(1)

        if parent_task.get("type") != "task":
            typer.echo(f"'{parent}' is not a task.")
            raise typer.Exit(1)

        parent_id = parent_task["id"]

    typer.echo("Enter task names, one per line. Press Ctrl-D when finished:")

    import sys

    created = []

    for line in sys.stdin:
        task_name = line.strip()

        if not task_name:
            continue

        try:
            task = create_item(
                v,
                "task",
                task_name,
                parent=parent_id,
            )
        except ValueError as e:
            typer.echo(str(e))
            continue

        if parent_id is None:
            task["module"] = module["id"]
            task.save()

            link(module, task)
        else:
            task.save()

        created.append(task)

    typer.echo(
        f"Created {len(created)} task(s) in '{module.title}'."
    )

