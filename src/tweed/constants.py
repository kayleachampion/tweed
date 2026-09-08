
## canonicalization here
TASK_STATUSES = {
    "waiting for resources": "waiting_for_resources",
    "waiting_for_resources": "waiting_for_resources",
    "in progress": "in_progress",
    "in_progress": "in_progress",
    "submitted": "submitted",
    "done": "done",
}

CANONICAL_TASK_STATUSES = sorted(set(TASK_STATUSES.values()))

PROJECT_STATUSES = {
    "active": "active",
    "on hold": "on_hold",
    "on_hold": "on_hold",
    "completed": "completed",
    "archived": "archived",
}

ACTIONABLE_TASK_STATUSES = {
    "in_progress",
    "submitted",
}

TASK_PRIORITIES = {
    "low": "low",
    "normal": "normal",
    "high": "high",
    "urgent": "urgent",
}
