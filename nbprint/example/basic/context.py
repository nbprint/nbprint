import pandas as pd
from typing import Optional

from nbprint import Context


class ExampleContext(Context):
    df: Optional[pd.DataFrame] = None
