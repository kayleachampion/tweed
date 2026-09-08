import typer

from tweed.config import Config
from tweed.services.init import init_course
from tweed.utils import normalize_day
from tweed.vault import Vault

app = typer.Typer(help="Initialize higher-level structures.")


@app.command("course")
def course(
    course_name: str,
    quarter: str,
    section: str,
    days: str | None = typer.Option(
        None,
        "--days",
        help="Meeting days, comma-separated: M,W or Mon,Wed.",
    ),
    start_time: str | None = typer.Option(None, "--start-time"),
    end_time: str | None = typer.Option(None, "--end-time"),
    location: str | None = typer.Option(None, "--location"),
    vault: str | None = typer.Option(None, "--vault"),
):
    """Initialize a course offering."""

    config = Config()
    vault = vault or config.vault

    if vault is None:
        typer.echo("No vault configured.")
        raise typer.Exit(1)

    try:
        meeting_days = [normalize_day(day.strip()) for day in (days.split(",") if days else [])]
    except ValueError as e:
        raise typer.BadParameter(str(e), param_hint="--days")

    v = Vault(vault)

    try:
        course, offering = init_course(
            v,
            course_name,
            quarter,
            section,
            meeting_days=meeting_days,
            start_time=start_time,
            end_time=end_time,
            location=location,
        )
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    typer.echo(f"Course:   {course.title}")
    typer.echo(f"Offering: {offering.title}")
