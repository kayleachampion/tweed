from __future__ import annotations
from pathlib import Path

from .note import Note
from .utils import slugify
from .registry import REGISTRY



class Vault:

    def __init__(self, root):
        self.root = Path(root)

    def exists(self, kind: str, name: str) -> bool:
        filename = slugify(name) + ".md"
        return (self.directory(kind) / filename).exists()

    def directory(self, kind: str) -> Path:
        """Return (and create) the directory for an item type."""

        try:
            relative = REGISTRY[kind]["directory"]
        except KeyError:
            raise ValueError(f"Unknown item type: {kind}")

        path = self.root / relative
        path.mkdir(parents=True, exist_ok=True)

        return path

    def item(self, kind: str, name: str) -> Note:
        """Create a Note object for an item."""

        filename = slugify(name) + ".md"
        return Note(self.directory(kind) / filename)

    def items(self, kind: str | None = None):
        """Return all items of the given type."""

        if kind is None:
            results = []
            for item_type in REGISTRY:
                results.extend(self.items(item_type))
            return sorted(results)

        return sorted(self.directory(kind).glob("*.md"))


    def load_by_id(self, item_id: str) -> Note:

        kind, slug = item_id.split(":", 1)

        return self.item(kind, slug).load()

    def find(self, terms=None):
        """Return all items matching the given search terms."""

        if terms is None:
            terms = []
        elif isinstance(terms, str):
            terms = [terms]

        terms = [t.lower() for t in terms]

        results = []

        for path in self.items():
            note = Note(path).load()

            fields = [
                note.title.lower(),
                note.kind.lower(),
                note.get("status", "").lower(),
                *[t.lower() for t in note.get("tags", [])],
                *[a.lower() for a in note.get("areas", [])],
                *[r.lower() for r in note.get("roles", [])],
            ]

            if all(any(term in field for field in fields) for term in terms):
                results.append(note)

        return results

  
    def resolve(self, query: str) -> Note:
        query = slugify(query)

        matches = []

        for note in self.find():

            if note.get("id") == query:
                return note

            if slugify(note.get("title", note.path.stem)) == query:
                matches.append(note)

        if not matches:
            raise ValueError(f"No item named '{query}'.")

        if len(matches) > 1:
            raise ValueError(f"Ambiguous item '{query}'.")

        return matches[0]


    def backlinks(self, note: Note) -> list[Note]:
        """Return all notes that link to this note."""

        results = []

        for path in self.items():
            other = Note(path).load()

            item_id = note.get("id")

            if item_id and item_id in other.get("links", []):
                results.append(other)


        return sorted(results, key=lambda n: n.title.lower())


    def links(self, note: Note) -> list[Note]:
        """Return Notes linked from this note."""

        results = []

        for item_id in note.get("links", []):
            results.append(self.load_by_id(item_id))

        return results


    def get_or_create(self, kind: str, name: str) -> Note:
        """Return an existing item of this kind, or create it."""

        for note in self.find():
            if (
                note.get("type") == kind
                and note.get("title", note.path.stem).lower() == name.lower()
            ):
                return note

        from tweed.services.create import create_item

        return create_item(self, kind, name)
