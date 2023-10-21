from typing import Optional

import pandas as pd

from nbcx import NBCXContext


class ExampleContext(NBCXContext):
    df: Optional[pd.DataFrame] = None
