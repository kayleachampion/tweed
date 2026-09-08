import typer
from tweed.commands import new, init, module, offering, event, task, project
from tweed.commands.link import link
from tweed.commands.ls import list_items
from tweed.commands.show import show


app = typer.Typer(help="Markdown-native academic life and lab management")

app.add_typer(new.app, name="new")
app.command(name="link")(link)
app.command(name="list")(list_items)
app.command(name="ls")(list_items)
app.command(name="show")(show)
app.add_typer(init.app, name="init")
app.add_typer(module.app, name="module")
app.add_typer(offering.app, name="offering")
app.add_typer(event.app, name="event")
app.add_typer(task.app, name="task")
app.add_typer(project.app, name="project")


if __name__ == "__main__":
    app()
