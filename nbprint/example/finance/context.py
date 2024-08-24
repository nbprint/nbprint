from typing import Optional

import pandas as pd

from nbprint import Context


class ExampleFinanceContext(Context):
    df: Optional[pd.DataFrame] = None
