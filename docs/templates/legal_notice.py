"""
legal_notice.py
===============
Generates the data dictionary for a Pakistani Property Legal Notice
in formal English, following the standard advocate letterhead format
used in District Courts and High Courts of Pakistan.

Usage:
    from legal_notice import get_legal_notice_data
    data = get_legal_notice_data()          # generic template
    data = get_legal_notice_data(**kwargs)  # override specific fields
"""

from datetime import datetime


def get_legal_notice_data(**overrides):
    """
    Returns a dictionary representing a complete Pakistani Property
    Legal Notice document.

    Fields:
    -------
    ADVOCATE / LAW FIRM DETAILS (Letterhead)
    ─────────────────────────────────────────
    advocate_name        : str  - Full name of the advocate
    advocate_designation : str  - e.g. "Advocate High Court"
    firm_name            : str  - Law firm / chamber name (optional)
    firm_address_line1   : str  - Address line 1
    firm_address_line2   : str  - Address line 2 (city, district)
    firm_phone           : str  - Office telephone
    firm_cell            : str  - Mobile number
    firm_email           : str  - Email address
    bar_council          : str  - Bar council (e.g. "Punjab Bar Council")
    enrollment_no        : str  - Enrollment / Bar registration number

    NOTICE META
    ───────────
    ref_no               : str  - Reference number
    notice_date          : str  - Date of notice (DD Month YYYY)
    notice_mode          : str  - "REGISTERED A.D." or "COURIER"
    subject              : str  - Subject line of the notice

    RECIPIENT (NOTICEE)
    ───────────────────
    noticee_name         : str  - Full name of the noticee
    noticee_father       : str  - Father's / Husband's name
    noticee_cnic         : str  - CNIC of noticee
    noticee_address      : str  - Full postal address of noticee

    CLIENT (NOTIFIER)
    ─────────────────
    client_name          : str  - Full name of the client
    client_father        : str  - Father's / Husband's name
    client_cnic          : str  - CNIC of client
    client_address       : str  - Address of client

    PROPERTY DETAILS
    ────────────────
    property_description : str  - Khasra/Plot/Survey No., area, location
    property_location    : str  - Full address / mauza / tehsil / district
    property_type        : str  - "agricultural land" / "residential plot" / "house"
    property_area        : str  - Area (e.g. "5 Marla", "2 Kanal", "200 sq. yds.")
    registry_no          : str  - Registry / Sale Deed number (if applicable)
    registry_date        : str  - Date of registry deed
    fard_no              : str  - Fard-e-Malkiyat number (if applicable)

    DISPUTE TYPE & GRIEVANCES
    ──────────────────────────
    dispute_type         : str  - e.g. "illegal possession" / "fraudulent resale" /
                                   "partition" / "encroachment" / "mutation fraud"
    grievance_paras      : list - List of str paragraphs describing grievances (numbered)

    LEGAL BASIS
    ───────────
    ppc_sections         : str  - Applicable PPC sections
    cpc_sections         : str  - Applicable CPC sections
    special_laws         : str  - Other applicable laws
    relief_demanded      : list - List of str demands / reliefs sought
    compliance_days      : int  - Number of days given to comply (default 15)

    SIGNATURE BLOCK
    ───────────────
    signatory_name       : str  - Name appearing under signature
    signatory_designation: str  - Designation under signature
    enclosures           : list - List of documents enclosed
    """

    now = datetime.now()
    notice_date = now.strftime("%d %B %Y")

    default_data = {
        # ── Advocate / Letterhead ──────────────────────────────────────
        "advocate_name":        "[ADVOCATE'S FULL NAME]",
        "advocate_designation": "Advocate High Court",
        "firm_name":            "[LAW CHAMBER / ASSOCIATES NAME]",
        "firm_address_line1":   "Chamber No. [XXX], [Court Complex Name]",
        "firm_address_line2":   "[City] – [Postal Code], Pakistan",
        "firm_phone":           "Tel: [+92-XX-XXXXXXX]",
        "firm_cell":            "Cell: [0300-XXXXXXX]",
        "firm_email":           "[advocate@email.com]",
        "bar_council":          "Punjab Bar Council",
        "enrollment_no":        "Enrl. No. [XXXXX/XXXX]",

        # ── Notice Meta ────────────────────────────────────────────────
        "ref_no":           "Ref: [LN/XXXX/2025]",
        "notice_date":      notice_date,
        "notice_mode":      "REGISTERED A.D.",
        "subject": (
            "Legal Notice Regarding [Nature of Dispute – e.g., Illegal Possession / "
            "Fraudulent Resale / Encroachment / Partition] of Property – "
            "Immediate Compliance Required"
        ),

        # ── Noticee (Recipient) ────────────────────────────────────────
        "noticee_name":     "[Full Name of Noticee]",
        "noticee_father":   "S/o or D/o or W/o [Father's / Husband's Name]",
        "noticee_cnic":     "CNIC No. [XXXXX-XXXXXXX-X]",
        "noticee_address": (
            "[House/Plot No., Street/Gali, Mohalla/Colony, City, District, Pakistan]"
        ),

        # ── Client (Notifier) ──────────────────────────────────────────
        "client_name":      "[Full Name of Client]",
        "client_father":    "S/o or D/o or W/o [Father's / Husband's Name]",
        "client_cnic":      "CNIC No. [XXXXX-XXXXXXX-X]",
        "client_address": (
            "[House/Plot No., Street, Colony, City, District, Pakistan]"
        ),

        # ── Property Details ───────────────────────────────────────────
        "property_description": (
            "Land / Property bearing Khasra No. [XXXX], measuring [area], "
            "situated in Mauza [Name], Tehsil [Name], District [Name], Province [Name]"
        ),
        "property_location":    "[Full Address / Mauza / Tehsil / District / Province]",
        "property_type":        "[agricultural land / residential plot / house / commercial property]",
        "property_area":        "[X Marla / X Kanal / X Square Yards / X Acres]",
        "registry_no":          "[Registry / Sale Deed No. XXXX, dated DD-MM-YYYY]",
        "registry_date":        "[DD-MM-YYYY]",
        "fard_no":              "[Fard-e-Malkiyat / Record of Rights Reference No.]",

        # ── Dispute ────────────────────────────────────────────────────
        "dispute_type": "illegal possession and encroachment",
        "grievance_paras": [
            (
                "That my client, [Client Name], is the lawful and rightful owner of the "
                "above-described property, having acquired the same through a duly "
                "registered Sale Deed No. [XXXX] executed on [DD-MM-YYYY] before the "
                "Sub-Registrar, [District]. The said property stands recorded in the "
                "Revenue Record (Fard-e-Malkiyat) in the name of my client."
            ),
            (
                "That my client has been in continuous, peaceful, and uninterrupted "
                "possession of the aforementioned property since the date of its "
                "acquisition. All dues, taxes, and levies in respect of the said "
                "property have been duly discharged by my client."
            ),
            (
                "That it has come to the knowledge of my client through credible and "
                "reliable sources that you, the noticee, have unlawfully and without "
                "any legal right, title, or authority [describe the wrongful act, e.g., "
                "encroached upon the said property / illegally occupied the said premises "
                "/ initiated a fraudulent resale / caused interference in the peaceful "
                "possession of my client]. Such acts on your part are wholly illegal, "
                "unlawful, and without any lawful justification."
            ),
            (
                "That the said unlawful acts of the noticee constitute a cognizable "
                "criminal offence and give rise to civil liability under the laws of "
                "Pakistan, including but not limited to the provisions of the Pakistan "
                "Penal Code, 1860, and the Code of Civil Procedure, 1908. My client "
                "reserves the right to seek all appropriate legal remedies available "
                "under the law."
            ),
        ],

        # ── Legal Basis ────────────────────────────────────────────────
        "ppc_sections": (
            "Sections 420 (Cheating), 467 (Forgery of Valuable Security), "
            "468 (Forgery for Purpose of Cheating), 471 (Using Forged Document as Genuine), "
            "506 (Criminal Intimidation) of the Pakistan Penal Code, 1860"
        ),
        "cpc_sections": (
            "Order 39 Rules 1 & 2 read with Section 151 C.P.C. (Temporary Injunction); "
            "Section 42 Specific Relief Act, 1877 (Declaration of Title)"
        ),
        "special_laws": (
            "[Punjab Land Revenue Act, 1967 / Registration Act, 1908 / "
            "Stamp Act, 1899 / other applicable provincial / federal law]"
        ),

        # ── Relief Demanded ────────────────────────────────────────────
        "relief_demanded": [
            (
                "Immediately cease and desist from all unlawful interference with, "
                "encroachment upon, or illegal occupation of the above-described property."
            ),
            (
                "Restore peaceful and vacant possession of the said property to my client "
                "forthwith, in the same condition as before."
            ),
            (
                "Refrain from creating any third-party interest, encumbrance, mortgage, "
                "lease, or purported transfer of the said property."
            ),
            (
                "Pay all costs, damages, and losses suffered by my client as a consequence "
                "of your unlawful acts, which shall be quantified and claimed in the "
                "appropriate forum."
            ),
        ],

        # ── Compliance Period ──────────────────────────────────────────
        "compliance_days": 15,

        # ── Signature ─────────────────────────────────────────────────
        "signatory_name":        "[Advocate's Full Name]",
        "signatory_designation": "Advocate High Court\n[Bar Council Enrollment No.]",

        # ── Enclosures ─────────────────────────────────────────────────
        "enclosures": [
            "Copy of CNIC of Client",
            "Copy of registered Sale Deed / Title Document",
            "Copy of Fard-e-Malkiyat (Record of Rights)",
            "[Any other relevant document]",
        ],

        # ── Closing Warning ────────────────────────────────────────────
        "closing_warning": (
            "Please note that this Notice is being served upon you as a final "
            "opportunity to resolve this matter amicably and without recourse to "
            "litigation. In the event you fail to comply with the above demands within "
            "the stipulated period, my client shall be constrained to initiate "
            "appropriate civil and/or criminal proceedings against you before the "
            "competent court/authority of law, entirely at your risk and cost, without "
            "any further notice or intimation whatsoever. A copy of this Notice is "
            "being retained in my office for record and future reference."
        ),
    }

    default_data.update(overrides)
    return default_data


# ── Quick self-test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    data = get_legal_notice_data(
        advocate_name="Muhammad Aslam Khan",
        advocate_designation="Advocate Supreme Court of Pakistan",
        firm_name="Aslam & Associates Law Chamber",
        dispute_type="fraudulent resale of already sold land",
        compliance_days=14,
    )
    print(json.dumps(data, indent=2))