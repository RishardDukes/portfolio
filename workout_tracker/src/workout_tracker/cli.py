import click
from . import create_app
from .db import db

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo("Database initialized.")
