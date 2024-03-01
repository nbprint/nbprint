from typing import List

from nbprint.config import Parameters

# from datetime import datetime
# from pydantic import Field
# from typing import Dict, List, Optional


class ExampleFinanceParameters(Parameters):
    ticker: str
    authors: List[str] = []
    color: str
    # publish_date: Optional[datetime] = Field(default_factory=datetime.today)
