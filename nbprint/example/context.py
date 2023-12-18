from typing import Optional

import pandas as pd

from nbprint import Context


class ExampleContext(Context):
    df: Optional[pd.DataFrame] = None
