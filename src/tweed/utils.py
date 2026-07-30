# src/tweed/utils.py

import re


def slugify(name: str) -> str:
    """
    Convert a human-readable name into a safe filename.
    """

    name = name.strip()

    # directory separators
    name = name.replace("/", "-")
    name = name.replace("\\", "-")

    # spaces become underscores
    name = re.sub(r"\s+", "_", name)

    # remove characters illegal or troublesome in filenames
    name = re.sub(r'[<>:"|?*]', "", name)

    # collapse repeated separators
    name = re.sub(r"_+", "_", name)
    name = re.sub(r"-+", "-", name)

    # avoid trailing punctuation
    return name.strip("._-")
