from tweed.services.create import create_item
from tweed.services.link import link


def instantiate_task_tree(
    vault,
    owner,
    module,
    task_definitions,
    parent=None,
):
    """Recursively instantiate task definitions for an owner."""

    task_ids = []

    for task_definition in task_definitions:

        title = task_definition["title"]

        unique_name = (
            f"{owner.id}__"
            f"{module.id}__"
            f"{title}"
        )

        task = create_item(
            vault,
            "task",
            title,
            parent=parent,
            storage_name=unique_name,
            item_id=unique_name,
        )

        task["owner"] = owner.id
        task["module"] = module.id

        if "description" in task_definition:
            task["description"] = task_definition["description"]

        task.save()

        children = task_definition.get("tasks", [])

        instantiate_task_tree(
            vault,
            owner,
            module,
            children,
            parent=task.id,
        )

        task_ids.append(task.id)

    return task_ids

def attach_module(vault, owner, module):
    """Attach a module definition and instantiate its tasks."""

    modules = owner.get("modules", [])

    if any(
        module_instance["id"] == module["id"]
        for module_instance in modules
    ):
        return False

    root_task_ids = instantiate_task_tree(
        vault,
        owner,
        module,
        module.get("tasks", []),
    )

    module_instance = {
        "id": module["id"],
        "tasks": root_task_ids,
    }

    modules.append(module_instance)

    owner["modules"] = modules
    owner.save()

    link(owner, module)

    return True
