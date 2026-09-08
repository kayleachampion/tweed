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


DAY_NAMES = {
    "m": "Monday",
    "mo": "Monday",
    "mon": "Monday",
    "monday": "Monday",

    "tu": "Tuesday",
    "tue": "Tuesday",
    "tuesday": "Tuesday",

    "w": "Wednesday",
    "we": "Wednesday",
    "wed": "Wednesday",
    "wednesday": "Wednesday",

    "th": "Thursday",
    "thu": "Thursday",
    "thursday": "Thursday",

    "f": "Friday",
    "fr": "Friday",
    "fri": "Friday",
    "friday": "Friday",

    "sa": "Saturday",
    "sat": "Saturday",
    "saturday": "Saturday",

    "su": "Sunday",
    "sun": "Sunday",
    "sunday": "Sunday",
}

DAY_ORDER = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


def normalize_day(day: str) -> str:
    key = day.strip().lower()

    try:
        return DAY_NAMES[key]
    except KeyError:
        raise ValueError(f"Unknown day '{day}'.")
