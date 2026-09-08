from datetime import date

from tweed.registry import REGISTRY
from tweed.templates import render
from tweed.utils import slugify

def create_item(
    vault,
    kind: str,
    name: str,
    parent=None,
    storage_name=None,
    item_id=None,
):

    """Create and save a new item."""

    storage_name = storage_name or name

    if vault.exists(kind, storage_name):
        raise ValueError(f"'{name}' already exists.")

    item = REGISTRY[kind]

    note = vault.item(kind, storage_name)

    slug = slugify(item_id or name)

    note["id"] = f"{kind}:{slug}"
    note["title"] = name
    note["type"] = kind
    note["status"] = item.get("status", "active")
    note["priority"] = item.get("priority", "normal")
    note["created"] = date.today().isoformat()
    note["updated"] = date.today().isoformat()

    note["areas"] = item.get("areas", [])
    note["roles"] = item.get("roles", [])
    note["modules"] = []
    note["tags"] = []
    note["links"] = []

    if kind == "module":
        note["tasks"] = []

    if kind == "task":
        note["parent"] = parent

    note.content = render(kind, name)

    note.save()

    return note
