from pydantic import Field

from nbprint.config import Parameters


class ExampleFinanceParameters(Parameters):
    ticker: str
    authors: list[str] = Field(default=[])
    color: str
