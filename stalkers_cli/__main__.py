import novel
import req
import scripts
import typer

app = typer.Typer(
    help="Collection of scripts that clean, extract, make requests and format a novel.",
    add_completion=False,
    no_args_is_help=True,
    
)
app.add_typer(scripts.app, name="scripts", help="Some useful scripts")
app.add_typer(novel.app, name="novel", help="Extract metadata and format chapters of a novel")
app.add_typer(req.app, name="req", help="Send requests to the Stalkers API")

if __name__ == "__main__":
    app()
