from textwrap import dedent


def render(name: str) -> str:
    return dedent(f"""\
    # {name}

    ## Purpose

    ## Notes
    """)
