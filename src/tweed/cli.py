import typer
from tweed.commands import new, init
from tweed.commands.link import link
from tweed.commands.ls import list_items
from tweed.commands.show import show
from tweed.commands.show import show


app = typer.Typer(help="Markdown-native academic life and lab management")

app.add_typer(new.app, name="new")
app.command(name="link")(link)
app.command(name="list")(list_items)
app.command(name="ls")(list_items)
app.command(name="show")(show)
app.add_typer(init.app, name="init")


if __name__ == "__main__":
    app()
