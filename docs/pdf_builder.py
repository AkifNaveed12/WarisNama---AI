"""
pdf_builder.py – Pakistani Legal Document PDF Generator
Full, properly formatted FIR, Legal Notice, and Share Certificate.
Fixed variable shadowing in FIR generator.
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Register Urdu font ────────────────────────────────────────────────────────
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
URDU_FONT_PATH = os.path.join(FONT_DIR, "NotoNastaliqUrdu.ttf")
URDU_AVAILABLE = False
if os.path.exists(URDU_FONT_PATH):
    try:
        pdfmetrics.registerFont(TTFont('UrduFont', URDU_FONT_PATH))
        URDU_AVAILABLE = True
    except:
        pass

# ── Page margins ──────────────────────────────────────────────────────────────
MARGIN_LEFT   = 2.5 * cm
MARGIN_RIGHT  = 2.0 * cm
MARGIN_TOP    = 2.0 * cm
MARGIN_BOTTOM = 2.0 * cm
PAGE_W, PAGE_H = A4

# ── Colour palette ────────────────────────────────────────────────────────────
C_BLACK  = colors.black
C_DARK   = colors.HexColor("#1A1A1A")
C_BLUE   = colors.HexColor("#003366")
C_LTBLUE = colors.HexColor("#E8F0F7")
C_GREY   = colors.HexColor("#666666")
C_LINE   = colors.HexColor("#2E4A7A")
C_TABLE_H= colors.HexColor("#2E4A7A")

# ── Base styles ───────────────────────────────────────────────────────────────
_base = getSampleStyleSheet()

def _style(name, **kw):
    return ParagraphStyle(name, **kw)

S = {
    "normal": _style("Normal", fontName="Times-Roman", fontSize=10, leading=14,
                     textColor=C_DARK, alignment=TA_JUSTIFY),
    "bold": _style("Bold", fontName="Times-Bold", fontSize=10, leading=14,
                   textColor=C_DARK),
    "small": _style("Small", fontName="Times-Roman", fontSize=8.5, leading=12,
                    textColor=C_GREY),
    "center": _style("Center", fontName="Times-Roman", fontSize=10, leading=14,
                     textColor=C_DARK, alignment=TA_CENTER),
    "right": _style("Right", fontName="Times-Roman", fontSize=10, leading=14,
                    textColor=C_DARK, alignment=TA_RIGHT),
    "title": _style("Title", fontName="Times-Bold", fontSize=14, leading=18,
                    textColor=C_BLUE, alignment=TA_CENTER, spaceAfter=4),
    "subtitle": _style("SubTitle", fontName="Times-Bold", fontSize=11, leading=15,
                       textColor=C_BLUE, alignment=TA_CENTER, spaceAfter=2),
    "h1": _style("H1", fontName="Times-Bold", fontSize=11, leading=15,
                 textColor=C_DARK, spaceAfter=4, spaceBefore=6),
    "h2": _style("H2", fontName="Times-Bold", fontSize=10, leading=14,
                 textColor=C_DARK, spaceAfter=2, spaceBefore=4),
    "para": _style("Para", fontName="Times-Roman", fontSize=10, leading=14.5,
                   textColor=C_DARK, alignment=TA_JUSTIFY,
                   firstLineIndent=18, spaceAfter=5),
    "label": _style("Label", fontName="Times-Bold", fontSize=9.5, leading=13,
                    textColor=C_DARK),
    "value": _style("Value", fontName="Times-Roman", fontSize=9.5, leading=13,
                    textColor=C_DARK),
    "center_bold": _style("CenterBold", fontName="Times-Bold", fontSize=11, leading=15,
                          textColor=C_DARK, alignment=TA_CENTER),
    "small_center": _style("SmallCenter", fontName="Times-Roman", fontSize=8.5, leading=12,
                           textColor=C_GREY, alignment=TA_CENTER),
}
if URDU_AVAILABLE:
    S["urdu"] = _style("Urdu", fontName="UrduFont", fontSize=12, leading=18,
                       textColor=C_DARK, alignment=TA_RIGHT)

def HR(color=C_LINE, thickness=1):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=4, spaceBefore=4)

def SP(h=6):
    return Spacer(1, h)

def P(text, style="normal"):
    return Paragraph(str(text), S[style] if isinstance(style, str) else style)

def field_row(label, value, label_width=4.5*cm):
    w = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
    return Table(
        [[Paragraph(label, S["label"]), Paragraph(value, S["value"])]],
        colWidths=[label_width, w - label_width],
        style=TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ])
    )

def section_heading(text):
    return P(f"<b><u>{text}</u></b>", "h1")

def number_para(n, text):
    return P(f"{n}. &nbsp; {text}", "para")

def _num_to_words(n: int) -> str:
    ones = ["","One","Two","Three","Four","Five","Six","Seven","Eight","Nine",
            "Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen",
            "Sixteen","Seventeen","Eighteen","Nineteen"]
    tens = ["","","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]
    if n < 20:
        return ones[n]
    return tens[n // 10] + ("" if n % 10 == 0 else "-" + ones[n % 10])

# ==============================================================================
# 1. FIR GENERATOR (Complete, properly formatted)
# ==============================================================================
def generate_fir_pdf(data: dict, output_path: Optional[str] = None, buffer=None):
    """Generate a complete, properly formatted Pakistani FIR PDF."""
    doc = SimpleDocTemplate(
        buffer if buffer else output_path,
        pagesize=A4,
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
    )
    story = []
    pw = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT   # renamed to avoid shadowing

    # Header
    is_fia = data.get("document_type", "POLICE").upper() == "FIA"
    if is_fia:
        story.append(P("FEDERAL INVESTIGATION AGENCY", "title"))
        story.append(P("FEDERAL GOVERNMENT OF PAKISTAN", "subtitle"))
    else:
        story.append(P(f"POLICE STATION — {data.get('police_station','').upper()}", "title"))
        story.append(P(f"PROVINCE OF {data.get('province','').upper()}", "subtitle"))

    story.append(HR(thickness=2))
    story.append(P("FIRST INFORMATION REPORT", "center_bold"))
    story.append(P("(FIRST INFORMATION OF A COGNIZABLE CRIME REPORTED UNDER "
                   "SECTION 154, CODE OF CRIMINAL PROCEDURE (Cr.P.C.))", "small_center"))
    story.append(HR())
    story.append(SP(4))

    # Form / Serial / PS / Circle row
    top_row = Table(
        [[
            P(f"<b>Form No:</b> FIR-{data.get('form_no','')}", "label"),
            P(f"<b>S. No:</b> {data.get('serial_no','')}", "center"),
            P(f"<b>Police Station:</b> {data.get('police_station','')}", "label"),
            P(f"<b>Circle / Sub-Circle:</b> {data.get('circle','')}", "label"),
        ]],
        colWidths=[pw*0.2, pw*0.2, pw*0.3, pw*0.3],
        style=TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,-1), C_LTBLUE),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
        ])
    )
    story.append(top_row)
    story.append(SP(6))

    # FIR No / Occurrence / Report / Place
    fir_info = Table(
        [
            [P(f"<b>FIR No:</b> {data.get('fir_no','')}", "label"),
             P(f"<b>Date & Hour of Occurrence:</b> {data.get('occurrence_date','')} {data.get('occurrence_time','')}", "label")],
            [P(f"<b>Date & Hour when reported:</b> {data.get('report_date','')} {data.get('report_time','')}", "label"),
             P(f"<b>Place of Occurrence:</b> {data.get('place_of_occurrence','')}", "label")],
        ],
        colWidths=[pw*0.5, pw*0.5],
        style=TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
        ])
    )
    story.append(fir_info)
    story.append(SP(8))

    # Informant / Complainant details
    story.append(section_heading("INFORMANT / COMPLAINANT DETAILS"))
    comp_rows = [
        ("Full Name:", data.get('informant_name', '')),
        ("Father's / Husband's Name:", data.get('informant_father', '')),
        ("CNIC No.:", data.get('informant_cnic', '')),
        ("Residential Address:", data.get('informant_address', '')),
        ("Phone No.:", data.get('informant_phone', '')),
    ]
    for lbl, val in comp_rows:
        story.append(field_row(lbl, val, 4.5*cm))
    story.append(SP(8))

    # Offence details
    story.append(section_heading("OFFENCE DETAILS"))
    off_rows = [
        ("Offence Sections (PPC / Special Laws):", data.get('offence_sections', '')),
        ("Act / Ordinance:", data.get('offence_act', '')),
        ("Additional Acts:", data.get('additional_acts', '')),
        ("Distance & Direction from PS:", data.get('distance_direction', '')),
        ("Mauza / Village:", data.get('mauza', '')),
        ("Tehsil:", data.get('tehsil', '')),
        ("District:", data.get('district', '')),
    ]
    for lbl, val in off_rows:
        story.append(field_row(lbl, val, 5*cm))
    story.append(SP(8))

    # Accused person details
    story.append(section_heading("PARTICULARS OF ACCUSED PERSON(S)"))
    acc_rows = [
        ("Name:", data.get('accused_name', '')),
        ("Father's Name:", data.get('accused_father', '')),
        ("CNIC:", data.get('accused_cnic', '')),
        ("Address:", data.get('accused_address', '')),
        ("Description (if unknown):", data.get('accused_description', '')),
    ]
    for lbl, val in acc_rows:
        story.append(field_row(lbl, val, 4.5*cm))
    story.append(SP(8))

    # Stolen / recovered property
    if data.get('property_details'):
        story.append(section_heading("PROPERTY STOLEN / RECOVERED"))
        story.append(field_row("Description:", data.get('property_details', ''), 4.5*cm))
        story.append(field_row("Estimated Value:", data.get('property_value', ''), 4.5*cm))
        story.append(SP(8))

    # Investigation details
    story.append(section_heading("INVESTIGATION DETAILS"))
    inv_rows = [
        ("Investigating Officer:", data.get('investigation_officer', '')),
        ("IO Rank:", data.get('io_rank', '')),
        ("Reason for delay (if any):", data.get('delay_reason', '')),
        ("Murasila / Complaint Ref.:", data.get('murasila_no', '')),
        ("Date & Hour of despatch from PS:", f"{data.get('dispatch_date','')} {data.get('dispatch_time','')}"),
    ]
    for lbl, val in inv_rows:
        story.append(field_row(lbl, val, 5*cm))
    story.append(SP(8))

    # Witnesses
    witnesses = data.get('witnesses', [])
    if witnesses:
        story.append(section_heading("WITNESSES"))
        wit_data = [["Name / Father's Name", "CNIC", "Address"]]
        for wit in witnesses:            # ← fixed variable name (was 'w')
            wit_data.append([
                f"{wit.get('name','')}<br/>{wit.get('father','')}",
                wit.get('cnic',''),
                wit.get('address','')
            ])
        wit_table = Table(wit_data, colWidths=[pw*0.4, pw*0.25, pw*0.35],
            style=TableStyle([
                ("BACKGROUND", (0,0), (-1,0), C_TABLE_H),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, C_LTBLUE]),
            ]))
        story.append(wit_table)
        story.append(SP(8))

    # Narrative
    story.append(section_heading("STATEMENT / MURASILA OF COMPLAINANT"))
    story.append(SP(4))
    narrative = data.get('fir_narrative', '')
    for para in narrative.split("\n"):
        if para.strip():
            story.append(P(para.strip(), "para"))
    story.append(SP(10))

    # Signature block
    HR_line = "_" * 40
    sig_data = [
        [P(f"<b>Complainant's Signature / Thumb Impression</b><br/><br/>{HR_line}<br/>{data.get('complainant_signature','')}", "center"),
         P(f"<b>Station House Officer (SHO)</b><br/><br/>{HR_line}<br/>{data.get('sho_name','')}<br/>{data.get('sho_designation','')}", "center")],
    ]
    sig_table = Table(sig_data, colWidths=[pw*0.5, pw*0.5],
        style=TableStyle([
            ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
    story.append(sig_table)
    story.append(HR(thickness=2))
    story.append(P("This FIR was read over to the complainant, who confirmed it to be correct.", "small_center"))

    doc.build(story)
    print(f"[✓] FIR PDF generated: {output_path if output_path else 'buffer'}")


# ==============================================================================
# 2. LEGAL NOTICE GENERATOR (Professional layout)
# ==============================================================================
def generate_legal_notice_pdf(data: dict, output_path: Optional[str] = None, buffer=None):
    """Generate a professional legal notice PDF."""
    doc = SimpleDocTemplate(
        buffer if buffer else output_path,
        pagesize=A4,
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
    )
    story = []
    pw = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT

    # Letterhead
    lh_data = [[
        P(f"<b>{data.get('advocate_name','').upper()}</b><br/>"
          f"<i>{data.get('advocate_designation','')}</i><br/>"
          f"{data.get('firm_name','')}<br/>"
          f"{data.get('enrollment_no','')}", "bold"),
        P(f"{data.get('firm_address_line1','')}<br/>"
          f"{data.get('firm_address_line2','')}<br/>"
          f"{data.get('firm_phone','')} &nbsp; {data.get('firm_cell','')}<br/>"
          f"{data.get('firm_email','')}", "right"),
    ]]
    lh_table = Table(lh_data, colWidths=[pw*0.5, pw*0.5],
        style=TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
    story.append(lh_table)
    story.append(HR(thickness=2, color=C_BLUE))
    story.append(HR(thickness=0.5, color=C_BLUE))
    story.append(SP(8))

    # Meta
    meta = Table(
        [[P(data.get("ref_no",""), "label"), P(f"<b>Dated:</b> {data.get('notice_date','')}", "right")]],
        colWidths=[pw*0.5, pw*0.5],
        style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"), ("TOPPADDING",(0,0),(-1,-1),0), ("BOTTOMPADDING",(0,0),(-1,-1),4)])
    )
    story.append(meta)
    story.append(P(f"<b>Sent By: {data.get('notice_mode','REGISTERED A.D.')}</b>", "right"))
    story.append(SP(8))

    # Noticee
    story.append(P("To,", "bold"))
    story.append(P(f"<b>{data.get('noticee_name','')}</b>", "normal"))
    story.append(P(data.get("noticee_father",""), "normal"))
    story.append(P(data.get("noticee_cnic",""), "normal"))
    story.append(P(data.get("noticee_address",""), "normal"))
    story.append(SP(10))

    # Subject
    story.append(P(f"<b>Sub: &nbsp; {data.get('subject','')}</b>",
                   _style("SubjectStyle", fontName="Times-Bold", fontSize=10.5, leading=14,
                          textColor=C_DARK, alignment=TA_JUSTIFY,
                          borderPad=4, borderColor=C_BLUE, borderWidth=0,
                          backColor=C_LTBLUE, leftIndent=4, rightIndent=4,
                          spaceAfter=6)))
    story.append(HR())
    story.append(SP(6))

    story.append(P("Sir / Madam,", "normal"))
    story.append(SP(4))
    story.append(P(
        f"Under the instructions and on behalf of my client, "
        f"<b>{data.get('client_name','')}</b>, "
        f"{data.get('client_father','')}, CNIC No. {data.get('client_cnic','')}, "
        f"resident of {data.get('client_address','')}, "
        f"I hereby serve upon you with the following Legal Notice:",
        "para"))
    story.append(SP(4))

    for i, para in enumerate(data.get("grievance_paras", []), 1):
        story.append(number_para(i, para))
    story.append(SP(6))

    # Legal Basis
    story.append(section_heading("LEGAL BASIS"))
    if data.get("ppc_sections"):
        story.append(field_row("PPC Sections:", data["ppc_sections"], 3.5*cm))
    if data.get("cpc_sections"):
        story.append(field_row("CPC / Civil:", data["cpc_sections"], 3.5*cm))
    if data.get("special_laws"):
        story.append(field_row("Other Laws:", data["special_laws"], 3.5*cm))
    story.append(SP(8))

    # Demands
    story.append(section_heading("DEMANDS / RELIEFS SOUGHT"))
    for i, demand in enumerate(data.get("relief_demanded", []), 1):
        story.append(number_para(i, demand))
    story.append(SP(8))

    days = data.get("compliance_days", 15)
    story.append(P(
        f"You are hereby called upon to comply with the above demands within "
        f"<b>{days} ({_num_to_words(days)}) days</b> from the receipt of this notice.",
        "para"))
    story.append(SP(6))
    story.append(P(data.get("closing_warning",""), "para"))
    story.append(SP(14))

    story.append(P("Yours faithfully,", "normal"))
    story.append(SP(24))
    story.append(HR(color=C_DARK))
    story.append(P(f"<b>{data.get('signatory_name','')}</b>", "normal"))
    story.append(P(data.get("signatory_designation","").replace("\n","<br/>"), "normal"))
    story.append(P(data.get("bar_council",""), "small"))
    story.append(SP(10))

    encl = data.get("enclosures", [])
    if encl:
        story.append(P("<b>Enclosures:</b>", "bold"))
        for e in encl:
            story.append(P(f"&nbsp;&nbsp;&#9679;&nbsp; {e}", "small"))

    doc.build(story)
    print(f"[✓] Legal Notice PDF generated: {output_path if output_path else 'buffer'}")


# ==============================================================================
# 3. SHARE CERTIFICATE GENERATOR (Detailed)
# ==============================================================================
def generate_share_certificate_pdf(data: dict, output_path: Optional[str] = None, buffer=None):
    """Generate a detailed property share certificate PDF."""
    doc = SimpleDocTemplate(
        buffer if buffer else output_path,
        pagesize=A4,
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
    )
    story = []
    pw = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT

    # Official Header
    story.append(P("ISLAMIC REPUBLIC OF PAKISTAN", "small_center"))
    story.append(P("GOVERNMENT OF PAKISTAN", "small_center"))
    story.append(SP(4))
    story.append(HR(thickness=2, color=C_BLUE))
    story.append(P(data.get("authority_office",""), "small_center"))
    story.append(HR(thickness=0.5, color=C_BLUE))
    story.append(SP(6))
    story.append(P("PROPERTY SHARE CERTIFICATE", "title"))
    story.append(P("(HISSA CERTIFICATE / WIRASAT CERTIFICATE)", "subtitle"))
    story.append(SP(4))
    story.append(HR())
    story.append(SP(6))

    # Certificate No / Date
    meta = Table(
        [[P(f"<b>Certificate No:</b> {data.get('certificate_no','')}", "label"),
          P(f"<b>Date of Issue:</b> {data.get('issue_date','')}", "center"),
          P(f"<b>Place of Issue:</b> {data.get('issue_place','')}", "right")]],
        colWidths=[pw*0.38, pw*0.30, pw*0.32],
        style=TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                          ("TOPPADDING",(0,0),(-1,-1),3),
                          ("BOTTOMPADDING",(0,0),(-1,-1),3)])
    )
    story.append(meta)
    story.append(SP(10))

    # Deceased
    story.append(section_heading("1. PARTICULARS OF DECEASED PROPERTY OWNER (MARHOOM)"))
    dec_fields = [
        ("Full Name:", data.get("deceased_name","")),
        ("Father's Name:", data.get("deceased_father","")),
        ("CNIC No:", data.get("deceased_cnic","")),
        ("Religion:", data.get("deceased_religion","")),
        ("Date of Death:", data.get("date_of_death","")),
        ("Death Certificate No:", data.get("death_cert_no","")),
        ("District of Domicile:", data.get("domicile_district","")),
    ]
    for lbl, val in dec_fields:
        story.append(field_row(lbl, val, 4.5*cm))
    story.append(SP(8))

    # Property
    story.append(section_heading("2. DETAILS OF INHERITED PROPERTY"))
    prop_fields = [
        ("Khasra / Plot No:", data.get("property_khasra","")),
        ("Khewat No:", data.get("property_khewat_no","")),
        ("Mauza / Locality:", data.get("property_mauza","")),
        ("Tehsil:", data.get("property_tehsil","")),
        ("District:", data.get("property_district","")),
        ("Total Area:", data.get("total_property_area","")),
        ("Property Type:", data.get("property_type","")),
    ]
    for lbl, val in prop_fields:
        story.append(field_row(lbl, val, 4.8*cm))
    story.append(SP(8))

    # Heir
    story.append(section_heading("3. PARTICULARS OF CERTIFICATE HOLDER (HEIR)"))
    heir_fields = [
        ("Full Name:", data.get("heir_name","")),
        ("Father's / Husband's Name:", data.get("heir_father","")),
        ("CNIC No:", data.get("heir_cnic","")),
        ("Relationship to Deceased:", data.get("heir_relationship","")),
        ("Share (Fraction):", data.get("heir_share_fraction","")),
        ("Share (Percentage):", data.get("heir_share_percent","")),
    ]
    for lbl, val in heir_fields:
        story.append(field_row(lbl, val, 5.5*cm))
    story.append(SP(8))

    # All heirs table
    story.append(section_heading("4. COMPLETE LIST OF ALL LEGAL HEIRS (WARSA)"))
    heirs = data.get("all_heirs", [])
    if heirs:
        hdr = [P("<b>S#</b>", "label"), P("<b>Name / Father</b>", "label"),
               P("<b>CNIC</b>", "label"), P("<b>Relationship</b>", "label"), P("<b>Share</b>", "label")]
        rows = [hdr]
        for i, h in enumerate(heirs, 1):
            rows.append([
                P(str(i), "value"),
                P(f"{h.get('name','')}<br/>{h.get('father','')}", "value"),
                P(h.get("cnic",""), "value"),
                P(h.get("relationship",""), "value"),
                P(h.get("share",""), "value"),
            ])
        tbl = Table(rows, colWidths=[pw*0.08, pw*0.35, pw*0.22, pw*0.15, pw*0.20],
            style=TableStyle([
                ("BACKGROUND", (0,0), (-1,0), C_TABLE_H),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, C_LTBLUE]),
            ]))
        story.append(tbl)
    story.append(SP(8))

    # Legal basis
    story.append(section_heading("5. LEGAL BASIS"))
    story.append(field_row("Inheritance Basis:", data.get("inheritance_basis",""), 4.8*cm))
    story.append(SP(8))

    # Certificate body
    story.append(HR())
    story.append(SP(6))
    story.append(P(data.get("certificate_body",""), "para"))
    story.append(SP(6))
    story.append(P(data.get("disclaimer",""), _style("DisclaimerStyle",
        fontName="Times-Italic", fontSize=9, leading=13,
        textColor=C_GREY, alignment=TA_JUSTIFY)))
    story.append(SP(10))
    story.append(HR())

    # Signature block
    HR_line = "_" * 36
    sig_data = [[
        P(f"Witness 1:<br/>{HR_line}<br/>{data.get('witness1_name','')}", "center"),
        P(f"Witness 2:<br/>{HR_line}<br/>{data.get('witness2_name','')}", "center"),
        P(f"Issuing Authority:<br/>{HR_line}<br/><b>{data.get('attesting_officer','')}</b><br/>{data.get('attesting_designation','')}", "center"),
    ]]
    sig_table = Table(sig_data, colWidths=[pw*0.33, pw*0.33, pw*0.34],
        style=TableStyle([
            ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
    story.append(sig_table)
    story.append(HR(thickness=2))

    doc.build(story)
    print(f"[✓] Share Certificate PDF generated: {output_path if output_path else 'buffer'}")


# ==============================================================================
# 4. HELPER: Convert app's shares to certificate data
# ==============================================================================
def create_certificate_data_from_shares(
    deceased_name: str,
    deceased_father: str,
    death_date: str,
    sect: str,
    total_estate: float,
    shares: dict,
    heir_name: str,
    heir_cnic: str,
    heir_father: str,
    heir_relationship: str,
    property_description: str = "Inherited Property"
) -> dict:
    """Convert WarisNama calculation output into Share Certificate data dict."""
    from docs.templates.share_certificate import get_share_certificate_data

    heir_share = shares.get(heir_name, {})
    fraction = heir_share.get("fraction", "N/A")
    amount = heir_share.get("amount", 0)

    all_heirs = []
    for hid, hdata in shares.items():
        all_heirs.append({
            "name": hid.replace("_", " ").title(),
            "father": "[Father's Name]",
            "cnic": "[CNIC]",
            "relationship": hid.split("_")[0].title(),
            "share": hdata.get("fraction", "N/A"),
        })

    base = get_share_certificate_data()
    base.update({
        "deceased_name": deceased_name,
        "deceased_father": deceased_father,
        "date_of_death": death_date,
        "heir_name": heir_name.replace("_", " ").title(),
        "heir_father": heir_father,
        "heir_cnic": heir_cnic,
        "heir_relationship": heir_relationship,
        "heir_share_fraction": fraction,
        "heir_share_percent": f"{(amount/total_estate)*100:.1f}%" if total_estate else "0%",
        "all_heirs": all_heirs,
        "total_property_area": property_description,
        "inheritance_basis": f"{sect.title()} law",
        "certificate_no": f"WN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "issue_date": datetime.now().strftime("%d-%m-%Y"),
        "issue_place": "Online",
        "property_khasra": property_description,
        "property_mauza": "N/A",
        "property_tehsil": "N/A",
        "property_district": "N/A",
        "attesting_officer": "WarisNama AI System",
        "attesting_designation": "Digital Certificate",
        "witness1_name": "System Generated",
        "witness2_name": "System Generated",
        "certificate_body": (
            f"This is to certify that {heir_name.replace('_', ' ').title()}, "
            f"{heir_relationship} of the late {deceased_name}, is a legal heir "
            f"entitled to {fraction} share in the above property."
        ),
        "disclaimer": "This certificate is AI-generated. For legal purposes, consult a lawyer.",
    })
    return base


# ==============================================================================
# MAIN (for standalone testing)
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", choices=["fir","notice","certificate","all"], default="all")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    # Fix imports for standalone mode – add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from docs.templates.fir_draft import get_fir_data
    from docs.templates.legal_notice import get_legal_notice_data
    from docs.templates.share_certificate import get_share_certificate_data

    if args.doc in ("fir", "all"):
        generate_fir_pdf(get_fir_data(), args.out or "fir_document.pdf")
    if args.doc in ("notice", "all"):
        generate_legal_notice_pdf(get_legal_notice_data(), args.out or "legal_notice.pdf")
    if args.doc in ("certificate", "all"):
        generate_share_certificate_pdf(get_share_certificate_data(), args.out or "share_certificate.pdf")

    print("\n[✓] All selected documents generated successfully.")