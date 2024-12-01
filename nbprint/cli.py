from pathlib import Path
from typing import Optional

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
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

    with initialize_config_dir(config_dir=str(path.parent.absolute()), version_base=None):
        hydra_config = compose(config_name=str(path.name), overrides=overrides)

        # bridge hydra and non-hydra
        extras = {"name": path.name.replace(".yaml", "").replace(".yml", "")} if "name" not in hydra_config else {}
        config = instantiate(hydra_config, **extras)
        if not isinstance(config, Configuration):
            config = Configuration(**config)

    # mimic hydra cfg
    if cfg:
        print(OmegaConf.to_yaml(config.model_dump(mode="json")))  # noqa: T201
    else:
        # TODO: return file?
        config.run(dry_run=dry_run)
    return config


def main() -> None:
    app = Typer()
    app.command("run")(run)
    app.command("cfg")(cfg)
    app.command("hydra")(run_hydra)
    app()
