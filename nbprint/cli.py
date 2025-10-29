from pathlib import Path
from pprint import pprint
from typing import Optional

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from nbformat import read as nb_read
from omegaconf import OmegaConf
from typer import Argument, Typer

from .config import Configuration

__all__ = ("cfg", "main", "run", "run_hydra")


def run(path: Path, name: str = "", dry_run: bool = False) -> Configuration:
    return run_hydra(path=path, overrides=name.split(" "), dry_run=dry_run)


def cfg(path: Path, name: str = "", dry_run: bool = False) -> Configuration:
    return run_hydra(path=path, overrides=name.split(" "), cfg=True, dry_run=dry_run)


def run_hydra(
    path: str,
    overrides: Optional[list[str]] = Argument(None),
    cfg: bool = False,
    dry_run: bool = False,
) -> Configuration:
    # convert to Path
    path = Path(path)

    if not isinstance(overrides, list):
        # maybe running via python, reset
        overrides = []

    # prune any empty strings
    overrides = [o for o in overrides if o]

    # If its a notebook, parse it out and run directly
    # Read notebook contents and shove into config
    config_name = "nbprint/config/default.yaml" if path.suffix in (".ipynb",) else str(path.name)

    with initialize_config_dir(config_dir=str(path.parent.absolute()), version_base=None):
        hydra_config = compose(config_name=config_name, overrides=overrides)

        # bridge hydra and non-hydra
        extras = {"name": path.name.replace(".yaml", "")} if "name" not in hydra_config else {}

        # swap in notebook content, if needed
        if path.suffix in (".ipynb",):
            with path.open("r", encoding="utf-8") as path_file:
                nb_content = nb_read(path_file, as_version=4)
            if "content" not in extras:
                extras["content"] = []
            for cell in nb_content.cells:
                extras["content"].append({"_target_": "nbprint.ContentCode" if cell.cell_type == "code" else "nbprint.ContentMarkdown", "source": cell.source})
        config = instantiate(hydra_config, **extras)
        if not isinstance(config, Configuration):
            config = Configuration.model_validate(config)

    # mimic hydra cfg
    pprint(OmegaConf.to_yaml(config.model_dump(mode="json"))) if cfg else config.run(dry_run=dry_run)
    return config


def main() -> None:
    app = Typer()
    app.command("run")(run)
    app.command("cfg")(cfg)
    app.command("hydra")(run_hydra)
    app()
