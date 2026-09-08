from tweed.config import Config
from tweed.note import Note
from tweed.vault import Vault
from tweed.constants import TASK_STATUSES, TASK_PRIORITIES, PROJECT_STATUSES


def complete_task_priorities(ctx, param, incomplete):
    """Complete task priority values."""

    incomplete_lower = incomplete.lower()

    return [
        priority
        for priority in TASK_PRIORITIES
        if priority.startswith(incomplete_lower)
    ]


def complete_task_statuses(ctx, param, incomplete: str):
    """Complete task status values."""

    incomplete_lower = incomplete.lower()

    return [
        status
        for status in TASK_STATUSES
        if status.lower().startswith(incomplete_lower)
    ]


def complete_items(kind=None):
    """Return a shell-completion function for vault items."""

    def complete(ctx, param, incomplete: str):
        config = Config()

        if not config.vault:
            return []

        vault = Vault(config.vault)
        paths = vault.items(kind) if kind else vault.items()

        incomplete_lower = incomplete.lower()
        results = []

        for path in paths:
            note = Note(path).load()
            title = note.get("title", path.stem)

            if incomplete_lower in title.lower():
                results.append(title.replace(" ", "\\ "))

        return results

    return complete


def complete_project_statuses(ctx, param, incomplete: str):
    """Complete project status values."""

    incomplete_lower = incomplete.lower()

    return [
        status
        for status in PROJECT_STATUSES
        if status.lower().startswith(incomplete_lower)
    ]

complete_tasks = complete_items("task")
complete_modules = complete_items("module")
complete_courses = complete_items("course")
complete_offerings = complete_items("offering")
complete_events = complete_items("event")
complete_projects = complete_items("project")
complete_students = complete_items("student")
