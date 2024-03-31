import os.path
import pytest

from nbprint import Configuration


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
def test_finance_e2e():
    config = Configuration.load("examples/finance.yaml", "finance")
    config.run()

@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
def test_research_e2e():
    config = Configuration.load("examples/research.yaml", "research")
    config.run()
