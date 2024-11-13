from pathlib import Path

from nbprint.cli import run_hydra


def test_config_rerunsafe():
    config = run_hydra(str(Path(__file__).parent / "files" / "hermetic.yaml"), dry_run=True)
    config1 = config.generate()
    config._reset()
    config2 = config.generate()
    code1 = ""
    code2 = ""
    for cell in config1.cells:
        code1 += cell["source"] + "\n"
    for cell in config2.cells:
        code2 += cell["source"] + "\n"
    assert code1 == code2
