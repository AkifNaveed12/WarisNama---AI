"""
share_certificate.py
====================
Generates the data dictionary for a Pakistani Property Share Certificate
(also known as Hissa Certificate / Wirasat Certificate / Partition Certificate).
This document certifies the share of a specific legal heir in inherited or
jointly-owned immovable property.

Issued by:  Revenue Authority / Patwari / Tehsildar / Civil Court
Governed by: Punjab Land Revenue Act 1967, Succession Act 1925,
             Muslim Family Laws Ordinance 1961, Registration Act 1908

Usage:
    from share_certificate import get_share_certificate_data
    data = get_share_certificate_data()          # generic template
    data = get_share_certificate_data(**kwargs)  # override specific fields
"""

from datetime import datetime


def get_share_certificate_data(**overrides):
    """
    Returns a dictionary representing a complete Pakistani Property
    Share Certificate (Hissa / Wirasat Certificate).

    Fields:
    ───────
    ISSUING AUTHORITY
    ─────────────────
    issuing_authority    : str  - Name of the issuing authority
    authority_designation: str  - Designation (Tehsildar / Patwari / SHC etc.)
    authority_office     : str  - Office name and address
    authority_stamp      : str  - Stamp text placeholder
    certificate_no       : str  - Certificate reference number
    issue_date           : str  - Date of issue (DD-MM-YYYY)
    issue_place          : str  - Place of issue

    DECEASED PROPERTY OWNER (MURRATH)
    ──────────────────────────────────
    deceased_name        : str  - Full name of the deceased owner
    deceased_father      : str  - Father's name of deceased
    deceased_cnic        : str  - CNIC of deceased (if known)
    deceased_religion    : str  - Religion (for applicable inheritance law)
    date_of_death        : str  - Date of death of the property owner
    death_cert_no        : str  - Death certificate number / NADRA ref
    domicile_district    : str  - District of domicile of deceased

    PROPERTY DETAILS
    ─────────────────
    property_khasra      : str  - Khasra/Khewat/Plot number(s)
    property_khewat_no   : str  - Khewat number (Jamabandi record)
    property_khatoni_no  : str  - Khatoni number
    property_mauza       : str  - Mauza / Village / Locality
    property_tehsil      : str  - Tehsil
    property_district    : str  - District
    property_province    : str  - Province
    total_property_area  : str  - Total area of the entire property
    total_shares         : str  - Total shares in property (e.g. "8/8" or "24/24")
    property_type        : str  - Type of property
    property_boundaries  : dict - {north, south, east, west} boundaries

    CERTIFICATE HOLDER (HEIR)
    ──────────────────────────
    heir_name            : str  - Full name of the heir receiving this certificate
    heir_father          : str  - Father's / Husband's name
    heir_cnic            : str  - CNIC of the heir
    heir_address         : str  - Current residential address of heir
    heir_relationship    : str  - Relationship to deceased (e.g. "Son", "Daughter", "Widow")
    heir_share_fraction  : str  - Share as fraction (e.g. "2/8", "1/4")
    heir_share_percent   : str  - Share as percentage (e.g. "25%")
    heir_share_area      : str  - Area corresponding to heir's share
    heir_share_marlas    : str  - Share in Marlas / Kanals / Acres

    ALL LEGAL HEIRS TABLE
    ──────────────────────
    all_heirs            : list - List of dicts, one per legal heir:
                                  {
                                    name        : str,
                                    father      : str,
                                    cnic        : str,
                                    relationship: str,
                                    share       : str,   # e.g. "2/8"
                                    area        : str,
                                  }

    LEGAL BASIS
    ────────────
    inheritance_basis    : str  - "Islamic (Muslim Personal Law)" / "Succession Act 1925"
    wirasat_court        : str  - Court that issued Wirasatnama (if applicable)
    wirasat_case_no      : str  - Court case number
    wirasat_date         : str  - Date of court order
    fard_reference       : str  - Fard-e-Malkiyat / Jamabandi reference
    mutation_no          : str  - Intiqal / Mutation number
    mutation_date        : str  - Date of mutation entry

    WITNESSES / ATTESTING OFFICERS
    ────────────────────────────────
    witnesses            : list - [{name, cnic, address, designation}]
    attesting_officer    : str  - Name of attesting/verifying officer
    attesting_designation: str  - Designation of attesting officer
    """

    now = datetime.now()
    issue_date = now.strftime("%d-%m-%Y")

    default_data = {
        # ── Issuing Authority ──────────────────────────────────────────
        "issuing_authority":     "[Name of Issuing Authority]",
        "authority_designation": "Tehsildar / Sub-Registrar / Revenue Officer",
        "authority_office": (
            "Office of the Tehsildar, [Tehsil Name], District [District Name], "
            "[Province], Pakistan"
        ),
        "authority_stamp":       "[OFFICIAL STAMP / SEAL OF ISSUING AUTHORITY]",
        "certificate_no":        "HSC-[XXXX]/[YEAR]",
        "issue_date":            issue_date,
        "issue_place":           "[City / Tehsil]",

        # ── Deceased Property Owner ────────────────────────────────────
        "deceased_name":        "[Full Name of Deceased Property Owner]",
        "deceased_father":      "S/o [Father's Name of Deceased]",
        "deceased_cnic":        "[XXXXX-XXXXXXX-X]",
        "deceased_religion":    "Islam",
        "date_of_death":        "[DD-MM-YYYY]",
        "death_cert_no":        "[NADRA Death Certificate No. / CNIC Cancellation Ref.]",
        "domicile_district":    "[District of Domicile of Deceased]",

        # ── Property Details ───────────────────────────────────────────
        "property_khasra":      "[Khasra No(s). e.g. 1234, 1235, 1236]",
        "property_khewat_no":   "[Khewat No. from Jamabandi]",
        "property_khatoni_no":  "[Khatoni No.]",
        "property_mauza":       "Mauza [Name of Village / Locality]",
        "property_tehsil":      "[Tehsil Name]",
        "property_district":    "[District Name]",
        "property_province":    "Punjab",
        "total_property_area":  "[X Kanal X Marla]  /  [X Acres]  /  [X Square Yards]",
        "total_shares":         "[8/8]  (Full / Total Shares in Property)",
        "property_type":        "[Agricultural Land / Residential Plot / House / Commercial]",
        "property_boundaries": {
            "north": "[Northern Boundary – Name / Road / Khasra No.]",
            "south": "[Southern Boundary – Name / Road / Khasra No.]",
            "east":  "[Eastern Boundary – Name / Road / Khasra No.]",
            "west":  "[Western Boundary – Name / Road / Khasra No.]",
        },
        "fard_reference":       "Fard-e-Malkiyat Ref. No. [XXXX], dated [DD-MM-YYYY]",
        "mutation_no":          "Intiqal / Mutation No. [XXXX]",
        "mutation_date":        "[DD-MM-YYYY]",

        # ── Certificate Holder (Primary Heir) ──────────────────────────
        "heir_name":            "[Full Name of Heir / Certificate Holder]",
        "heir_father":          "S/o or D/o or W/o [Father's / Husband's Name]",
        "heir_cnic":            "[XXXXX-XXXXXXX-X]",
        "heir_address": (
            "[House No., Street, Mohalla, City, District, Pakistan]"
        ),
        "heir_relationship":    "[Son / Daughter / Widow / Brother / Sister of Deceased]",
        "heir_share_fraction":  "[X/X]  (e.g. 2/8 or 1/4)",
        "heir_share_percent":   "[XX%]",
        "heir_share_area":      "[X Kanal X Marla]  /  [X Sq. Yds.]",
        "heir_share_marlas":    "[X Marla]  (if applicable)",

        # ── All Legal Heirs ────────────────────────────────────────────
        "all_heirs": [
            {
                "name":         "[Heir 1 Full Name]",
                "father":       "S/o [Father]",
                "cnic":         "[CNIC]",
                "relationship": "Son",
                "share":        "2/8",
                "area":         "[Area]",
            },
            {
                "name":         "[Heir 2 Full Name]",
                "father":       "S/o [Father]",
                "cnic":         "[CNIC]",
                "relationship": "Son",
                "share":        "2/8",
                "area":         "[Area]",
            },
            {
                "name":         "[Heir 3 Full Name]",
                "father":       "D/o [Father]",
                "cnic":         "[CNIC]",
                "relationship": "Daughter",
                "share":        "1/8",
                "area":         "[Area]",
            },
            {
                "name":         "[Heir 4 Full Name]",
                "father":       "W/o [Husband]",
                "cnic":         "[CNIC]",
                "relationship": "Widow (Wife)",
                "share":        "1/8",
                "area":         "[Area]",
            },
            {
                "name":         "[Heir 5 Full Name]",
                "father":       "D/o [Father]",
                "cnic":         "[CNIC]",
                "relationship": "Daughter",
                "share":        "1/8",
                "area":         "[Area]",
            },
            {
                "name":         "[Heir 6 Full Name]",
                "father":       "S/o [Father]",
                "cnic":         "[CNIC]",
                "relationship": "Son",
                "share":        "1/8",
                "area":         "[Area]",
            },
        ],

        # ── Legal Basis ────────────────────────────────────────────────
        "inheritance_basis": "Islamic Law (Muslim Personal Law / Sharia)",
        "applicable_laws": (
            "Succession Act, 1925; Muslim Family Laws Ordinance, 1961; "
            "Punjab Land Revenue Act, 1967; Registration Act, 1908; "
            "West Pakistan Rules under the Land Revenue Act, 1968"
        ),
        "wirasat_court":        "[Civil Court / District Court Name]",
        "wirasat_case_no":      "[Case No. / Suit No. XXXX/XXXX]",
        "wirasat_date":         "[DD-MM-YYYY]  (Date of Court Order)",

        # ── Witnesses ─────────────────────────────────────────────────
        "witnesses": [
            {
                "name":        "[Witness 1 Full Name]",
                "father":      "S/o [Father's Name]",
                "cnic":        "[CNIC]",
                "address":     "[Witness 1 Address]",
                "designation": "Neighbour / Patwari / Lambardar",
            },
            {
                "name":        "[Witness 2 Full Name]",
                "father":      "S/o [Father's Name]",
                "cnic":        "[CNIC]",
                "address":     "[Witness 2 Address]",
                "designation": "Neighbour / Patwari / Lambardar",
            },
        ],

        # ── Attesting Officer ──────────────────────────────────────────
        "attesting_officer":        "[Name of Attesting / Verifying Officer]",
        "attesting_designation":    "Patwari / Tehsildar / Sub-Registrar",
        "attesting_office":         "Office of [Designation], [Tehsil], [District]",

        # ── Certificate Body Text ──────────────────────────────────────
        "certificate_body": (
            "This is to certify that [Heir Name], [Relationship] of the late "
            "[Deceased Name], is a bona fide legal heir and is entitled to "
            "[Share Fraction] share in the above-described immovable property, "
            "in accordance with the applicable laws of inheritance and succession "
            "of the Islamic Republic of Pakistan. This certificate is issued on "
            "the basis of the Wirasatnama / Heirship Certificate duly recorded "
            "in the Revenue Record, and is subject to verification of the "
            "Fard-e-Malkiyat / Jamabandi and other official documents."
        ),

        # ── Disclaimer ────────────────────────────────────────────────
        "disclaimer": (
            "This certificate is issued for the purpose of establishing the "
            "share of the above-named heir in the inherited property and shall "
            "not be construed as a transfer of title or as conferring any "
            "independent right of disposal without the written consent of all "
            "co-sharers or without the due process of law. Any dispute regarding "
            "the shares stated herein shall be subject to the jurisdiction of the "
            "competent Revenue Authority / Civil Court."
        ),
    }

    default_data.update(overrides)
    return default_data


# ── Quick self-test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    data = get_share_certificate_data(
        deceased_name="Muhammad Akbar Khan",
        deceased_father="S/o Muhammad Umar Khan",
        property_mauza="Mauza Chak 45/GB",
        property_district="Faisalabad",
        property_province="Punjab",
        heir_name="Muhammad Salman Khan",
        heir_relationship="Son",
        heir_share_fraction="2/8",
        heir_share_percent="25%",
    )
    print(json.dumps(data, indent=2))