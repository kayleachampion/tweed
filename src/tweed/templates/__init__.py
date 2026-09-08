from tweed.registry import REGISTRY

from . import student, project, committee, course, grant, paper, event, module, offering, task

TEMPLATES = {
    "student": student.render,
    "project": project.render,
    "committee": committee.render,
    "course": course.render,
    "grant": grant.render,
    "paper": paper.render,
    "module": module.render,
    "event": event.render,
    "task": task.render,
    "offering": offering.render,
}


def render(kind: str, name: str) -> str:
    """Render the appropriate markdown template."""

    try:
        template = REGISTRY[kind]["template"]
    except KeyError:
        raise ValueError(f"Unknown item type '{kind}'")

    try:
        renderer = TEMPLATES[template]
    except KeyError:
        raise ValueError(f"No renderer registered for template '{template}'")

    return renderer(name)
