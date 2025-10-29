from pathlib import Path
from pprint import pprint
from typing import Optional

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from nbformat import read as nb_read
from omegaconf import DictConfig, OmegaConf
from typer import Argument, Option, Typer

from .config import Configuration

__all__ = ("main", "run")


def run(
    path: str,
    overrides: Optional[list[str]] = Argument(None),
    cfg: bool = False,
    debug: bool = False,
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

        if isinstance(hydra_config, DictConfig):
            hydra_config = OmegaConf.to_container(hydra_config, resolve=True)

        # bridge hydra and non-hydra
        extras = {"name": path.name.replace(".yaml", "").replace(".ipynb", "")} if "name" not in hydra_config else {}

        # swap in notebook content, if needed
        if path.suffix in (".ipynb",):
            with path.open("r", encoding="utf-8") as path_file:
                nb_content = nb_read(path_file, as_version=4)

            if "content" not in hydra_config:
                hydra_config["content"] = []

            # TODO: if first cell has tags, insert at front instead of appending
            for cell in nb_content.cells:
                hydra_config["content"].append(
                    {"_target_": "nbprint.ContentCode" if cell.cell_type == "code" else "nbprint.ContentMarkdown", "content": cell.source}
                )

        config = instantiate(hydra_config, **extras)
        if not isinstance(config, Configuration):
            config = Configuration.model_validate(config)

    if debug:
        config.debug = True

    # mimic hydra cfg
    pprint(OmegaConf.to_yaml(config.model_dump(mode="json"))) if cfg else config.run(dry_run=dry_run)
    return config


def run_cli(
    path: str,
    overrides: Optional[list[str]] = Argument(None),
    cfg: bool = Option(False, "--cfg", is_eager=True, help="Print the config"),
    debug: bool = Option(False, "--debug", help="Run in debug mode"),
    dry_run: bool = Option(False, "--dry-run", "-d", help="Run dry run"),
) -> None:
    run(path=path, overrides=overrides, cfg=cfg, debug=debug, dry_run=dry_run)


def main() -> None:
    app = Typer()
    app.command("run")(run)
    app()
