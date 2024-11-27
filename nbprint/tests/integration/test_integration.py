from pathlib import Path

import pytest
from nbformat import reads

from nbprint.cli import run_hydra


@pytest.mark.parametrize("file", list((Path(__file__).parent / "files").glob("*")))
def test_integrations(file):
    res = run_hydra(str(file.resolve()))

    # file specific tests
    if file.name == "capture.yaml":
        output = res.outputs.resolve_output(res).read_text()
        nb = reads(output, as_version=4)
        assert nb.cells[-1].source == '%%capture\nprint("test1")\nimport logging\nlogging.critical("test!")\n'
        assert nb.cells[-1].outputs == []

    if file.name == "plugins.yaml":
        output = res.outputs.resolve_output(res).read_text()
        assert "Example Page Content from Plugin" in output
