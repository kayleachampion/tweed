from textwrap import dedent

def render(name: str) -> str:
    return dedent(f"""\ 

        ---
        id:
        title: {name}
        type: offering

        course:
        quarter:
        section:

        status: 

        links: []

        students: []
        meetings: []
        assignments: []

        tags: []
        ---

        # {{ title }}

        ## Schedule

        ## Announcements

        ## Notes

        ## TODO

        ## Meetings

        ## Students

        ## Assignments

    """
    )
