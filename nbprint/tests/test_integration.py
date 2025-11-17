from pathlib import Path

import pytest
from nbformat import reads

from nbprint.cli import run


@pytest.mark.parametrize("file", sorted((Path(__file__).parent / "files").glob("*")))
def test_integrations(file):
    res = run(str(file.resolve()))

    # file specific tests
    if file.name == "capture.yaml":
        output = res.outputs.notebook.read_text()
        nb = reads(output, as_version=4)
        assert nb.cells[-1].source == '%%capture\nprint("test1")\nimport logging\nlogging.critical("test!")\n'
        assert nb.cells[-1].outputs == []

    if file.name == "plugins.yaml":
        output = res.outputs.notebook.read_text()
        assert "Example Page Content from Plugin" in output


def test_content_injection():
    res = run("examples/basic.ipynb", ["nbprint/content/frontmatter=nbprint/title_toc"])
    output = res.outputs.notebook.read_text()
    nb = reads(output, as_version=4)
    # Title cell
    assert nb.cells[4].source.startswith("# basic")
    # TOC cell
    assert nb.cells[6].source.startswith("nbprint_contenttableofcontents = nbprint_config.content[2]")


def test_parameter_injection():
    res = run("examples/parameters.ipynb", ["+nbprint.parameters.a=10", "+nbprint.parameters.b='hello'", "+nbprint.parameters.d=True"])
    output = res.outputs.notebook.read_text()
    nb = reads(output, as_version=4)
    first_cell = nb.cells[0]
    for k, v in [("a", 10), ("b", "'hello'"), ("d", True), ("c", "'abc'")]:
        assert f"{k} = {v}" in first_cell.source
