class TestSearchpathPlugin:
    def test_discover_self(self):
        import hydra_plugins.lerna.searchpath

        assert "nbprint" in hydra_plugins.lerna.searchpath._searchpaths_pkg
