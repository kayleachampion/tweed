from tweed.services.attach import attach_module
from tweed.services.create import create_item
from tweed.vault import Vault


def test_attach_module_is_idempotent(tmp_path):
    vault = Vault(tmp_path)

    owner = create_item(vault, "project", "zUnderproduction")
    module = create_item(vault, "module", "zInterview Study")

    attach_module(vault, owner, module)
    attach_module(vault, owner, module)

    assert len(owner["modules"]) == 1
    assert owner["modules"][0]["id"] == module["id"]
