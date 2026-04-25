from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Dict, Optional
from app.services.document_service import (
    generate_share_certificate, generate_legal_notice, generate_fir,
    prepare_certificate_data
)

router = APIRouter(prefix="/documents", tags=["Documents"])

class ShareCertRequest(BaseModel):
    deceased_name: str
    deceased_father: str
    death_date: str
    sect: str
    total_estate: float
    heir_name: str
    heir_cnic: str
    heir_father: str
    heir_relationship: str
    shares: Dict
    property_description: str = "Inherited Property"

class LegalNoticeRequest(BaseModel):
    dispute_data: Dict
    overrides: Optional[Dict] = None

class FIRRequest(BaseModel):
    overrides: Optional[Dict] = None

@router.post("/share-certificate", response_class=Response)
async def share_certificate(request: ShareCertRequest):
    data = prepare_certificate_data(
        deceased_name=request.deceased_name,
        deceased_father=request.deceased_father,
        death_date=request.death_date,
        sect=request.sect,
        total_estate=request.total_estate,
        shares=request.shares,
        heir_name=request.heir_name,
        heir_cnic=request.heir_cnic,
        heir_father=request.heir_father,
        heir_relationship=request.heir_relationship,
        property_description=request.property_description
    )
    pdf_bytes = generate_share_certificate(data)
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=share_certificate.pdf"})

@router.post("/legal-notice", response_class=Response)
async def legal_notice(request: LegalNoticeRequest):
    pdf_bytes = generate_legal_notice(request.dispute_data, request.overrides)
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=legal_notice.pdf"})

@router.post("/fir", response_class=Response)
async def fir(request: FIRRequest):
    pdf_bytes = generate_fir(request.overrides)
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=fir.pdf"})
