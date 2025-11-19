import sys
from itertools import product
from os import environ
from os.path import exists
from unittest.mock import patch

import pytest

from nbprint import Configuration
from nbprint.cli import hydra, run


def _example_folder_does_not_exist():
    return not exists("examples")


_integration_templates = (
    "basic",
    "inline",
    "landscape",
    "finance",
    "research",
    "plotly",
    "customsize",
    "nonpagedjs",
    "greattables",
)
_integration_notebooks = (
    "basic",
    "parameters",
)
_integration_formats = (
    "ipynb",
    "html",
    "webhtml",
    "webpdf",
)


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize(("template", "fmt"), list(product(_integration_templates, _integration_formats)))
def test_run_e2e(template, fmt):
    if fmt == "":
        config = Configuration.load(f"examples/{template}.yaml", template)
        config.run()
    elif fmt == "webpdf":
        if template == "customsize":
            return
        run(f"examples/{template}.yaml", ["++outputs.target=webpdf"])


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("parameters", ("string1", "string2"))
def test_hydra_e2e(parameters):
    run("examples/hydra.yaml", ["config=inline", "page=report", f"parameters={parameters}"])


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples not present - skipping examples tests")
@pytest.mark.parametrize("template", _integration_templates)
def test_email(template):
    pytest.skip("TODO", template)


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples - notebook direct")
@pytest.mark.parametrize(("notebook", "fmt"), list(product(_integration_notebooks, _integration_formats)))
def test_run_notebook_direct(notebook, fmt):
    if notebook == "parameters":
        run(
            f"examples/{notebook}.ipynb",
            [
                f"++nbprint.outputs.target={fmt}",
                "+nbprint.parameters.a=10",
                "+nbprint.parameters.b='hello'",
                "+nbprint.parameters.c=True",
            ],
        )
    else:
        run(f"examples/{notebook}.ipynb", [])


@pytest.mark.skipif(_example_folder_does_not_exist(), reason="Examples - notebook direct")
@pytest.mark.parametrize(("notebook", "fmt"), list(product(_integration_notebooks, _integration_formats)))
def test_email_notebook(notebook, fmt):
    if notebook == "basic":
        if not environ.get("SMTP_USER") or not environ.get("SMTP_PASSWORD"):
            pytest.skip("SMTP credentials not set in environment - skipping email test")
            return
        run(
            f"examples/{notebook}.ipynb",
            [
                "nbprint/outputs=nbprint/email",
                f"++nbprint.outputs.target={fmt}",
                f"+nbprint.outputs.to={environ['SMTP_USER']}",
                f"+nbprint.outputs.smtp.host={environ['SMTP_HOST']}",
                f"+nbprint.outputs.smtp.user={environ['SMTP_USER']}",
                f"+nbprint.outputs.smtp.password={environ['SMTP_PASSWORD']}",
                "nbprint/content/frontmatter=nbprint/title_toc",
            ],
        )
    else:
        # Skip for now
        ...


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


def test_multirun():
    with patch("nbconvert.nbconvertapp.main") as mock_nbconvert_main:
        ret = run(
            "examples/basic.ipynb",
            [
                "++callable=/nbprintx",
                r"""+nbprint.outputs.naming='{{name}}-{{date}}-{{a}}'""",
                r"""+nbprintx.parameters='[{"a":1},{"a":2},{"a":3}]'""",
                "++nbprint.outputs.execute=False",
            ],
        )
        assert len(ret.outputs) == 3

        # Ensure that nbconvert was only called exactly 3 times (once per output)
        assert mock_nbconvert_main.call_count == 3
