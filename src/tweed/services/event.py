from tweed.services.create import create_item
from tweed.services.link import link


def create_event(
    vault,
    owner,
    date,
    start_time,
    end_time=None,
    event_type="meeting",
    location=None,
):
    """Create an event attached to an item."""

    event_name = f"{owner.title} {date} {start_time}"

    event = create_item(vault, "event", event_name)

    event["owner"] = owner["id"]
    event["date"] = date
    event["start_time"] = start_time
    event["end_time"] = end_time
    event["event_type"] = event_type
    event["location"] = location
    event.save()

    link(owner, event)

    return event
