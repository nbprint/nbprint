from nbprint.config import Parameters


class ExampleFinanceParameters(Parameters):
    ticker: str
    authors: list[str] = []
    color: str
