from datetime import date, datetime

from pydantic import Field

from nbprint.config import Parameters

__all__ = ("ExampleParameters", "ExampleParametersVariousTypes")


class ExampleParameters(Parameters):
    string: str
    a: int | None = 4
    b: float | None = 4.5
    c: list[int] = Field(default=[1, 2, 3])
    d: dict[str, int] = Field(default={"A": 1, "B": 2, "C": 3})


class ExampleParametersVariousTypes(Parameters):
    a: bool
    b: str
    c: int
    d: float
    e: date
    f: datetime
    g: ExampleParameters
