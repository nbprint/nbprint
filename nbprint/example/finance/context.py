import pandas as pd
from typing import Optional

from nbprint import Context


class ExampleFinanceContext(Context):
    df: Optional[pd.DataFrame] = None
