from __future__ import annotations

from pydantic import Field

from nbprint.config import Parameters

# from datetime import datetime
# from pydantic import Field
# from typing import Dict, List, Optional


class ExampleFinanceParameters(Parameters):
    ticker: str
    authors: list[str] = Field(default=[])
    color: str
    # publish_date: Optional[datetime] = Field(default_factory=datetime.today)
