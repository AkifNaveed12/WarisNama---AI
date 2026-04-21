#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WarisNama AI - Knowledge Base (Deterministic Core)
All rules sourced from:
- Muslim Family Laws Ordinance 1961 (MFLO) - pakistancode.gov.pk
- Succession Act 1925 (for Christians/Hindus) - pakistancode.gov.pk
- Hanafi Faraid rules: Mulla's Mohammedan Law (1905, public domain)
- Shia Jafari rules: Zafar & Associates practice guide
- FBR Finance Act 2025 tables: fbr.gov.pk/overseas-faqs
- PPC Sections: pakistancode.gov.pk
- NADRA process: nadra.gov.pk
"""

from fractions import Fraction
from typing import Dict, List, Optional, Any

# ============================================================================
# SECTION 1: SUNNI HANAFI FARAID RULES
# ============================================================================

HANAFI_FIXED_SHARES = {
    'wife_with_children': Fraction(1, 8),
    'wife_no_children': Fraction(1, 4),
    'husband_with_children': Fraction(1, 4),
    'husband_no_children': Fraction(1, 2),
    'mother_with_children': Fraction(1, 6),
    'mother_no_children_no_siblings': Fraction(1, 3),
    'mother_no_children_with_siblings': Fraction(1, 6),
    'father_minimum': Fraction(1, 6),
    'daughter_sole': Fraction(1, 2),
    'daughters_multiple': Fraction(2, 3),
}

HANAFI_ASABA_PRIORITY = [
    'son', 'grandson (son\'s son)', 'father', 'grandfather (paternal)',
    'brother (full)', 'brother (consanguine)', 'son of full brother',
    'paternal uncle', 'cousin'
]

MFLO_PREDECEASED_SON_RULE = True

# ============================================================================
# SECTION 2: SHIA JAFARI RULES
# ============================================================================

SHIA_RULES = {
    'wife_inherits_land': False,
    'wife_only_movable': True,
    'radd_applies': True,
    'daughter_sole_radd': True,
    'husband_with_children': Fraction(1, 4),
    'husband_no_children': Fraction(1, 2),
    'wife_with_children': Fraction(1, 8),
    'wife_no_children': Fraction(1, 4),
    'mother': Fraction(1, 6),
    'father': Fraction(1, 6),
    'daughter_sole': Fraction(1, 2),
    'daughters_multiple': Fraction(2, 3),
    'distant_kindred_inherit': True,
}

# ============================================================================
# SECTION 3: CHRISTIAN INHERITANCE RULES (Succession Act 1925)
# ============================================================================

CHRISTIAN_RULES = {
    'spouse_with_children': {'spouse': Fraction(1, 3), 'children': Fraction(2, 3)},
    'spouse_only': {'spouse': Fraction(1, 1)},
    'children_only': {'children': Fraction(1, 1)},
    'no_spouse_no_children': {
        'parents': 'equal', 'siblings': 'equal', 'half_blood': 'half_share_of_full_blood'
    },
    'gender_equal': True,
}

# ============================================================================
# SECTION 4: HINDU INHERITANCE RULES (Hindu Succession Act 1956)
# ============================================================================

HINDU_RULES = {
    'class_I_heirs': ['widow', 'son', 'daughter', 'widow_of_predeceased_son',
                      'son_of_predeceased_son', 'daughter_of_predeceased_son'],
    'class_II_order': ['father', 'siblings', 'grandparents', 'uncles'],
    'coparcenary_special': True,
    'mvp_note': "For joint family property, consult a lawyer. MVP provides basic Class I distribution only."
}

# ============================================================================
# SECTION 5: FBR TAX TABLES (Finance Act 2025)
# ============================================================================

TAX_236K = {
    'up_to_50M': {'filer': 0.03, 'late_filer': 0.06, 'non_filer': 0.10},
    '50M_to_100M': {'filer': 0.035, 'late_filer': 0.07, 'non_filer': 0.10},
    'over_100M': {'filer': 0.04, 'late_filer': 0.08, 'non_filer': 0.10}
}

TAX_236C = {
    'up_to_50M': {'filer': 0.03, 'late_filer': 0.06, 'non_filer': 0.13},
    '50M_to_100M': {'filer': 0.035, 'late_filer': 0.07, 'non_filer': 0.16},
    'over_100M': {'filer': 0.04, 'late_filer': 0.08, 'non_filer': 0.20}
}

CGT_RULES = {
    'before_30_june_2024': {
        'year1': 0.15, 'year2': 0.125, 'year3': 0.10,
        'year4': 0.075, 'year5': 0.05, 'year6_plus': 0.00
    },
    'after_1_july_2024': {
        'filer_flat': 0.15,
        'non_filer_sliding': {'up_to_25M': 0.15, '25M_to_50M': 0.20, 'over_50M': 0.45}
    },
    'inherited_property_basis': 'FMV_at_inheritance',
    'cgt_only_on_post_inheritance_gain': True
}

CVT_RATE = 0.02
STAMP_DUTY = {'Punjab': 0.01, 'Sindh': 0.02, 'KPK': 0.015, 'Balochistan': 0.01, 'default': 0.01}
REGISTRATION_FEE = 0.005
SECTION_7E_RATE = 0.01
FEDERAL_EXCISE_DUTY = 0.05
INHERITANCE_TAX = 0.00

# ============================================================================
# SECTION 6: DISPUTE & FRAUD PATTERNS (7 patterns)
# ============================================================================

DISPUTE_PATTERNS = {
    'fraudulent_mutation': {
        'triggers': ['mutation_by_single_heir', 'no_succession_certificate'],
        'fraud_score': 87,
        'law': 'PPC Section 498A + Succession Act 1925',
        'penalty': '5-10 years imprisonment and fine',
        'actions': ['file_complaint_at_arazi_record_centre', 'file_fir_under_ppc_498a', 'send_legal_notice_to_patwari'],
        'court': 'Civil Court (Declaratory Suit)',
        'remedy': 'Mutation can be declared void; property restored to all heirs.'
    },
    'forced_partial_sale': {
        'triggers': ['one_heir_wants_to_sell', 'other_heirs_refuse', 'sale_already_done_without_consent'],
        'fraud_score': 70,
        'law': 'Transfer of Property Act 1882, Section 44',
        'penalty': 'Sale is voidable at the option of other co-owners',
        'actions': ['send_legal_notice_to_buyer_and_seller', 'file_civil_suit_for_declaration_of_void_sale'],
        'court': 'Civil Court',
        'remedy': 'Court can declare sale void; property remains jointly owned.'
    },
    'invalid_hiba': {
        'triggers': ['gift_deed_mentioned', 'donor_still_in_possession', 'no_delivery_of_possession'],
        'fraud_score': 65,
        'law': 'Muslim Personal Law (Shariat) Application Act 1962',
        'penalty': 'Hiba is invalid if possession not transferred',
        'actions': ['challenge_hiba_in_civil_court', 'send_legal_notice_to_donee'],
        'court': 'Civil Court',
        'remedy': 'Court can declare Hiba invalid; property returns to estate.'
    },
    'excessive_wasiyyat': {
        'triggers': ['will_mentioned', 'will_percentage_greater_than_33.33'],
        'fraud_score': 60,
        'law': 'Islamic law – Wasiyyat valid only up to 1/3 of estate after debts',
        'penalty': 'Excess portion is void; distributed among legal heirs via Faraid',
        'actions': ['explain_1/3_rule', 'recalculate_valid_shares', 'generate_legal_notice_to_executor'],
        'court': 'Civil Court',
        'remedy': 'Will is partially enforceable; remaining 2/3 distributed by Faraid.'
    },
    'debt_priority_violation': {
        'triggers': ['debts_mentioned', 'estate_distributed_before_debt_payment'],
        'fraud_score': 90,
        'law': 'Islamic law and Succession Act – debts and funeral expenses take priority',
        'penalty': 'Heirs may be personally liable for unpaid debts',
        'actions': ['stop_distribution', 'pay_all_debts_first', 'then_distribute_remainder'],
        'court': 'Civil Court (creditors can sue heirs)',
        'remedy': 'Correct order: Funeral → Debts → Wasiyyat (max 1/3) → Faraid.'
    },
    'minor_heir': {
        'triggers': ['heir_age_under_18', 'no_legal_guardian_appointed'],
        'fraud_score': 50,
        'law': 'Guardians and Wards Act 1890, Succession Act 1925',
        'penalty': 'NADRA will not issue succession certificate without court-appointed guardian',
        'actions': ['apply_to_district_court_for_guardian_appointment', 'file_guardian_application_with_heir_list'],
        'court': 'District Court (Guardian Judge)',
        'remedy': 'Guardian appointed; then normal succession process.'
    },
    'buyout_negotiation': {
        'triggers': ['one_heir_wants_to_keep', 'others_want_cash', 'mutual_agreement_possible'],
        'fraud_score': 0,
        'law': 'Transfer of Property Act – internal transfer allowed with all heirs\' NOC',
        'penalty': 'None if done legally',
        'actions': ['calculate_buyout_amount_per_heir', 'generate_buyout_agreement', 'calculate_stamp_duty_and_236K'],
        'court': 'None needed if all agree; otherwise Civil Court',
        'remedy': 'Buying heir pays others their share; property transferred via registered deed.'
    }
}

# ============================================================================
# SECTION 7: LEGAL REFERENCES
# ============================================================================

REFERENCES = {
    'hanafi_wife_with_children': "📖 Mulla's Mohammedan Law, Section 272: Wife gets 1/8 if children exist.",
    'hanafi_wife_no_children': "📖 Mulla's Mohammedan Law, Section 273: Wife gets 1/4 if no children.",
    'hanafi_husband_with_children': "📖 Mulla's Mohammedan Law, Section 274: Husband gets 1/4 if children exist.",
    'hanafi_husband_no_children': "📖 Mulla's Mohammedan Law, Section 275: Husband gets 1/2 if no children.",
    'hanafi_mother_with_children': "📖 Mulla's Mohammedan Law, Section 276: Mother gets 1/6 if children or 2+ siblings exist.",
    'hanafi_mother_no_children_no_siblings': "📖 Mulla's Mohammedan Law, Section 277: Mother gets 1/3 if no children and no siblings.",
    'hanafi_father_minimum': "📖 Mulla's Mohammedan Law, Section 278: Father gets minimum 1/6 then residue (Asaba).",
    'hanafi_daughter_sole': "📖 Mulla's Mohammedan Law, Section 279: Single daughter gets 1/2 if no son.",
    'hanafi_daughters_multiple': "📖 Mulla's Mohammedan Law, Section 280: Two or more daughters get 2/3 collectively if no son.",
    'hanafi_asaba_children': "📖 Hanafi Asaba rule: Sons get double daughter's share of residue.",
    'hanafi_mflo_predeceased_son': "📜 MFLO 1961, Section 4: Predeceased son's children inherit his share.",
    'shia_wife_no_land': "📖 Shia Jafari law: Wife does NOT inherit immovable property.",
    'christian_spouse_children': "📖 Succession Act 1925, Section 33(c): Spouse 1/3, Children 2/3 equally.",
    'christian_spouse_only': "📖 Succession Act 1925, Section 33(b): Spouse gets entire estate.",
    'christian_children_only': "📖 Succession Act 1925, Section 33(a): Children split estate equally.",
    'hindu_class_I': "📖 Hindu Succession Act 1956: Class I heirs inherit equally.",
    'debt_priority': "📜 Order: Funeral → Debts → Wasiyyat (max 1/3) → Faraid.",
    'wasiyyat_limit': "📜 Will cannot exceed 1/3 of estate after debts. Excess is void.",
}

# ============================================================================
# SECTION 8: NADRA & COURT PROCESS STEPS
# ============================================================================

NADRA_SUCCESSION_PROCESS = {
    'step1': {
        'name': 'Obtain Death Certificate',
        'authority': 'NADRA / Union Council',
        'fee': 'Rs 50',
        'documents': ['CNIC of applicant', 'Medical certificate or witness statements'],
        'time': 'Same day to 3 days'
    },
    'step2': {
        'name': 'Apply for Succession Certificate',
        'authority': 'NADRA Succession Cell OR Civil Court',
        'fee': 'Rs 2,000 – 5,000',
        'documents': ['Death certificate', 'CNICs of all heirs', 'Property details', 'Family registration certificate'],
        'time': '15 days (NADRA) to 90 days (Court)',
        'note': 'If any heir is minor (<18), court must appoint guardian first.'
    },
    'step3': {
        'name': 'Mutation of Property at Arazi Record Centre',
        'authority': 'Arazi Record Centre (Patwari / Tehsildar)',
        'fee': 'Rs 500 – 2,000',
        'documents': ['Succession certificate', 'Death certificate', 'Original property deed', 'CNICs of all heirs'],
        'time': '30 days after application',
        'note': 'All heirs must sign or provide NOC. Single-heir mutation without consent is fraudulent.'
    },
    'step4': {
        'name': 'Registration of Transfer (if selling)',
        'authority': 'Sub-Registrar (Stamp Office)',
        'fee': 'Stamp duty (1-3%) + Registration fee (0.5-1%)',
        'documents': ['Sale deed', 'Succession certificate', 'CNICs', 'Tax clearance (FBR)'],
        'time': '7-14 days'
    }
}

# ============================================================================
# SECTION 9: LEGAL DOCUMENT TEMPLATES
# ============================================================================

LEGAL_NOTICE_TEMPLATE_URDU = """
بسم اللہ الرحمن الرحیم
{date}

از: {sender_name}, وارث مرحوم {deceased_name}
بہ: {recipient_name}, {recipient_address}

موضوع: قانونی نوٹس برائے {fraud_description}

محترم,
آپ کا عمل {law_section} کے تحت غیر قانونی ہے۔ آپ کو ہدایت کی جاتی ہے کہ 15 دنوں کے اندر {remedy} کریں۔ بصورت دیگر قانونی کارروائی کی جائے گی۔

دستخط: ______________
"""

LEGAL_NOTICE_TEMPLATE_EN = """
LEGAL NOTICE
Without Prejudice

Date: {date}
From: {sender_name}, legal heir of late {deceased_name}
To: {recipient_name}, {recipient_address}
Subject: Legal notice regarding {fraud_description}

Sir/Madam,
Your action of {fraud_description} is illegal under {law_section}. You are hereby directed to {remedy} within 15 days of receiving this notice. Failure to comply will result in legal proceedings.

Sincerely,
{sender_name}
"""

FIR_DRAFT_TEMPLATE_URDU = """
درخواست برائے ایف آئی آر
تھانہ: {police_station_name}
مقدمہ نمبر: (طے ہوگا)

مدعی: {complainant_name}, وارث مرحوم {deceased_name}
مدعا علیہ: {accused_name}

الزام: {fraud_description} جو کہ {law_section} کے تحت جرم ہے۔

تفصیل: مدعا علیہ نے {accused_action} کرکے وارثین کو ان کے قانونی حصے سے محروم کیا۔ ثبوت موجود ہیں: {evidence_list}.

درخواست ہے کہ ایف آئی آر درج کرکے قانونی کارروائی کی جائے۔
"""

INHERITANCE_CERTIFICATE_TEMPLATE = """
WARISNAMA AI – INHERITANCE SHARE CERTIFICATE
Certificate No: {certificate_no}
Date: {date}

This is to certify that the estate of late {deceased_name} is distributed among the following legal heirs under {sect} law:

Estate Value: PKR {total_estate:,.0f}
Deductible Debts: PKR {debts:,.0f}
Wasiyyat (max 1/3): PKR {wasiyyat:,.0f}
Distributable Estate: PKR {distributable:,.0f}

Heir Shares:
{share_table}

Tax liability (if selling): See attached FBR 2025 calculation.

Disclaimer: This is an AI-generated estimate. Consult a lawyer for final legal action.
"""

# ============================================================================
# SECTION 10: HELPER FUNCTIONS
# ============================================================================

def get_tax_bracket(value: float) -> str:
    """Return tax bracket key based on property value."""
    if value <= 50_000_000:
        return 'up_to_50M'
    elif value <= 100_000_000:
        return '50M_to_100M'
    else:
        return 'over_100M'

def get_stamp_duty(province: str = 'default') -> float:
    """Return stamp duty rate for given province."""
    return STAMP_DUTY.get(province, STAMP_DUTY['default'])