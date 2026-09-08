def add_link(note, target_id):
    links = note.get("links", [])

    if target_id not in links:
        links.append(target_id)
        note["links"] = sorted(links)


def link(a, b):
    """Create a bidirectional link between two items."""

    add_link(a, b["id"])
    add_link(b, a["id"])

    a.save()
    b.save()
