#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Legal Document Generator – creates share certificates, legal notices, FIR drafts.
Uses ReportLab for PDF, and templates from knowledge_base.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from knowledge_base import LEGAL_NOTICE_TEMPLATE_EN, LEGAL_NOTICE_TEMPLATE_URDU, FIR_DRAFT_TEMPLATE_URDU, INHERITANCE_CERTIFICATE_TEMPLATE

def generate_inheritance_certificate_pdf(deceased_name: str, sect: str, total_estate: float,
                                         debts: float, wasiyyat: float, shares: dict,
                                         certificate_no: str = None) -> bytes:
    """Generate PDF inheritance certificate."""
    if certificate_no is None:
        certificate_no = f"WN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    distributable = total_estate - debts - wasiyyat
    # Build share table rows
    share_rows = ""
    for heir, data in shares.items():
        share_rows += f"{heir}: {data['fraction']} = PKR {data['amount']:,.0f}\n"
    content = INHERITANCE_CERTIFICATE_TEMPLATE.format(
        certificate_no=certificate_no,
        date=datetime.now().strftime("%Y-%m-%d"),
        deceased_name=deceased_name,
        sect=sect,
        total_estate=total_estate,
        debts=debts,
        wasiyyat=wasiyyat,
        distributable=distributable,
        share_table=share_rows
    )
    # Create PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40
    for line in content.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line[:100])  # simple truncation
        y -= 15
    c.save()
    return buffer.getvalue()

def generate_legal_notice(sender_name: str, deceased_name: str, recipient_name: str,
                          recipient_address: str, fraud_description: str, law_section: str,
                          remedy: str, language: str = 'en') -> str:
    """Generate legal notice text (not PDF, for display/copy)."""
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

def generate_fir_draft(complainant_name: str, deceased_name: str, accused_name: str,
                       fraud_description: str, law_section: str, accused_action: str,
                       evidence_list: str, police_station_name: str = "Local Police Station") -> str:
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