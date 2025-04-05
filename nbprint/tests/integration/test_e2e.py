import os.path

import pytest

from nbprint import Configuration
from nbprint.cli import run_hydra


def _example_folder_does_not_exist():
    return not os.path.exists("examples")


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("template", ("basic", "inline", "landscape", "finance", "research", "plotly", "customsize", "nonpagedjs"))
def test_e2e(template):
    config = Configuration.load(f"examples/{template}.yaml", template)
    config.run()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("parameters", ("string1", "string2"))
def test_hydra_e2e(parameters):
    run_hydra("examples/hydra.yaml", ["config=inline", "page=report", f"parameters={parameters}"])
