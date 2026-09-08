
from tweed.services.task import set_status


def test_set_task_status(tmp_path):
    from tweed.vault import Vault
    from tweed.services.create import create_item

    vault = Vault(tmp_path)

    task = create_item(vault, "task", "Analyze transcripts")

    set_status(task, "in progress")

    assert task["status"] == "in progress"

def test_set_task_status_rejects_invalid_status(tmp_path):
    import pytest
    from tweed.vault import Vault
    from tweed.services.create import create_item

    vault = Vault(tmp_path)

    task = create_item(vault, "task", "Analyze transcripts")

    with pytest.raises(ValueError):
        set_status(task, "active")
