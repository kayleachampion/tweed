
import typer

from tweed.config import Config
from tweed.vault import Vault
from tweed.services.create import create


app = typer.Typer(help="Initialize higher-level structures.")

def init_course(
    vault,
    course_name: str,
    quarter: str,
    section: str,
    meeting_days: list[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    location: str | None = None,
):

    # Create (or retrieve) the canonical course.
    course = vault.get_or_create("course", course_name)

    # Create this offering.
    offering = create_item(
        vault,
        "offering",
        f"{course_name} ({quarter} {section})",
    )

    vault.link(course, offering)

    offering["course"] = course["id"]
    offering["quarter"] = quarter
    offering["section"] = section

    offering["meeting_days"] = meeting_days or []
    offering["start_time"] = start_time
    offering["end_time"] = end_time
    offering["location"] = location

    offering.save()

    return offering
