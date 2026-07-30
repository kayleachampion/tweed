from textwrap import dedent

def render(name: str) -> str:
    return dedent(f"""\ 

    ---
    type: meeting
    title: {name}
    date: 

    participants: []

    links: []

    tags:
        - meeting
    ---

    # {{ name }}

    ## Agenda

    ## Action Items

    ## Tasks

    ## Key Links

    ## Notes
    """
    )
