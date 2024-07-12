from __future__ import annotations

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pathlib import Path
from typer import Argument, Typer

from .config import Configuration


def run(path: Path, name: str) -> None:
    """Helper function to run nbprint outside hydra config context."""
    config = Configuration.load(path, name)
    config.run()


def run_hydra(config_dir="", overrides: list[str] | None = Argument(None)) -> None:  # noqa: B008
    """Helper function to run nbprint inside hydra config context."""
    with initialize_config_dir(config_dir=str(Path(__file__).parent.resolve() / "config" / "hydra"), version_base=None):
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
    """Main CLI entrypoint for nbprint."""
    app = Typer()
    app.command("run")(run)
    app.command("hydra")(run_hydra)
    app()
