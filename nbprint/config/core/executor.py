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
        return [(self.nbprint.model_copy(deep=True), [p.model_copy(deep=True)]) for p in context.parameters]

    @Flow.call
    def __call__(self, context: ExecutorParameters = None) -> ExecutorOutputs:
        op = []
        for p in context.parameters:
            nb = self.nbprint.model_copy(deep=True)
            nb(p.model_copy(deep=True))
            op.append(nb.outputs.model_copy(deep=True))
        self.outputs = op
        return ExecutorOutputs(outputs=op)

    def run(self, dry_run: bool = False) -> ExecutorOutputs:
        if dry_run:
            raise NotImplementedError
        return self(ExecutorParameters(parameters=self.parameters))
