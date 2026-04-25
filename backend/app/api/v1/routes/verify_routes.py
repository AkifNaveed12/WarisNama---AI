# app/api/v1/routes/verify_routes.py
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.local_mufti_verification import (
    DEFAULT_MUFTI_EMAIL,
    MuftiVerificationError,
    build_verification_payload,
    decode_certificate_base64,
    send_mufti_verification_email,
)

router = APIRouter(prefix="/verify", tags=["Verification"])

class MuftiVerificationRequest(BaseModel):
    results: Dict[str, Any] = Field(..., description="Final WarisNama result object with shares, tax, disputes, and estate data")
    case_details: Dict[str, Any] = Field(default_factory=dict)
    recipient_email: str = DEFAULT_MUFTI_EMAIL
    dry_run: bool = True
    certificate_base64: Optional[str] = None
    source: str = "api"

@router.post("/mufti")
async def request_mufti_verification(request: MuftiVerificationRequest):
    try:
        payload = build_verification_payload(
            results=request.results,
            case_details=request.case_details,
            source=request.source,
        )
        certificate_pdf = decode_certificate_base64(request.certificate_base64)
        result = send_mufti_verification_email(
            payload=payload,
            recipient_email=request.recipient_email,
            certificate_pdf=certificate_pdf,
            dry_run=request.dry_run,
        )
        return {"status": "success", "data": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except MuftiVerificationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Mufti verification failed: {exc}")