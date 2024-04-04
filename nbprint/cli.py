from pathlib import Path
from typer import Typer

from .config import Configuration


def cli(path: Path, name: str):
    config = Configuration.load(path, name)
    config.run()


def cli_hydra(path: Path, name: str):
    path = path.resolve()
    config = Configuration.load_hydra(str(path.parent), str(path.name), name)
    config.run()


def main():
    app = Typer()
    app.command("run")(cli)
    # TODO more
    app()


def main_hydra():
    app = Typer()
    app.command("run")(cli_hydra)
    # TODO more
    app()
