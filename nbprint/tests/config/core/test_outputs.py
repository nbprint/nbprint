from datetime import datetime
from pathlib import Path

from nbprint.cli import run_hydra


def test_outputs():
    config = run_hydra(str(Path(__file__).parent / "files" / "basic.yaml"), dry_run=True)
    assert config.outputs.naming == "{{name}}-{{date}}-{{datetime}}-{{uuid}}-{{sha}}"
    path = config.outputs.run(config=config, gen=config.generate())
    assert len(path.name) == 150
    today = datetime.now()
    assert path.name.startswith(f"basic-{today.year}-{today.month}-{today.day}")
    assert config.outputs._get_sha(config=config) in path.name
