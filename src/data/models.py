from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class FundManager(BaseModel):
    name: str
    experience: Optional[str] = None
    education: Optional[str] = None
    date_from: Optional[str] = None

class MutualFundScheme(BaseModel):
    scheme_name: str
    expense_ratio: float
    exit_load: str
    benchmark_name: str
    nav: float
    nav_date: str
    launch_date: str
    min_sip_amount: float
    riskometer: str
    url: str
    managers: List[FundManager]
