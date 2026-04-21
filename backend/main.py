#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WarisNama AI - FastAPI Backend
Intelligent Inheritance Dispute Resolution System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import all modules
from knowledge_base import get_tax_bracket, get_stamp_duty
from dispute_detector import detect_disputes
from faraid_engine import calculate_shares
from gemini_nlp import parse_scenario, parse_scenario_with_fallback
from legal_doc_generator import (
    generate_inheritance_certificate_pdf,
    generate_legal_notice,
    generate_legal_notice_pdf,
    generate_fir_draft,
    generate_fir_draft_pdf
)
from process_navigator import get_bilingual_steps, get_process_summary
from tax_engine import calculate_heir_tax, calculate_all_heirs_tax, get_family_tax_summary
from whatif_engine import simulate_what_if, simulate_compare_scenarios

app = FastAPI(
    title="WarisNama AI API",
    description="Pakistan's First Intelligent Inheritance Dispute Resolution System",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

class ParseScenarioRequest(BaseModel):
    input_text: str
    language: str = "urdu"
    use_fallback: bool = False
    sect: Optional[str] = None

class ParseScenarioResponse(BaseModel):
    deceased: Dict[str, str]
    heirs: List[Dict[str, Any]]
    assets: List[Dict[str, Any]]
    debts: List[Dict[str, Any]]
    will_mentioned: bool
    disputes_mentioned: bool
    dispute_description: Optional[str]
    sect_mentioned: Optional[str]
    confidence: float

class ShareCalculationRequest(BaseModel):
    sect: str
    heirs: Dict[str, int]
    total_estate: float
    debts: float = 0
    wasiyyat: float = 0
    movable_estate: Optional[float] = None

class ShareCalculationResponse(BaseModel):
    shares: Dict[str, Dict[str, Any]]
    error: Optional[str] = None

class DisputeDetectionRequest(BaseModel):
    mutation_by_single_heir: bool = False
    no_succession_certificate: bool = False
    one_heir_wants_sell: bool = False
    others_refuse: bool = False
    gift_deed_mentioned: bool = False
    donor_still_in_possession: bool = False
    will_mentioned: bool = False
    will_percentage: Optional[float] = None
    debts_mentioned: bool = False
    estate_distributed_before_debt: bool = False
    heir_age_under_18: bool = False
    legal_guardian_appointed: bool = False
    buyout_scenario: bool = False

class HeirTaxRequest(BaseModel):
    share_value: float
    filer_status: str
    action: str
    province: str = "Punjab"
    share_value_at_inheritance: Optional[float] = None

class CertificateRequest(BaseModel):
    deceased_name: str
    sect: str
    total_estate: float
    debts: float = 0
    wasiyyat: float = 0
    shares: Dict[str, Dict[str, Any]]
    language: str = "en"

class LegalNoticeRequest(BaseModel):
    sender_name: str
    deceased_name: str
    recipient_name: str
    recipient_address: str
    fraud_description: str
    law_section: str
    remedy: str
    language: str = "en"

class FIRDraftRequest(BaseModel):
    complainant_name: str
    deceased_name: str
    accused_name: str
    fraud_description: str
    law_section: str
    accused_action: str
    evidence_list: str
    police_station_name: str = "Local Police Station"

class ProcessNavigatorRequest(BaseModel):
    minor_heir: bool = False
    has_dispute: bool = False
    sect: str = "hanafi"
    province: str = "Punjab"

class WhatIfRequest(BaseModel):
    sect: str
    heirs: Dict[str, int]
    total_estate: float
    scenario_type: str
    debts: float = 0
    wasiyyat: float = 0
    excluded_heir_type: Optional[str] = None
    buying_heir_id: Optional[str] = None
    province: str = "Punjab"

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {"message": "WarisNama AI API", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "WarisNama AI"}

@app.post("/api/parse-scenario", response_model=ParseScenarioResponse)
async def parse_scenario_endpoint(request: ParseScenarioRequest):
    """Parse natural language inheritance description into structured data"""
    try:
        if request.use_fallback:
            result = parse_scenario_with_fallback(request.input_text)
        else:
            result = parse_scenario(request.input_text)
        
        if request.sect:
            result['sect_mentioned'] = request.sect
        
        return ParseScenarioResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/calculate-shares", response_model=ShareCalculationResponse)
async def calculate_shares_endpoint(request: ShareCalculationRequest):
    """Calculate inheritance shares based on sect and heirs"""
    try:
        kwargs = {}
        if request.movable_estate is not None:
            kwargs['movable_estate'] = request.movable_estate
        
        result = calculate_shares(
            sect=request.sect,
            heirs=request.heirs,
            total_estate=request.total_estate,
            debts=request.debts,
            wasiyyat=request.wasiyyat,
            **kwargs
        )
        
        if "error" in result:
            return ShareCalculationResponse(shares={}, error=result["error"])
        
        return ShareCalculationResponse(shares=result, error=None)
    except Exception as e:
        return ShareCalculationResponse(shares={}, error=str(e))

@app.post("/api/detect-disputes")
async def detect_disputes_endpoint(request: DisputeDetectionRequest):
    """Detect inheritance fraud patterns based on scenario flags"""
    result = detect_disputes(request.dict())
    return result

@app.post("/api/tax/calculate-heir")
async def calculate_heir_tax_endpoint(request: HeirTaxRequest):
    """Calculate taxes for a single heir"""
    result = calculate_heir_tax(
        share_value=request.share_value,
        filer_status=request.filer_status,
        action=request.action,
        province=request.province,
        share_value_at_inheritance=request.share_value_at_inheritance
    )
    return result

@app.post("/api/generate-certificate")
async def generate_certificate(request: CertificateRequest):
    """Generate inheritance share certificate PDF"""
    pdf_bytes = generate_inheritance_certificate_pdf(
        deceased_name=request.deceased_name,
        sect=request.sect,
        total_estate=request.total_estate,
        debts=request.debts,
        wasiyyat=request.wasiyyat,
        shares=request.shares,
        language=request.language
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=inheritance_certificate.pdf"}
    )

@app.post("/api/generate-legal-notice")
async def generate_legal_notice_endpoint(request: LegalNoticeRequest):
    """Generate legal notice PDF"""
    pdf_bytes = generate_legal_notice_pdf(
        sender_name=request.sender_name,
        deceased_name=request.deceased_name,
        recipient_name=request.recipient_name,
        recipient_address=request.recipient_address,
        fraud_description=request.fraud_description,
        law_section=request.law_section,
        remedy=request.remedy,
        language=request.language
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=legal_notice.pdf"}
    )

@app.post("/api/generate-fir-draft")
async def generate_fir_draft_endpoint(request: FIRDraftRequest):
    """Generate FIR draft PDF"""
    pdf_bytes = generate_fir_draft_pdf(
        complainant_name=request.complainant_name,
        deceased_name=request.deceased_name,
        accused_name=request.accused_name,
        fraud_description=request.fraud_description,
        law_section=request.law_section,
        accused_action=request.accused_action,
        evidence_list=request.evidence_list,
        police_station_name=request.police_station_name
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=fir_draft.pdf"}
    )

@app.post("/api/process-navigator/steps")
async def get_process_steps(request: ProcessNavigatorRequest):
    """Get step-by-step process guidance for succession"""
    steps = get_bilingual_steps(
        minor_heir=request.minor_heir,
        has_dispute=request.has_dispute
    )
    return steps

@app.post("/api/process-navigator/summary")
async def get_process_summary_endpoint(request: ProcessNavigatorRequest):
    """Get quick summary of the process"""
    summary = get_process_summary(
        minor_heir=request.minor_heir,
        has_dispute=request.has_dispute
    )
    return summary

@app.post("/api/whatif")
async def whatif_endpoint(request: WhatIfRequest):
    """What-if scenario simulation"""
    kwargs = {
        'debts': request.debts,
        'wasiyyat': request.wasiyyat,
        'province': request.province
    }
    if request.excluded_heir_type:
        kwargs['excluded_heir_type'] = request.excluded_heir_type
    if request.buying_heir_id:
        kwargs['buying_heir_id'] = request.buying_heir_id
    
    result = simulate_what_if(
        sect=request.sect,
        heirs=request.heirs,
        total_estate=request.total_estate,
        scenario_type=request.scenario_type,
        **kwargs
    )
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)