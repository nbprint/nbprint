from contextlib import suppress
from json import JSONDecodeError, loads
from pathlib import Path

from ccflow import CallableModel, ContextBase, Flow, ResultBase
from pydantic import Field, PrivateAttr, model_validator

from .config import Configuration, Outputs
from .parameters import PapermillParameters, Parameters

__all__ = ("Executor",)


class ExecutorParameters(ContextBase):
    parameters: list[Parameters]


class ExecutorOutputs(ResultBase):
    outputs: list[Outputs]


class Executor(CallableModel):
    # Common with Configuration
    debug: bool | None = Field(default=False)

    nbprint: Configuration
    parameters: list[Parameters] = Field(default_factory=list)
    outputs: list[Outputs] = Field(default_factory=list)

    _nbprints: list[Configuration] = PrivateAttr(default_factory=list)
    _parameters: list[Parameters] = PrivateAttr(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _parameters_list_to_list(cls, values) -> dict:
        if "parameters" in values:
            if isinstance(values["parameters"], str):
                # If its a file, try to read it
                parameters_str = values["parameters"]
                if Path(parameters_str).exists():
                    if parameters_str.endswith((".json",)):
                        with open(parameters_str) as f:
                            values["parameters"] = f.read()
                    elif parameters_str.endswith((".jsonl", ".yml")):
                        with open(parameters_str) as f:
                            values["parameters"] = f"[{f.read()}]"
                with suppress(JSONDecodeError):
                    # Try parse as json
                    values["parameters"] = loads(values["parameters"])
            if isinstance(values["parameters"], dict):
                values["parameters"] = [PapermillParameters(**values["parameters"])]
            if isinstance(values["parameters"], list):
                values["parameters"] = [p if isinstance(p, Parameters) else PapermillParameters(**p) for p in values["parameters"]]
        return values

    @Flow.deps
    def __deps__(self, context: ExecutorParameters) -> list[tuple[Configuration, PapermillParameters]]:
        # TODO: Make sure outputs will not clobber
        # TODO: vars is ugly hack, need to fix in papermill parameters
        self._nbprints = [self.nbprint.model_copy(deep=True, update={"_multi": True}) for _ in context.parameters]
        self._parameters = context.parameters
        return list(
            zip(
                self._nbprints,
                [[_] for _ in self._parameters],
                strict=True,
            )
        )

    @Flow.call
    def __call__(self, context: ExecutorParameters = None) -> ExecutorOutputs:  # noqa: ARG002
        op = []
        for p in self._parameters:
            nb = self.nbprint.model_copy(deep=True, update={"_multi": True})
            op.append(nb(p.model_copy(deep=True)))
        self.outputs = op
        return ExecutorOutputs(outputs=op)

    def run(self, dry_run: bool = False) -> ExecutorOutputs:
        if dry_run:
            raise NotImplementedError
        res = self(ExecutorParameters(parameters=self.parameters))
        # Run outputs postprocessing
        if res.outputs and res.outputs[0].postprocess:
            # Run postprocessing
            res.outputs[0].postprocess.object(self._nbprints)
        return res
