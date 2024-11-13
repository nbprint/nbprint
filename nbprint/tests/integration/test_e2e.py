import os.path

import pytest

from nbprint import Configuration
from nbprint.cli import run_hydra


def _example_folder_does_not_exist():
    return not os.path.exists("examples")


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
def test_basic_e2e():
    config = Configuration.load("examples/basic.yaml", "basic")
    config.run()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
def test_inline_e2e():
    config = Configuration.load("examples/inline.yaml", "inline")
    config.run()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
def test_landscape_e2e():
    config = Configuration.load("examples/landscape.yaml", "landscape")
    config.run()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
def test_finance_e2e():
    config = Configuration.load("examples/finance.yaml", "finance")
    config.run()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
def test_research_e2e():
    config = Configuration.load("examples/research.yaml", "research")
    config.run()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("parameters", ("string1", "string2"))
def test_hydra_e2e(parameters):
    run_hydra("examples/hydra.yaml", ["config=inline", "page=report", f"parameters={parameters}"])
