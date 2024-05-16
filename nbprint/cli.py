import os
import os.path
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pathlib import Path
from typer import Argument, Typer
from typing import List, Optional

from .config import Configuration


def run(path: Path, name: str):
    config = Configuration.load(path, name)
    config.run()


def run_hydra(config_dir="", overrides: Optional[List[str]] = Argument(None)):
    with initialize_config_dir(
        config_dir=os.path.join(os.path.dirname(__file__), "config", "hydra"), version_base=None
    ):
        if config_dir:
            cfg = compose(config_name="conf", overrides=[], return_hydra_config=True)
            searchpaths = cfg["hydra"]["searchpath"]
            searchpaths.append(config_dir)
            overrides = overrides.copy() + [f"hydra.searchpath=[{','.join(searchpaths)}]"]
        cfg = compose(config_name="conf", overrides=overrides)
        config = instantiate(cfg)
        if not isinstance(config, Configuration):
            config = Configuration(**config)
        config.run()


def main():
    app = Typer()
    app.command("run")(run)
    app.command("hydra")(run_hydra)
    app()
