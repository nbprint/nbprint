from copy import deepcopy

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
