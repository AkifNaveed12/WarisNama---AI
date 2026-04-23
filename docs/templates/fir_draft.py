"""
fir_draft.py
============
Generates the data dictionary for a Pakistani First Information Report (FIR)
based on the standard Form No. FIA-26 / Section 154 Cr.P.C. format.

Usage:
    from fir_draft import get_fir_data
    data = get_fir_data()          # returns populated generic template
    data = get_fir_data(**kwargs)  # override specific fields
"""

from datetime import datetime


def get_fir_data(**overrides):
    """
    Returns a dictionary representing a complete Pakistani FIR document.
    All placeholder values follow official Pakistani FIR field structure.

    Fields:
    -------
    form_no          : str  - Form number (e.g. "FIA-26" or "Police-15")
    serial_no        : str  - Serial / S. No. of the FIR
    police_station   : str  - Name of the Police Station / FIA ACC wing
    circle           : str  - Circle / Sub-Circle / Division
    fir_no           : str  - FIR registration number (e.g. "FIR62/2023")
    occurrence_date  : str  - Date and hour of occurrence of offence
    report_date      : str  - Date and hour when FIR was reported
    report_time      : str  - Time when FIR was reported (24-hr)
    informant_name   : str  - Full name of the complainant / informant
    informant_father : str  - Father's / husband's name of informant
    informant_cnic   : str  - CNIC number of informant (XXXXX-XXXXXXX-X)
    informant_address: str  - Residential address of informant
    informant_phone  : str  - Contact number of informant
    offence_sections : str  - Offence sections under PPC / special laws
    offence_act      : str  - Act under which sections invoked
    place_of_occurrence: str - Location / address where offence occurred
    distance_direction : str - Distance and direction from police station
    accused_name     : str  - Name(s) of accused (known / unknown)
    accused_father   : str  - Father's name of accused
    accused_address  : str  - Address of accused
    accused_cnic     : str  - CNIC of accused (if known)
    property_details : str  - Details of property carried off (if any)
    property_value   : str  - Estimated value of property (PKR)
    investigation_officer: str - Name & designation of IO assigned
    io_rank          : str  - Rank of investigating officer
    delay_reason     : str  - Reason for delay in recording (if any)
    murasila_no      : str  - Murasila / complaint reference number
    dispatch_date    : str  - Date and hour of despatch from police station
    dispatch_time    : str  - Time of despatch
    fir_narrative    : str  - Full narration of the offence / statement
    complainant_signature: str - "Thumb impression" or "Signature"
    sho_name         : str  - Name of Station House Officer
    sho_designation  : str  - Designation of SHO
    witnesses        : list - List of witness dicts [{name, address, cnic}]
    document_type    : str  - "FIA" or "POLICE" (controls header)
    province         : str  - Province (Punjab / Sindh / KPK / Balochistan)
    """

    now = datetime.now()
    current_date = now.strftime("%d-%m-%Y")
    current_time = now.strftime("%I:%M %p")

    default_data = {
        # ── Document Meta ──────────────────────────────────────────────
        "document_type":    "POLICE",          # "FIA" or "POLICE"
        "province":         "Punjab",
        "form_no":          "15",              # Standard Police FIR form
        "serial_no":        "0001/2025",

        # ── FIR Identity ───────────────────────────────────────────────
        "police_station":   "[Name of Police Station]",
        "circle":           "[District / Sub-Circle]",
        "fir_no":           "FIR____/2025",
        "occurrence_date":  "[DD-MM-YYYY]",
        "occurrence_time":  "[HH:MM]",

        # ── Report Details ─────────────────────────────────────────────
        "report_date":      current_date,
        "report_time":      current_time,

        # ── Informant / Complainant ────────────────────────────────────
        "informant_name":       "[Full Name of Complainant]",
        "informant_father":     "S/o or D/o or W/o [Father's / Husband's Name]",
        "informant_cnic":       "[XXXXX-XXXXXXX-X]",
        "informant_address":    "[House No., Street, Mohalla, City, District]",
        "informant_phone":      "[0300-XXXXXXX]",
        "informant_occupation": "[Occupation of Complainant]",

        # ── Offence ────────────────────────────────────────────────────
        "offence_sections":     "[e.g. U/S 302, 109, 34 PPC]",
        "offence_act":          "Pakistan Penal Code, 1860 (PPC)",
        "additional_acts":      "[e.g. R/w 7(1) ATA 1997 / 5(2) 47 PCA / etc.]",

        # ── Place of Occurrence ────────────────────────────────────────
        "place_of_occurrence":  "[Complete address / location of offence]",
        "distance_direction":   "[X] km [North/South/East/West] of Police Station",
        "mauza":                "[Mauza / Village / Locality Name]",
        "tehsil":               "[Tehsil]",
        "district":             "[District]",

        # ── Accused ────────────────────────────────────────────────────
        "accused_name":         "[Name of Accused / Unknown Person]",
        "accused_father":       "S/o [Father's Name]",
        "accused_cnic":         "[XXXXX-XXXXXXX-X or Unknown]",
        "accused_address":      "[Address of Accused / Unknown]",
        "accused_description":  "[Physical description if unknown accused]",

        # ── Property ───────────────────────────────────────────────────
        "property_details":     "[Description of stolen / recovered property, if any]",
        "property_value":       "PKR [Amount in figures and words]",

        # ── Investigation ──────────────────────────────────────────────
        "investigation_officer":    "[Name of Investigating Officer]",
        "io_rank":                  "[Inspector / Sub-Inspector / ASI]",
        "io_badge_no":              "[Badge/PO Number]",
        "delay_reason":             "No delay. FIR registered forthwith upon receipt of information.",
        "murasila_no":              "[Murasila / Complaint Ref. No.]",

        # ── Dispatch ───────────────────────────────────────────────────
        "dispatch_date":    current_date,
        "dispatch_time":    current_time,

        # ── SHO / Recording Officer ────────────────────────────────────
        "sho_name":         "[Name of Station House Officer]",
        "sho_designation":  "SHO / Inspector / Sub-Inspector",
        "sho_badge_no":     "[Badge Number]",

        # ── Witnesses ──────────────────────────────────────────────────
        "witnesses": [
            {
                "name":    "[Witness 1 Full Name]",
                "father":  "S/o [Father's Name]",
                "address": "[Witness 1 Address]",
                "cnic":    "[CNIC]",
            },
            {
                "name":    "[Witness 2 Full Name]",
                "father":  "S/o [Father's Name]",
                "address": "[Witness 2 Address]",
                "cnic":    "[CNIC]",
            },
        ],

        # ── Signature / Thumb ──────────────────────────────────────────
        "complainant_signature": "Signature / Left Thumb Impression of Complainant",

        # ── Narrative (main body of FIR) ───────────────────────────────
        "fir_narrative": (
            "That on the above mentioned date and time, the complainant/informant was "
            "present at [location]. At approximately [time], the accused, namely "
            "[Accused Name], [armed with / in a vehicle bearing registration No.], "
            "did [describe the offence in detail: e.g., commit robbery / cause grievous "
            "hurt / murder / kidnapping / fraud etc.]. The complainant further states "
            "that [additional details of events as they unfolded — eyewitness account, "
            "direction of escape, identifiable features of accused, nature of injury or "
            "loss, names of witnesses present, etc.]. The complainant has accordingly "
            "appeared before the undersigned officer and tendered this information for "
            "registration of the First Information Report and commencement of "
            "investigation under the law."
        ),
    }

    # Apply any caller-supplied overrides
    default_data.update(overrides)
    return default_data


# ── Quick self-test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    data = get_fir_data(
        police_station="FIA/ACC Lahore",
        circle="Lahore",
        fir_no="FIR62/2025",
        document_type="FIA",
        offence_sections="U/S 34, 109, 342, 365-A PPC",
        additional_acts="R/w 5(2) 47 PCA",
    )
    print(json.dumps(data, indent=2))