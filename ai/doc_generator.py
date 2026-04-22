#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — doc_generator.py
=================================
Generates:
✔ Inheritance Certificate (PDF)
✔ Legal Notice (EN/UR)
✔ FIR Draft (UR)

Fully aligned with knowledge_base templates
"""

import io
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from core.knowledge_base import (
    INHERITANCE_CERTIFICATE_TEMPLATE,
    LEGAL_NOTICE_TEMPLATE_EN,
    LEGAL_NOTICE_TEMPLATE_URDU,
    FIR_DRAFT_TEMPLATE_URDU,
    generate_certificate_number,
    generate_ref_number,
    validate_estate,
    fraction_to_display
)


# ─────────────────────────────────────────────
# PDF BUILDER (CLEAN)
# ─────────────────────────────────────────────
def _build_pdf(text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    story = []

    for line in text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return buffer.getvalue()


# ─────────────────────────────────────────────
# INHERITANCE CERTIFICATE
# ─────────────────────────────────────────────
def generate_inheritance_certificate_pdf(
    deceased_name: str,
    death_date: str,
    sect: str,
    total_estate: float,
    debts: float,
    funeral: float,
    wasiyyat: float,
    shares: dict
) -> bytes:

    certificate_no = generate_certificate_number()
    ref_no = generate_ref_number("REF")

    # Correct estate validation
    distributable, _ = validate_estate(total_estate, debts, funeral)

    # Apply wasiyyat cap
    valid_wasiyyat = min(wasiyyat, distributable / 3)
    distributable -= valid_wasiyyat

    # Build share table
    share_lines = []
    for heir, data in shares.items():
        share_lines.append(
            f"{heir} → {data['fraction']} = PKR {data['amount']:,.0f}"
        )

    share_table = "\n".join(share_lines)

    content = INHERITANCE_CERTIFICATE_TEMPLATE.format(
        certificate_no=certificate_no,
        date=datetime.now().strftime("%Y-%m-%d"),
        ref_no=ref_no,
        deceased_name=deceased_name,
        death_date=death_date,
        sect=sect,
        total_estate=total_estate,
        debts=debts,
        funeral=funeral,
        wasiyyat=valid_wasiyyat,
        distributable=distributable,
        share_table=share_table
    )

    return _build_pdf(content)


# ─────────────────────────────────────────────
# LEGAL NOTICE
# ─────────────────────────────────────────────
def generate_legal_notice(
    sender_name: str,
    sender_address: str,
    sender_cnic: str,
    recipient_name: str,
    recipient_address: str,
    deceased_name: str,
    death_date: str,
    sect: str,
    sender_share_fraction: str,
    sender_share_amount: float,
    fraud_description: str,
    law_sections_list: str,
    remedy: str,
    language: str = "en"
) -> str:

    template = (
        LEGAL_NOTICE_TEMPLATE_URDU
        if language == "ur"
        else LEGAL_NOTICE_TEMPLATE_EN
    )

    return template.format(
        date=datetime.now().strftime("%d-%m-%Y"),
        ref_no=generate_ref_number("LN"),
        sender_name=sender_name,
        sender_address=sender_address,
        sender_cnic=sender_cnic,
        recipient_name=recipient_name,
        recipient_address=recipient_address,
        deceased_name=deceased_name,
        death_date=death_date,
        sect=sect,
        sender_share_fraction=sender_share_fraction,
        sender_share_amount=sender_share_amount,
        fraud_description=fraud_description,
        law_sections_list=law_sections_list,
        remedy=remedy
    )


# ─────────────────────────────────────────────
# FIR DRAFT (URDU)
# ─────────────────────────────────────────────
def generate_fir_draft(
    complainant_name: str,
    complainant_cnic: str,
    complainant_address: str,
    complainant_father_name: str,
    deceased_name: str,
    death_date: str,
    heirs_list: str,
    accused_name: str,
    accused_address: str,
    crime_description: str,
    evidence_list: str,
    police_station_name: str,
    police_station_address: str,
    ppc_sections: str = "498A"
) -> str:

    return FIR_DRAFT_TEMPLATE_URDU.format(
        ppc_sections=ppc_sections,
        police_station_name=police_station_name,
        police_station_address=police_station_address,
        complainant_name=complainant_name,
        complainant_cnic=complainant_cnic,
        complainant_father_name=complainant_father_name,
        complainant_address=complainant_address,
        deceased_name=deceased_name,
        death_date=death_date,
        heirs_list=heirs_list,
        accused_name=accused_name,
        accused_address=accused_address,
        crime_description=crime_description,
        evidence_list=evidence_list,
        date=datetime.now().strftime("%d-%m-%Y"),
        complainant_phone="N/A"
    )