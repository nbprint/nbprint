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


def _direct_notebook_run(path: Path, hydra_config: dict) -> None:
    with path.open("r", encoding="utf-8") as path_file:
        nb_content = nb_read(path_file, as_version=4)

    if "content" not in hydra_config["nbprint"]:
        hydra_config["nbprint"]["content"] = []

    # TODO: if first cell has tags, insert at front instead of appending
    if nb_content.cells and "metadata" in nb_content.cells[0] and "parameters" in nb_content.cells[0]["metadata"].get("tags", []):
        # skip first cell
        cells_to_process = nb_content.cells[1:]

        # Pull out the parameters object and ensure everything is present
        if "parameters" not in hydra_config["nbprint"]:
            hydra_config["nbprint"]["parameters"] = {}

        # Parse first cell for parameters
        first_cell = nb_content.cells[0]
        param_lines = first_cell.source.splitlines()
        for line in param_lines:
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Attempt to eval the value to get correct type
                try:
                    evaluated_value = literal_eval(value)
                except SyntaxError:
                    evaluated_value = value
                if key not in hydra_config["nbprint"]["parameters"]:
                    hydra_config["nbprint"]["parameters"][key] = evaluated_value
    else:
        cells_to_process = nb_content.cells

    for cell in cells_to_process:
        hydra_config["nbprint"]["content"].append(
            {"_target_": "nbprint.ContentCode" if cell.cell_type == "code" else "nbprint.ContentMarkdown", "content": cell.source}
        )


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
            _direct_notebook_run(path, cfg)

        registry = ModelRegistry.root()
        registry.load_config(cfg=cfg, overwrite=True)

    return registry
