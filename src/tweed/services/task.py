from tweed.constants import TASK_STATUSES, TASK_PRIORITIES
from datetime import date


def set_due(task, due):
    """Set or clear a task due date."""

    if due is not None:
        try:
            date.fromisoformat(due)
        except ValueError:
            raise ValueError("Due date must be YYYY-MM-DD.")

    task["due"] = due
    task.save()

    return due


def set_status(task, status):
    canonical = TASK_STATUSES.get(status.lower())

    if canonical is None:
        raise ValueError(
            "Invalid status. Choose from: "
            + ", ".join(TASK_STATUSES.keys())
        )

    task["status"] = canonical
    task.save()

    return canonical



def set_priority(task, priority):
    """Set a task's priority."""

    canonical = TASK_PRIORITIES.get(priority.lower())

    if canonical is None:
        raise ValueError(
            "Invalid priority. Choose from: "
            + ", ".join(TASK_PRIORITIES.keys())
        )

    task["priority"] = canonical
    task.save()

    return canonical

def set_owner(task, owner: str | None):
    """Set or clear a task owner."""

    if owner is None:
        task["owner"] = ""
    else:
        task["owner"] = owner

    task.save()

    return task["owner"]
