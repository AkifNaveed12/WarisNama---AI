import sys
import io
from app.core.config import settings
if str(settings.BASE_DIR) not in sys.path:
    sys.path.insert(0, str(settings.BASE_DIR))

from docs.pdf_builder import (
    generate_share_certificate_pdf,
    generate_legal_notice_pdf,
    generate_fir_pdf,
    create_certificate_data_from_shares
)
from docs.templates.legal_notice import get_legal_notice_data
from docs.templates.fir_draft import get_fir_data

def generate_share_certificate(data: dict) -> bytes:
    buffer = io.BytesIO()
    generate_share_certificate_pdf(data, buffer=buffer)
    return buffer.getvalue()

def generate_legal_notice(dispute_data: dict, overrides: dict = None) -> bytes:
    notice_data = get_legal_notice_data()
    if overrides:
        notice_data.update(overrides)
    buffer = io.BytesIO()
    generate_legal_notice_pdf(notice_data, buffer=buffer)
    return buffer.getvalue()

def generate_fir(overrides: dict = None) -> bytes:
    fir_data = get_fir_data()
    if overrides:
        fir_data.update(overrides)
    buffer = io.BytesIO()
    generate_fir_pdf(fir_data, buffer=buffer)
    return buffer.getvalue()

def prepare_certificate_data(
    deceased_name, deceased_father, death_date, sect,
    total_estate, shares, heir_name, heir_cnic, heir_father,
    heir_relationship, property_description
) -> dict:
    return create_certificate_data_from_shares(
        deceased_name, deceased_father, death_date, sect,
        total_estate, shares, heir_name, heir_cnic, heir_father,
        heir_relationship, property_description
    )
