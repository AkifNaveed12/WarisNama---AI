#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legal Document Generator – creates share certificates, legal notices, FIR drafts.
Uses ReportLab for PDF, and templates from knowledge_base.
"""

import io
import os
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

from knowledge_base import (
    LEGAL_NOTICE_TEMPLATE_EN, LEGAL_NOTICE_TEMPLATE_URDU,
    FIR_DRAFT_TEMPLATE_URDU, INHERITANCE_CERTIFICATE_TEMPLATE
)


def wrap_text(text: str, font_name: str, font_size: int, max_width: int) -> list:
    """Wrap text to fit within max_width."""
    return simpleSplit(text, font_name, font_size, max_width)


def generate_inheritance_certificate_pdf(
    deceased_name: str, sect: str, total_estate: float,
    debts: float, wasiyyat: float, shares: Dict[str, Dict[str, Any]],
    certificate_no: Optional[str] = None, language: str = 'en'
) -> bytes:
    """Generate PDF inheritance certificate."""
    if certificate_no is None:
        certificate_no = f"WN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    distributable = total_estate - debts - min(wasiyyat, total_estate * 1/3)
    
    share_rows = []
    for heir, data in shares.items():
        if 'error' not in data:
            fraction = data.get('fraction', '?')
            amount = data.get('amount', 0)
            share_rows.append(f"• {heir}: {fraction} = PKR {amount:,.0f}")
    
    share_table_text = "\n".join(share_rows)
    
    content = INHERITANCE_CERTIFICATE_TEMPLATE.format(
        certificate_no=certificate_no,
        date=datetime.now().strftime("%Y-%m-%d"),
        deceased_name=deceased_name,
        sect=sect.capitalize(),
        total_estate=total_estate,
        debts=debts,
        wasiyyat=wasiyyat,
        distributable=distributable,
        share_table=share_table_text
    )
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40
    
    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, y, "WARISNAMA AI")
    y -= 25
    
    c.setFont('Helvetica', 10)
    c.drawString(40, y, f"Inheritance Share Certificate | {certificate_no}")
    y -= 30
    
    c.setFont('Helvetica', 10)
    for line in content.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont('Helvetica', 10)
        
        wrapped_lines = wrap_text(line, 'Helvetica', 10, width - 80)
        for wrapped_line in wrapped_lines:
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont('Helvetica', 10)
            c.drawString(40, y, wrapped_line)
            y -= 15
    
    c.setFont('Helvetica-Oblique', 8)
    c.drawString(40, 30, "Disclaimer: This is an AI-generated estimate. Consult a lawyer for final legal action.")
    
    c.save()
    return buffer.getvalue()


def generate_legal_notice(
    sender_name: str, deceased_name: str, recipient_name: str,
    recipient_address: str, fraud_description: str, law_section: str,
    remedy: str, language: str = 'en'
) -> str:
    """Generate legal notice text."""
    if language == 'ur':
        template = LEGAL_NOTICE_TEMPLATE_URDU
    else:
        template = LEGAL_NOTICE_TEMPLATE_EN
    
    return template.format(
        date=datetime.now().strftime("%d-%m-%Y"),
        sender_name=sender_name,
        deceased_name=deceased_name,
        recipient_name=recipient_name,
        recipient_address=recipient_address,
        fraud_description=fraud_description,
        law_section=law_section,
        remedy=remedy
    )


def generate_legal_notice_pdf(
    sender_name: str, deceased_name: str, recipient_name: str,
    recipient_address: str, fraud_description: str, law_section: str,
    remedy: str, language: str = 'en'
) -> bytes:
    """Generate legal notice as PDF."""
    notice_text = generate_legal_notice(
        sender_name, deceased_name, recipient_name, recipient_address,
        fraud_description, law_section, remedy, language
    )
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40
    
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, "LEGAL NOTICE")
    y -= 25
    
    c.setFont('Helvetica', 10)
    for line in notice_text.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont('Helvetica', 10)
        
        wrapped_lines = wrap_text(line, 'Helvetica', 10, width - 80)
        for wrapped_line in wrapped_lines:
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont('Helvetica', 10)
            c.drawString(40, y, wrapped_line)
            y -= 15
    
    c.save()
    return buffer.getvalue()


def generate_fir_draft(
    complainant_name: str, deceased_name: str, accused_name: str,
    fraud_description: str, law_section: str, accused_action: str,
    evidence_list: str, police_station_name: str = "Local Police Station"
) -> str:
    """Generate FIR draft in Urdu."""
    return FIR_DRAFT_TEMPLATE_URDU.format(
        police_station_name=police_station_name,
        complainant_name=complainant_name,
        deceased_name=deceased_name,
        accused_name=accused_name,
        fraud_description=fraud_description,
        law_section=law_section,
        accused_action=accused_action,
        evidence_list=evidence_list
    )


def generate_fir_draft_pdf(
    complainant_name: str, deceased_name: str, accused_name: str,
    fraud_description: str, law_section: str, accused_action: str,
    evidence_list: str, police_station_name: str = "Local Police Station"
) -> bytes:
    """Generate FIR draft as PDF."""
    fir_text = generate_fir_draft(
        complainant_name, deceased_name, accused_name,
        fraud_description, law_section, accused_action,
        evidence_list, police_station_name
    )
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40
    
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, "FIR DRAFT - POLICE COMPLAINT")
    y -= 25
    
    c.setFont('Helvetica', 10)
    for line in fir_text.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
            c.setFont('Helvetica', 10)
        
        wrapped_lines = wrap_text(line, 'Helvetica', 10, width - 80)
        for wrapped_line in wrapped_lines:
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont('Helvetica', 10)
            c.drawString(40, y, wrapped_line)
            y -= 15
    
    c.save()
    return buffer.getvalue()


if __name__ == "__main__":
    test_shares = {
        'son_1': {'fraction': '1/2', 'amount': 4000000},
        'daughter_1': {'fraction': '1/4', 'amount': 2000000},
        'wife_1': {'fraction': '1/8', 'amount': 1000000},
    }
    
    pdf_bytes = generate_inheritance_certificate_pdf(
        deceased_name="Ahmed Khan", sect="Hanafi", total_estate=8000000,
        debts=500000, wasiyyat=500000, shares=test_shares
    )
    
    with open("test_certificate.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ Generated test_certificate.pdf")