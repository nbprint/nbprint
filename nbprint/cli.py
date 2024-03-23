from pathlib import Path
from typer import run

from .config import Configuration


def cli(path: Path, name: str):
    config = Configuration.load(path, name)
    config.run()


def main():
    run(cli)
