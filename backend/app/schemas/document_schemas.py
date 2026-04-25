from pydantic import BaseModel
from typing import Optional, List

class ShareCertificateRequest(BaseModel):
    deceased_name: str
    deceased_father: str
    death_date: str
    sect: str
    total_estate: float
    heir_name: str
    heir_cnic: str
    heir_father: str
    heir_relationship: str
    shares: dict   # shares dict from calculation
    property_description: str = "Inherited Property"

class LegalNoticeRequest(BaseModel):
    top_dispute: dict   # from dispute detection
    # (minimal; we can also send full overrides)

class FIRRequest(BaseModel):
    accused_name: str
    fir_narrative: str
    # minimal – we will merge with template
