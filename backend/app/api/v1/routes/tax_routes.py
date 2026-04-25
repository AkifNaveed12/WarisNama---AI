from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from app.services.tax_service import calculate_taxes

router = APIRouter(prefix="/tax", tags=["Tax"])

class TaxRequest(BaseModel):
    heirs_shares: Dict[str, Dict]
    full_property_value_pkr: float
    filer_status_map: Dict[str, str] = None
    action: str = "sell"
    province: str = "Punjab"

@router.post("/calculate")
async def compute_taxes(request: TaxRequest):
    try:
        tax_result = calculate_taxes(
            heirs_shares=request.heirs_shares,
            full_property_value_pkr=request.full_property_value_pkr,
            filer_status_map=request.filer_status_map,
            action=request.action,
            province=request.province
        )
        return {"status": "success", "data": tax_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
