from hydra.core.plugins import Plugins


class TestSearchpathPlugin:
    def test_discover_self(self):
        p = Plugins()
        all_ps = [_.__name__ for _ in p.discover()]
        assert "NBPrintSearchPathPlugin" in all_ps
