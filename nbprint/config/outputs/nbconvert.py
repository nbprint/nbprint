import os
from pathlib import Path
from typing import Literal, Optional

from nbformat import NotebookNode
from pydantic import field_validator

from nbprint.config import Configuration, Outputs

__all__ = ("HTMLOutputs", "NBConvertOutputs", "NotebookOutputs", "PDFOutputs")


class NBConvertOutputs(Outputs):
    target: Optional[Literal["ipynb", "html", "pdf", "webpdf"]] = "html"  # TODO: nbconvert types
    execute: Optional[bool] = True
    timeout: Optional[int] = 600
    template: Optional[str] = "nbprint"

    @field_validator("target", mode="before")
    @classmethod
    def validate_target(cls, v) -> str:
        if v is None:
            return "html"
        if v == "pdf":
            return "webpdf"
        return v

    def resolve_output(self, config: "Configuration") -> Path:
        # get original notebook
        original = str(super().resolve_output(config=config))
        target = self.target if self.target != "webpdf" else "pdf"
        if self.target == "ipynb":
            return Path(original.replace(".ipynb", ".nbconvert.ipynb"))
        return Path(original.replace(".ipynb", f".{target}"))

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        from nbconvert.nbconvertapp import main as execute_nbconvert

        # run the nbconvert
        notebook = super().run(config=config, gen=gen)

        cmd = [
            str(notebook),
            f"--to={self.target}",
            f"--template={self.template}",
        ]

        if self.execute:
            cmd.extend(
                [
                    "--execute",
                    f"--ExecutePreprocessor.timeout={self.timeout}",
                ]
            )

        # We have some cheats here because we have to
        os.environ["_NBPRINT_IN_NBCONVERT"] = "1"
        os.environ["PSP_JUPYTER_HTML_EXPORT"] = "1"
        execute_nbconvert(cmd)
        self._output_path = self.resolve_output(config=config)
        return self._output_path


class NotebookOutputs(NBConvertOutputs):
    target: Literal["ipynb"] = "ipynb"


class HTMLOutputs(NBConvertOutputs):
    target: Literal["html"] = "html"


class PDFOutputs(NBConvertOutputs):
    target: Literal["webpdf"] = "webpdf"


# class PapermillOutputs(NBConvertOutputs):
#     def run(self, config: "Configuration", gen: NotebookNode) -> Path:
#         from nbconvert.nbconvertapp import main

#         notebook = super().run(config=config, gen=gen)
#         main([notebook, f"--to={self.target}", f"--template={self.template}", "--execute"])
