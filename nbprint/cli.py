from pathlib import Path
from pprint import pprint
from typing import Optional

from ccflow import ResultBase
from ccflow.utils.hydra import cfg_explain_cli, cfg_run
from hydra import main as hydra_main
from omegaconf import OmegaConf
from typer import Argument, Option, Typer

from .config import Configuration
from .config.hydra import load_config

__all__ = ("hydra", "main", "run")


def run(
    path: str,
    overrides: Optional[list[str]] = Argument(None),
    cfg: bool = False,
    debug: bool = False,
    dry_run: bool = False,
) -> Configuration:
    registry = load_config(path, overrides=overrides)
    config = registry["nbprint"]
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


@hydra_main(config_path=str(Path(__file__).parent / "config" / "hydra"), config_name="base", version_base=None)
def hydra(cfg) -> ResultBase:
    return cfg_run(cfg)


def hydra_explain() -> None:
    cfg_explain_cli(config_path=str(Path(__file__).parent / "config" / "hydra"), config_name="base", hydra_main=hydra)


def main() -> None:
    app = Typer()
    app.command("run")(run_cli)
    app()
