from tweed.services.attach import attach_module
from tweed.services.create import create_item
from tweed.vault import Vault


def test_attach_module_is_idempotent(tmp_path):
    vault = Vault(tmp_path)

    owner = create_item(vault, "project", "zUnderproduction")
    module = create_item(vault, "module", "zInterview Study")

    attach_module(owner, module)
    attach_module(owner, module)

    owner = vault.resolve("zUnderproduction")
    module = vault.resolve("zInterview Study")

    assert owner["modules"] == [module["id"]]
    assert owner["links"] == [module["id"]]
    assert module["links"] == [owner["id"]]
