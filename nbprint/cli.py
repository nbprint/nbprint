import os
import os.path
from pathlib import Path
from typing import Optional

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from typer import Argument, Typer

from .config import Configuration


def run(path: Path, name: str) -> None:
    config = Configuration.load(path, name)
    config.run()


def run_hydra(config_dir="", overrides: Optional[list[str]] = Argument(None)) -> None:  # noqa: B008
    with initialize_config_dir(config_dir=os.path.join(os.path.dirname(__file__), "config", "hydra"), version_base=None):
        if config_dir:
            cfg = compose(config_name="conf", overrides=[], return_hydra_config=True)
            searchpaths = cfg["hydra"]["searchpath"]
            searchpaths.append(config_dir)
            overrides = [*overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]
        cfg = compose(config_name="conf", overrides=overrides)
        config = instantiate(cfg)
        if not isinstance(config, Configuration):
            config = Configuration(**config)
        config.run()


def main() -> None:
    app = Typer()
    app.command("run")(run)
    app.command("hydra")(run_hydra)
    app()
