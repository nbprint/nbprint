import pandas as pd

from nbprint import Context


class ExampleFinanceContext(Context):
    df: pd.DataFrame | None = None
