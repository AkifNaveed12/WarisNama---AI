from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.process_service import get_process_steps

router = APIRouter(prefix="/process", tags=["Process"])

class ProcessRequest(BaseModel):
    has_minor_heir: bool = False
    has_dispute: bool = False
    is_selling: bool = False

@router.post("/steps")
async def process_steps(request: ProcessRequest):
    steps = get_process_steps(
        has_minor_heir=request.has_minor_heir,
        has_dispute=request.has_dispute,
        is_selling=request.is_selling
    )
    return {"status": "success", "data": steps}