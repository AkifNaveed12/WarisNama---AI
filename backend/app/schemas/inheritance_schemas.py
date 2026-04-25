from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class HeirsInput(BaseModel):
    sons: int = 0
    daughters: int = 0
    wife: int = 0
    husband: int = 0
    mother: int = 0
    father: int = 0
    # For Christian
    spouse: Optional[int] = 0
    children: Optional[int] = 0
    # For Hindu
    widow: Optional[int] = 0

class CalculationRequest(BaseModel):
    sect: str = Field(..., description="hanafi / shia / christian / hindu")
    heirs: HeirsInput
    total_estate: float = Field(..., gt=0)
    debts: float = 0.0
    funeral: float = 0.0
    wasiyyat: float = 0.0
    # Optional MFLO predeceased sons
    predeceased_sons: Optional[List[Dict]] = None

class ShareItem(BaseModel):
    fraction: str
    amount: float
    reference: str
    note: Optional[str] = None

class CalculationResponse(BaseModel):
    distributable_estate: float
    warning: Optional[str] = None
    shares: Dict[str, ShareItem]
