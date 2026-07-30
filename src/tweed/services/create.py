from datetime import date

from tweed.registry import REGISTRY
from tweed.templates import render
from tweed.utils import slugify


def create_item(vault, kind: str, name: str):
    """Create and save a new item."""

    if vault.exists(kind, name):
        raise ValueError(f"'{name}' already exists.")

    item = REGISTRY[kind]

    note = vault.item(kind, name)

    slug = slugify(name)

    note["id"] = f"{kind}:{slug}"
    note["title"] = name
    note["type"] = kind
    note["status"] = "active"
    note["created"] = date.today().isoformat()
    note["updated"] = date.today().isoformat()

    note["areas"] = item.get("areas", [])
    note["roles"] = item.get("roles", [])
    note["modules"] = item.get("modules", [])
    note["tags"] = []
    note["links"] = []

    note.content = render(kind, name)

    note.save()

    return note
