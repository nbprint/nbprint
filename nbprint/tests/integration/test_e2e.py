import os.path
import sys
from unittest.mock import patch

import pytest

from nbprint import Configuration
from nbprint.cli import hydra, run


def _example_folder_does_not_exist():
    return not os.path.exists("examples")


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("template", ("basic", "inline", "landscape", "finance", "research", "plotly", "customsize", "nonpagedjs", "greattables"))
def test_e2e(template):
    config = Configuration.load(f"examples/{template}.yaml", template)
    config.run()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("parameters", ("string1", "string2"))
def test_hydra_e2e(parameters):
    run("examples/hydra.yaml", ["config=inline", "page=report", f"parameters={parameters}"])


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("template", ("basic", "inline", "landscape", "finance", "research", "plotly", "customsize", "nonpagedjs", "greattables"))
def test_pdf(template):
    run(f"examples/{template}.yaml", ["++outputs.target=webpdf"])


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples - notebook direct")
@pytest.mark.parametrize("template", ("basic", "parameters"))
def test_run_notebook_direct(template):
    if template == "parameters":
        run(f"examples/{template}.ipynb", ["+parameters.a=10", "+parameters.b='hello'", "+parameters.c=True"])
    else:
        run(f"examples/{template}.ipynb", [])


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples - notebook direct")
@pytest.mark.parametrize("parameters", ("string1", "string2"))
def test_run_notebook_ccflow(parameters):
    argv = [
        "nbprint",
        "--config-dir",
        "examples/ccflow",
        "nbprint=inline",
        f"+context={parameters}",
    ]
    with patch.object(sys, "argv", argv):
        hydra()


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples - notebook direct")
@pytest.mark.parametrize("parameters", ("string1", "string2"))
def test_run_notebook_ccflow_with_notebook(parameters):
    argv = [
        "nbprint",
        "--config-dir",
        "examples/ccflow",
        "+nbprint.notebook=examples/basic.ipynb",
        "+nbprint.name=basic",
        f"+context={parameters}",
    ]
    with patch.object(sys, "argv", argv):
        hydra()
