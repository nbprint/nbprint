from pathlib import Path
from typer import Typer

from .config import Configuration


def cli(path: Path, name: str):
    config = Configuration.load(path, name)
    config.run()


def main():
    app = Typer()
    app.command("run")(cli)
    # TODO more
    app()
