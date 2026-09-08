from textwrap import dedent

def render(name: str) -> str:
    return dedent(f"""\ 

    ---
    type: event
    start_time:
    end_time:
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
