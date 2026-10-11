import subprocess
import sys
from copy import deepcopy

import pytest

from nbprint.config.hydra import load_config


class TestSearchpathPlugin:
    def test_discover_self(self):
        import hydra_plugins.lerna.searchpath

        assert "nbprint" in hydra_plugins.lerna.searchpath._searchpaths_pkg

    def test_load_config_defers_unselected_models(self):
        registry = load_config("examples/basic.ipynb")

        assert registry["callable"] is registry["nbprint"]
        assert not registry.is_loaded("nbprintx")

        registry["nbprintx"]

        assert registry.is_loaded("nbprintx")

    def test_loaded_models_remain_deepcopyable(self):
        registry = load_config("examples/basic.ipynb")

        copied = deepcopy(registry["callable"])

        assert copied == registry["callable"]

    def test_locating_config_package_is_lightweight(self):
        # lerna resolves pkg://nbprint.config.hydra on every hydra app startup
        code = (
            "import importlib.resources, sys; "
            "importlib.resources.files('nbprint.config.hydra'); "
            "heavy = [m for m in ('ccflow', 'nbformat', 'nbprint.cli', 'nbprint.config.core') if m in sys.modules]; "
            "assert not heavy, heavy"
        )
        subprocess.run([sys.executable, "-c", code], check=True)  # noqa: S603

    @pytest.mark.parametrize("module", ["nbprint.cli", "nbprint.config.overlay", "nbprint.config.hydra.loader"])
    def test_import_without_warnings_or_cycles(self, module):
        subprocess.run([sys.executable, "-W", "error::UserWarning", "-c", f"import {module}"], check=True)  # noqa: S603
