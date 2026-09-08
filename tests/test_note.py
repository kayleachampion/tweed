from tweed.vault import Vault
from tweed.services.create import create_item


def test_new_note(tmp_path):
    vault = Vault(tmp_path)

    note = vault.item("project", "Groovy_New_Project")

    note["type"] = "project"
    note["status"] = "planning"
    note.content = "# Groovy New Project"

    note.save()

    path = tmp_path / "Projects" / "Groovy_New_Project.md"

    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "type: project" in text
    assert "status: planning" in text
    assert "# Groovy New Project" in text


def test_note_round_trip(tmp_path):
    vault = Vault(tmp_path)

    note = vault.item("project", "Groovy_New_Project")
    note["type"] = "project"
    note["status"] = "planning"
    note.content = "# Groovy New Project"
    note.save()

    loaded = vault.item("project", "Groovy_New_Project").load()

    assert loaded["type"] == "project"
    assert loaded["status"] == "planning"
    assert loaded.content == "# Groovy New Project"
