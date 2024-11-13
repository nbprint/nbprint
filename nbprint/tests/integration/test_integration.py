from pathlib import Path

import pytest

from nbprint.cli import run_hydra


@pytest.mark.parametrize("file", list((Path(__file__).parent / "files").glob("*")))
def test_integrations(file):
    run_hydra(str(file.resolve()))
