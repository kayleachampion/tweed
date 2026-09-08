from tweed.services.create import create_item
from tweed.services.link import link


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
    """Create a course and one offering."""

    course = vault.get_or_create("course", course_name)

    offering_name = f"{course_name} ({quarter} {section})"
    offering = create_item(vault, "offering", offering_name)

    offering["course"] = course["id"]
    offering["quarter"] = quarter
    offering["section"] = section
    offering["meeting_days"] = meeting_days or []
    offering["start_time"] = start_time
    offering["end_time"] = end_time
    offering["location"] = location

    offering.save()

    link(course, offering)

    return course, offering
