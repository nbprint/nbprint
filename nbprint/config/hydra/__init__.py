from ast import literal_eval
from logging import getLogger
from pathlib import Path
from typing import Any, List, Optional

from ccflow import LazyRegistry
from lerna import compose, initialize_config_dir
from nbformat import read as nb_read
from omegaconf import DictConfig, OmegaConf, open_dict
from typing_extensions import Self

__all__ = ("load_config",)

_logger = getLogger(__name__)


class _SharedLazyRegistry(LazyRegistry):
    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> Self:
        if memo is not None:
            memo[id(self)] = self
        return self


def load_config(
    path: str,
    overrides: List[str] | None = None,
) -> LazyRegistry:
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
    if path.suffix == ".yaml":
        config_dir = str(path.parent.absolute().resolve())
        config_name = str(path.name)
        is_default = False
    else:
        # Use base
        config_dir = str((Path(__file__).parent).absolute().resolve())
        config_name = "base.yaml"
        is_default = True

    with initialize_config_dir(config_dir=config_dir, version_base=None):
        if not is_default:
            cfg = compose(config_name=config_name, overrides=[], return_hydra_config=True)
            searchpaths = cfg["hydra"]["searchpath"]
            searchpaths.extend([config_dir])
            overrides = [*overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]
        cfg = compose(config_name=config_name, overrides=overrides)

        if "nbprint" not in cfg:
            _logger.warning("No 'nbprint' config found in the provided configuration. Assuming entire config is for nbprint.")
            with open_dict(cfg):
                cfg.nbprint = cfg.copy()

        if "_target_" not in cfg.nbprint:
            with open_dict(cfg.nbprint):
                cfg.nbprint._target_ = "nbprint.Configuration"

        if "debug" not in cfg.nbprint:
            with open_dict(cfg.nbprint):
                cfg.nbprint.debug = False

        # bridge hydra and non-hydra
        if "name" not in cfg.nbprint:
            with open_dict(cfg.nbprint):
                cfg.nbprint.name = path.name.replace(".yaml", "").replace(".ipynb", "")

        # If its a notebook, parse it out and run directly
        # Read notebook contents and shove into config
        if path.suffix == ".ipynb":
            with open_dict(cfg):
                cfg.nbprint.notebook = path

        if isinstance(cfg, DictConfig):
            cfg = OmegaConf.to_container(cfg, resolve=True)

        registry = _SharedLazyRegistry()
        registry.load_config(cfg=cfg, overwrite=True)

        if "callable" in cfg:
            callable_path = cfg["callable"]
        elif "callable" in cfg.get("nbprint", {}):
            callable_path = cfg["nbprint"]["callable"]
        else:
            callable_path = "nbprint"
        registry.add("callable", registry[callable_path.removeprefix("/")], overwrite=True)

    return registry
