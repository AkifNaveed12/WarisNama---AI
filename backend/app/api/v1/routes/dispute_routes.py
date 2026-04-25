from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.dispute_service import detect_disputes

router = APIRouter(prefix="/dispute", tags=["Dispute"])

class DisputeRequest(BaseModel):
    flags: Dict[str, Any]

@router.post("/detect")
async def detect(request: DisputeRequest):
    try:
        disputes = detect_disputes(request.flags)
        return {"status": "success", "data": disputes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
