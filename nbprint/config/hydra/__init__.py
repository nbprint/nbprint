from ast import literal_eval
from logging import getLogger
from pathlib import Path
from typing import List, Optional

from ccflow import ModelRegistry
from hydra import compose, initialize_config_dir
from nbformat import read as nb_read
from omegaconf import DictConfig, OmegaConf

__all__ = ("load_config",)

_logger = getLogger(__name__)


def load_config(
    path: str,
    overrides: Optional[List[str]] = None,
) -> dict:
    # convert to Path
    path = Path(path)

    if not isinstance(overrides, list):
        # maybe running via python, reset
        overrides = []

    # prune any empty strings
    overrides = [o for o in overrides if o]

    # TODO: right now, nbprint runs off a specific config file, whereas
    # hydra takes a config dir and config name. For now we use the nbprint
    # style, so we adjust accordingly
    if path.suffix in (".yaml",):
        config_dir = str(path.parent.absolute().resolve())
        config_name = str(path.name)
    else:
        # Use base
        config_dir = str((Path(__file__).parent).absolute().resolve())
        config_name = "base.yaml"

    with initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = compose(config_name=config_name, overrides=[], return_hydra_config=True)
        searchpaths = cfg["hydra"]["searchpath"]
        searchpaths.extend([config_dir])
        overrides = [*overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]
        cfg = compose(config_name=config_name, overrides=overrides)

        if isinstance(cfg, DictConfig):
            cfg = OmegaConf.to_container(cfg, resolve=True)

        if "nbprint" not in cfg:
            _logger.warning("No 'nbprint' config found in the provided configuration. Assuming entire config is for nbprint.")
            cfg = {"nbprint": cfg}
            if "_target_" not in cfg["nbprint"]:
                cfg["nbprint"]["_target_"] = "nbprint.Configuration"

        # bridge hydra and non-hydra
        if "name" not in cfg["nbprint"]:
            cfg["nbprint"]["name"] = path.name.replace(".yaml", "").replace(".ipynb", "")

        # If its a notebook, parse it out and run directly
        # Read notebook contents and shove into config
        if path.suffix in (".ipynb",):
            cfg["nbprint"]["notebook"] = path

        registry = ModelRegistry.root()
        registry.load_config(cfg=cfg, overwrite=True)

    return registry
