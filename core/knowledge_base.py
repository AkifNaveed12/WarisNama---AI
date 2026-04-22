#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WarisNama AI — knowledge_base.py
=================================
THE DETERMINISTIC BRAIN of WarisNama AI.

All rules, tables, templates, and helper functions live here.
This single file is imported by every other module. No JSON files required —
Python constants load faster, are type-safe, and support Fraction objects natively.

Legal Sources:
  - Muslim Family Laws Ordinance 1961 (MFLO §4) — pakistancode.gov.pk
  - Succession Act 1925 (Christian/Hindu) — pakistancode.gov.pk
  - Pakistan Penal Code (PPC §498A) — pakistancode.gov.pk
  - Guardians and Wards Act 1890 — pakistancode.gov.pk
  - Transfer of Property Act 1882 — pakistancode.gov.pk
  - Hanafi Faraid: Mulla's Mohammedan Law (1905, public domain) + the-legal.org
  - Shia Jafari: Zafar & Associates LLP practice guide + alsyedlaw.com
  - FBR Finance Act 2025: fbr.gov.pk/overseas-faqs + taxationpk.com
  - NADRA process: nadra.gov.pk
  - Arazi mutation: punjab.gov.pk / arazi.punjab.gov.pk

Author: WarisNama AI Team
Version: 1.0.0 — Production Ready
"""

from __future__ import annotations

import re
import uuid
import datetime
from fractions import Fraction
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS — type-safe identifiers used across all modules
# ═══════════════════════════════════════════════════════════════════════════════

class Sect(str, Enum):
    HANAFI   = "hanafi"       # Sunni Hanafi (~75% of Pakistan)
    SHIA     = "shia_jafari"  # Shia Jafari/Ithna Ashari (~20%)
    CHRISTIAN = "christian"   # Succession Act 1925
    HINDU    = "hindu"        # Hindu Succession Act 1956


class FilerStatus(str, Enum):
    FILER      = "filer"
    LATE_FILER = "late_filer"
    NON_FILER  = "non_filer"


class HeirType(str, Enum):
    HUSBAND             = "husband"
    WIFE                = "wife"
    SON                 = "son"
    DAUGHTER            = "daughter"
    FATHER              = "father"
    MOTHER              = "mother"
    GRANDSON            = "grandson"            # son's son
    GRANDDAUGHTER       = "granddaughter"       # son's daughter
    PATERNAL_GRANDFATHER = "paternal_grandfather"
    PATERNAL_GRANDMOTHER = "paternal_grandmother"
    MATERNAL_GRANDMOTHER = "maternal_grandmother"
    FULL_BROTHER        = "full_brother"
    FULL_SISTER         = "full_sister"
    CONSANGUINE_BROTHER = "consanguine_brother" # same father, different mother
    CONSANGUINE_SISTER  = "consanguine_sister"
    UTERINE_BROTHER     = "uterine_brother"     # same mother, different father
    UTERINE_SISTER      = "uterine_sister"
    SON_OF_FULL_BROTHER = "son_of_full_brother"
    PATERNAL_UNCLE      = "paternal_uncle"
    SON_OF_PATERNAL_UNCLE = "son_of_paternal_uncle"


class AssetType(str, Enum):
    HOUSE            = "house"
    PLOT             = "plot"
    SHOP             = "shop"
    AGRICULTURAL     = "agricultural_land"
    APARTMENT        = "apartment"
    COMMERCIAL       = "commercial_property"
    CAR              = "car"
    CASH             = "cash"
    BANK_ACCOUNT     = "bank_account"
    BUSINESS         = "business"
    JEWELRY          = "jewelry"
    STOCKS           = "stocks"


class Province(str, Enum):
    PUNJAB      = "Punjab"
    SINDH       = "Sindh"
    KPK         = "KPK"
    BALOCHISTAN = "Balochistan"
    DEFAULT     = "default"


class DisputePattern(str, Enum):
    FRAUDULENT_MUTATION    = "fraudulent_mutation"
    FORCED_PARTIAL_SALE    = "forced_partial_sale"
    INVALID_HIBA           = "invalid_hiba"
    EXCESSIVE_WASIYYAT     = "excessive_wasiyyat"
    DEBT_PRIORITY          = "debt_priority_violation"
    MINOR_HEIR             = "minor_heir"
    BUYOUT_NEGOTIATION     = "buyout_negotiation"
    DAUGHTER_SHARE_DENIED  = "daughters_share_denied"


class DocumentType(str, Enum):
    SHARE_CERTIFICATE = "share_certificate"
    LEGAL_NOTICE      = "legal_notice"
    FIR_DRAFT         = "fir_draft"
    BUYOUT_AGREEMENT  = "buyout_agreement"
    ARAZI_COMPLAINT   = "arazi_complaint"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SUNNI HANAFI FARAID RULES
# Source: Mulla's Mohammedan Law, Ch. V (public domain) + MFLO 1961 §4
# ═══════════════════════════════════════════════════════════════════════════════

# ── Fixed Shares (Quranic / Fard heirs) ──────────────────────────────────────
HANAFI_FIXED_SHARES: Dict[str, Fraction] = {

    # WIFE / WIVES
    # Rule: 1/8 if deceased has ANY children or grandchildren (through son).
    #       1/4 if no children at all.
    #       Multiple wives SHARE this fraction equally among themselves.
    "wife_with_children":    Fraction(1, 8),
    "wife_no_children":      Fraction(1, 4),

    # HUSBAND
    # Rule: 1/4 if wife (deceased) has children or grandchildren through son.
    #       1/2 if no children at all.
    "husband_with_children": Fraction(1, 4),
    "husband_no_children":   Fraction(1, 2),

    # MOTHER
    # Rule: 1/6 if deceased has children OR grandchildren (through son).
    #       1/6 if deceased has 2 or more FULL or consanguine siblings (even if childless).
    #       1/3 if deceased has NO children AND FEWER than 2 siblings.
    # ENGINE NOTE: check (has_children OR has_grandchildren_through_son OR sibling_count >= 2)
    "mother_with_children":              Fraction(1, 6),
    "mother_no_children_with_2_siblings": Fraction(1, 6),  # reduced by 2+ siblings
    "mother_no_children_no_siblings":    Fraction(1, 3),   # full 1/3

    # FATHER
    # ENGINE NOTE — CRITICAL THREE-CASE LOGIC (implement exactly):
    #
    # CASE A — Deceased has son(s) alive:
    #     Father gets ONLY his fixed 1/6. No Asaba.
    #     Code: father_share = Fraction(1,6)
    #
    # CASE B — Deceased has daughter(s) but NO son:
    #     Father gets 1/6 fixed PLUS whatever residue remains after all Quranic shares.
    #     This combined share may be large if daughters are the only other heirs.
    #     Code: father_share = Fraction(1,6) + residue_after_daughters
    #
    # CASE C — Deceased has NO children at all (no son, no daughter):
    #     Father takes the ENTIRE residue as Asaba (no fixed minimum in this case,
    #     he just takes what is left; but he is never less than 0).
    #     If father is the ONLY heir, he takes the entire estate.
    #     Code: father_share = entire_residue (could be the full estate)
    #
    "father_fixed_minimum": Fraction(1, 6),   # applies in Case A and Case B only

    # DAUGHTER(S)
    # Rule: 1/2 if single daughter and NO son present.
    #       2/3 shared equally among 2+ daughters when NO son present.
    #       When SON is present: daughters do NOT get fixed share —
    #       they join the Asaba pool with sons at ratio 2:1 (son:daughter).
    "daughter_sole":     Fraction(1, 2),
    "daughters_multiple": Fraction(2, 3),

    # PATERNAL GRANDFATHER (when father is dead)
    # Rule: Substitutes father in father's absence. Same three-case logic as father.
    # ENGINE NOTE: Only inherits if father is deceased. Does NOT inherit if father is alive.
    "grandfather_fixed_minimum": Fraction(1, 6),

    # PATERNAL GRANDMOTHER (when mother is dead and father is dead)
    # Rule: 1/6 only. Does NOT increase. Maternal grandmother also gets 1/6.
    # Both grandmothers share 1/6 equally if both alive.
    "grandmother_share": Fraction(1, 6),

    # UTERINE SIBLINGS (same mother, different fathers)
    # Rule: 1/6 each if single uterine sibling. 1/3 shared if 2 or more.
    #       Males and females take EQUAL shares (unlike full/consanguine siblings).
    #       Completely excluded (Mahjub) if deceased has: children, grandchildren through son, or father.
    "uterine_sibling_single":   Fraction(1, 6),
    "uterine_siblings_multiple": Fraction(1, 3),
}


# ── Asaba (Residue / agnatic) Priority Order ──────────────────────────────────
# ENGINE NOTE: Asaba heir takes what remains after all Quranic fixed shares.
# Only the FIRST available heir in this list (who is not excluded) gets Asaba.
# If two heirs of the same rank exist, they share equally.
# A son and daughter together form Asaba — son gets 2 shares, daughter gets 1.
HANAFI_ASABA_PRIORITY: List[str] = [
    "son",
    "grandson (son's son, then son's son's son)",     # as deep as needed
    "father",                                          # Case C only (see above)
    "paternal_grandfather",                            # substitutes father if father dead
    "full_brother",                                    # excluded by son, grandson, father, grandfather
    "consanguine_brother",                             # excluded by full brother
    "son_of_full_brother",
    "son_of_consanguine_brother",
    "paternal_uncle (full)",
    "paternal_uncle (consanguine)",
    "son_of_paternal_uncle (full)",
    "son_of_paternal_uncle (consanguine)",
]


# ── Mahjub (Exclusion / Blocking) Rules ──────────────────────────────────────
# Maps an heir type to the set of heirs that COMPLETELY block them from inheriting.
# ENGINE NOTE: Before calculating any heir's share, check if they are blocked.
HANAFI_MAHJUB: Dict[str, List[str]] = {
    "paternal_grandfather":   ["father"],
    "paternal_grandmother":   ["mother", "father", "paternal_grandfather"],
    "maternal_grandmother":   ["mother"],
    "full_sister":            ["son", "grandson", "father", "paternal_grandfather"],
    "consanguine_sister":     ["son", "grandson", "father", "paternal_grandfather", "full_brother"],
    "uterine_brother":        ["son", "grandson", "father", "paternal_grandfather", "mother"],
    "uterine_sister":         ["son", "grandson", "father", "paternal_grandfather", "mother"],
    "consanguine_brother":    ["son", "grandson", "father", "paternal_grandfather", "full_brother"],
    "son_of_full_brother":    ["son", "grandson", "father", "paternal_grandfather",
                                "full_brother", "consanguine_brother"],
    "paternal_uncle":         ["son", "grandson", "father", "paternal_grandfather",
                                "full_brother", "consanguine_brother",
                                "son_of_full_brother", "son_of_consanguine_brother"],
    "son_of_paternal_uncle":  ["son", "grandson", "father", "paternal_grandfather",
                                "full_brother", "consanguine_brother",
                                "son_of_full_brother", "son_of_consanguine_brother",
                                "paternal_uncle"],
}


# ── MFLO 1961 §4 — Predeceased Son Rule ──────────────────────────────────────
# CRITICAL: Always apply in Pakistan. Overrides classical Hanafi.
# If a son died before the father, that son's children (grandchildren of deceased)
# inherit THEIR FATHER'S share — not zero, not less.
# Example: Father has Son A (alive) and Son B (dead, has 2 children).
#          Classical Hanafi: Son B's children get NOTHING (blocked by Son A).
#          MFLO 1961 §4: Son B's children split Son B's share equally.
# This is the single most commonly exploited rule in Pakistani inheritance fraud.
MFLO_PREDECEASED_SON_APPLIES: bool = True
MFLO_PREDECEASED_DAUGHTER_APPLIES: bool = False  # MFLO §4 only covers predeceased SON'S children


# ── Awl (Proportional Reduction) Rule ────────────────────────────────────────
# If the sum of all Quranic fixed shares EXCEEDS the estate (i.e., fractions add to > 1),
# all shares are reduced proportionally. This is called Awl.
# ENGINE NOTE: Calculate sum of all fixed fractions. If > 1, multiply each by (1 / total_sum).
# Example: Husband (1/2) + 2 daughters (2/3) + mother (1/6) = 1/2+2/3+1/6 = 4/3 > 1
#          Apply Awl: each share multiplied by 3/4.
AWL_APPLIES: bool = True  # always handle this case


# ── Radd (Return / Surplus) Rule — Hanafi ────────────────────────────────────
# In Hanafi: Surplus (after Quranic shares < 1) goes to Asaba agnates.
# If no Asaba exists, surplus goes back to Quranic heirs proportionally
# EXCEPT the husband/wife (spouse never benefits from Radd in Hanafi).
HANAFI_RADD_EXCLUDES_SPOUSE: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — SHIA JAFARI RULES
# Source: Zafar & Associates LLP (zallp.com/practice/inheritance_law/)
#         Al-Syed Law (alsyedlaw.com)
# ═══════════════════════════════════════════════════════════════════════════════

SHIA_RULES: Dict[str, Any] = {

    # ── Wife / Wives ──────────────────────────────────────────────────────────
    # CRITICAL SHIA RULE: Wife does NOT inherit immovable property (land, houses,
    # buildings, agricultural land). She receives the MONETARY EQUIVALENT of her
    # share from other liquid assets or is bought out by other heirs.
    # Many Shia widows are wrongly told they own part of the house — they do not.
    "wife_inherits_immovable":  False,
    "wife_only_movable_assets": True,
    "wife_with_children":       Fraction(1, 8),
    "wife_no_children":         Fraction(1, 4),

    # ── Husband ───────────────────────────────────────────────────────────────
    "husband_with_children":    Fraction(1, 4),
    "husband_no_children":      Fraction(1, 2),

    # ── Mother ────────────────────────────────────────────────────────────────
    # DIFFERENCE FROM HANAFI: In Shia, mother's share is ALWAYS 1/6 when children exist.
    # No 1/3 case when siblings are present (different reduction mechanism).
    "mother_with_children":     Fraction(1, 6),
    "mother_no_children":       Fraction(1, 3),   # same as Hanafi in this case

    # ── Father ────────────────────────────────────────────────────────────────
    # Shia father: same 1/6 minimum, but Asaba residue calculation differs.
    "father_fixed_minimum":     Fraction(1, 6),

    # ── Daughters ─────────────────────────────────────────────────────────────
    "daughter_sole":            Fraction(1, 2),
    "daughters_multiple":       Fraction(2, 3),

    # ── Radd (Surplus Return) — SHIA DIFFERENCE ───────────────────────────────
    # CRITICAL SHIA RULE: When fixed shares < 1 and no Asaba exists,
    # surplus is returned to ALL fixed-share heirs including daughters.
    # Unlike Hanafi, even the spouse may benefit from Radd in some Shia interpretations.
    # Practical impact: A sole daughter gets 1/2 fixed + 1/2 returned = FULL estate.
    # This is dramatically different from Hanafi where the surplus goes to agnates.
    "radd_applies":             True,
    "radd_includes_spouse":     True,   # unlike Hanafi

    # ── Full Sister inherits WITH Father (Shia-only rule) ─────────────────────
    # DIFFERENCE FROM HANAFI: In Shia law, a full sister is NOT blocked by the father.
    # She can inherit ALONGSIDE the father, which does not happen in Hanafi.
    # This matters significantly in contested cases where sisters claim inheritance.
    "full_sister_blocked_by_father": False,   # Shia: sister NOT blocked by father
    # Hanafi value would be True

    # ── Distant Kindred ───────────────────────────────────────────────────────
    # In Shia, distant kindred (Dhawul Arham) can inherit even when closer heirs
    # of a different category are present. Priority system differs from Hanafi.
    "distant_kindred_can_inherit": True,

    # ── Only 9 Sharers Recognised ─────────────────────────────────────────────
    # Shia law recognises only 9 fixed-share heirs (vs 12 in Hanafi).
    # The rest are either residuaries or blocked.
    "recognised_sharers": [
        "husband", "wife", "father", "mother",
        "daughter", "granddaughter (if daughter absent)",
        "full_sister (if daughter absent and no son)",
        "uterine_sibling",
        "paternal_grandmother / maternal_grandmother"
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CHRISTIAN INHERITANCE RULES (Succession Act 1925)
# Source: Succession Act 1925, Part V (Intestate Succession) — pakistancode.gov.pk
# Key principle: NO gender discrimination. Daughters and sons inherit equally.
# ═══════════════════════════════════════════════════════════════════════════════

CHRISTIAN_RULES: Dict[str, Any] = {

    # Scenario A: Spouse + Children
    # Spouse takes 1/3. Children share 2/3 EQUALLY — no gender difference.
    "spouse_and_children": {
        "spouse_share":   Fraction(1, 3),
        "children_share": Fraction(2, 3),
        "children_split": "equal",   # sons and daughters get identical shares
    },

    # Scenario B: Spouse only (no children, no parents, no siblings)
    "spouse_only": {
        "spouse_share": Fraction(1, 1),
    },

    # Scenario C: Children only (no spouse)
    "children_only": {
        "children_share": Fraction(1, 1),
        "children_split": "equal",
    },

    # Scenario D: No spouse, no children
    # Priority: Parents (equally) → Siblings → Half-blood siblings → Remote relatives
    "no_spouse_no_children": {
        "priority_order": ["parents", "siblings", "half_blood_siblings",
                           "grandparents", "uncles_aunts", "cousins"],
        "parents_split":   "equal",   # father and mother share equally
        "siblings_split":  "equal",   # all brothers and sisters share equally
        "half_blood_rule": "half_share_of_full_blood",  # half-sibling gets half of full sibling
    },

    # Key distinctions from Islamic law
    "gender_equal":             True,   # No male:female ratio difference
    "spouse_guaranteed_share":  True,   # Spouse always gets at least 1/3 if children exist
    "no_asaba_concept":         True,   # No residue agnate concept
    "will_can_exceed_1_3":      True,   # Christians can will more than 1/3 (no Islamic limit)
    "probate_required_for_will": True,  # Will must be probated by court
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — HINDU INHERITANCE RULES (Hindu Succession Act 1956)
# Source: Hindu Succession Act 1956 — pakistancode.gov.pk
# MVP scope: Class I heirs only. Coparcenary property flagged for lawyer referral.
# ═══════════════════════════════════════════════════════════════════════════════

HINDU_RULES: Dict[str, Any] = {

    # Class I Heirs — all inherit simultaneously and equally
    "class_I_heirs": [
        "widow", "son", "daughter",
        "widow_of_predeceased_son",
        "son_of_predeceased_son",
        "daughter_of_predeceased_son",
        "widow_of_predeceased_son_of_predeceased_son",
    ],
    "class_I_split": "equal",   # all Class I heirs share equally, no gender difference

    # Class II Heirs — only if NO Class I heir exists
    "class_II_order": [
        "father",
        ["siblings", "sibling_children"],   # same rank
        "paternal_grandparents",
        ["paternal_uncle_aunt", "paternal_uncle_aunt_children"],
        ["maternal_grandparents", "maternal_uncle_aunt"],
    ],

    # Coparcenary Property (joint family / ancestral property)
    # This requires separate analysis — too complex for 24-hr MVP.
    "coparcenary_special_rules": True,
    "coparcenary_mvp_note": (
        "Joint/ancestral family property follows different coparcenary rules. "
        "WarisNama AI provides basic Class I distribution only for self-acquired property. "
        "Please consult a lawyer for ancestral/joint family property disputes."
    ),

    "gender_equal": True,       # 2005 amendment removed male coparcenary preference
    "will_allowed": True,       # Hindus can make a will for self-acquired property
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — FBR TAX TABLES (Finance Act 2025)
# Source: FBR official site fbr.gov.pk/overseas-faqs (retrieved April 2025)
#         Cross-verified: taxationpk.com, icons.com.pk, waystax.com
# ═══════════════════════════════════════════════════════════════════════════════

# ── Section 236K — Advance Tax on PURCHASE (buyer pays) ──────────────────────
TAX_236K: Dict[str, Dict[str, float]] = {
    "up_to_50M": {
        FilerStatus.FILER:       0.03,   # 3%
        FilerStatus.LATE_FILER:  0.06,   # 6%
        FilerStatus.NON_FILER:   0.10,   # 10%
    },
    "50M_to_100M": {
        FilerStatus.FILER:       0.035,  # 3.5%
        FilerStatus.LATE_FILER:  0.07,   # 7%
        FilerStatus.NON_FILER:   0.10,   # 10% (capped)
    },
    "over_100M": {
        FilerStatus.FILER:       0.04,   # 4%
        FilerStatus.LATE_FILER:  0.08,   # 8%
        FilerStatus.NON_FILER:   0.10,   # 10% (capped)
    },
}

# ── Section 236C — Advance Tax on SALE (seller pays) ─────────────────────────
TAX_236C: Dict[str, Dict[str, float]] = {
    "up_to_50M": {
        FilerStatus.FILER:       0.03,   # 3%
        FilerStatus.LATE_FILER:  0.06,   # 6%
        FilerStatus.NON_FILER:   0.13,   # 13% — significantly higher
    },
    "50M_to_100M": {
        FilerStatus.FILER:       0.035,  # 3.5%
        FilerStatus.LATE_FILER:  0.07,   # 7%
        FilerStatus.NON_FILER:   0.16,   # 16%
    },
    "over_100M": {
        FilerStatus.FILER:       0.04,   # 4%
        FilerStatus.LATE_FILER:  0.08,   # 8%
        FilerStatus.NON_FILER:   0.20,   # 20%
    },
}

# ── Capital Gains Tax (CGT) ───────────────────────────────────────────────────
# CRITICAL: Inherited property uses STEP-UP BASIS.
# CGT only applies on gains AFTER the date of inheritance, not before.
# There is ZERO CGT at the time of inheritance itself.
CGT_RULES: Dict[str, Any] = {

    # Properties acquired BEFORE June 30, 2024
    "pre_july_2024_sliding": {
        "year_1": 0.15,   # 15% if sold within 1st year of acquisition
        "year_2": 0.125,  # 12.5%
        "year_3": 0.10,
        "year_4": 0.075,
        "year_5": 0.05,
        "year_6_plus": 0.00,  # zero CGT after 6 years
    },

    # Properties acquired ON OR AFTER July 1, 2024
    "post_july_2024": {
        "filer_flat_rate": 0.15,   # flat 15% regardless of holding period
        "non_filer_by_value": {
            "up_to_25M":    0.15,  # 15%
            "25M_to_50M":   0.20,  # 20%
            "over_50M":     0.45,  # 45% — punitive for non-filers
        },
    },

    # Inherited property specifics
    "inherited_property": {
        "basis":                    "FMV_at_date_of_inheritance",
        "cgt_at_time_of_inheritance": 0.00,   # ZERO — inheritance itself is NOT taxed
        "cgt_on_post_inheritance_gain": True,  # only on gain AFTER inheritance date
        "inheritance_tax":          0.00,      # Pakistan has NO inheritance tax whatsoever
    },
}

# ── Other Property Taxes ──────────────────────────────────────────────────────
CVT_RATE: float = 0.02   # Capital Value Tax — 2% of declared property value, buyer pays once

STAMP_DUTY: Dict[str, float] = {
    Province.PUNJAB:      0.01,   # 1%
    Province.SINDH:       0.02,   # 2%
    Province.KPK:         0.015,  # 1.5%
    Province.BALOCHISTAN: 0.01,   # 1%
    Province.DEFAULT:     0.01,   # 1% default
}

REGISTRATION_FEE: float = 0.005      # 0.5% — provincial, use as default
SECTION_7E_RATE: float  = 0.01       # ~1% deemed income tax on market value (annual)
                                      # Exempt if: only one self-occupied residential property
FEDERAL_EXCISE_DUTY: float = 0.05    # 5% on FIRST allotment/transfer of residential property only
INHERITANCE_TAX: float = 0.00        # ZERO. Pakistan has absolutely no inheritance tax.
                                      # Many families wait years fearing this — it does not exist.

# Overseas Pakistanis with NICOP/POC get FILER rates on 236C and 236K
# regardless of whether they are on Active Taxpayers List (ATL).
NICOP_POC_FILER_TREATMENT: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — DISPUTE & FRAUD PATTERNS (8 patterns)
# Legal sources: PPC §498A, Succession Act 1925, Transfer of Property Act 1882,
#                Guardians and Wards Act 1890, MFLO 1961, Islamic law (Wasiyyat)
# ═══════════════════════════════════════════════════════════════════════════════

DISPUTE_PATTERNS: Dict[str, Dict[str, Any]] = {

    # ── Pattern 1: Fraudulent Mutation ───────────────────────────────────────
    # Most common fraud: one heir goes to Patwari and mutates entire property
    # into their own name without a succession certificate and without other heirs.
    DisputePattern.FRAUDULENT_MUTATION: {
        "triggers": [
            "mutation_by_single_heir",
            "no_succession_certificate_obtained",
            "other_heirs_not_informed",
            "patwari_involvement_suspected",
        ],
        "fraud_score": 87,
        "severity":    "CRITICAL",
        "law_sections": {
            "PPC §498A": "Willful dispossession or deprivation of a woman from her property inheritance rights — 5 to 10 years imprisonment and fine of Rs 1,000,000.",
            "Succession Act 1925 §370": "Transfer without succession certificate is void.",
            "MFLO 1961 §4": "All heirs including grandchildren must be recognised.",
        },
        "penalty": "5–10 years imprisonment and Rs 1,000,000 fine (PPC §498A)",
        "immediate_actions": [
            "File complaint at Arazi Record Centre for mutation reversal",
            "File FIR at local police station under PPC §498A",
            "Send legal notice to the heir who mutated",
            "Apply for stay order in Civil Court to freeze further transfers",
        ],
        "documents_to_generate": [
            DocumentType.FIR_DRAFT,
            DocumentType.LEGAL_NOTICE,
            DocumentType.ARAZI_COMPLAINT,
        ],
        "court": "Civil Court (Declaratory Suit) + Criminal Court (FIR §498A)",
        "remedy": "Mutation declared void; property restored to all heirs proportionally.",
        "urdu_title": "غیر قانونی انتقال",
        "urdu_action": "ارازی ریکارڈ سینٹر میں شکایت درج کریں اور FIR درج کریں",
    },

    # ── Pattern 2: Forced Partial Sale ───────────────────────────────────────
    # One heir sells jointly inherited property without all co-owners' consent.
    DisputePattern.FORCED_PARTIAL_SALE: {
        "triggers": [
            "one_heir_selling_without_consent",
            "sale_deed_signed_by_only_one_heir",
            "buyer_purchased_without_checking_all_heirs",
        ],
        "fraud_score": 72,
        "severity":    "HIGH",
        "law_sections": {
            "Transfer of Property Act 1882 §44": "A co-owner can only transfer their OWN share, not the whole property. Buyer gets only that heir's undivided share.",
            "Specific Relief Act 1877": "Other heirs can seek injunction to stop the sale.",
        },
        "penalty": "Sale of others' shares is void; civil liability to other heirs.",
        "immediate_actions": [
            "Send legal notice to the selling heir and the buyer",
            "File civil suit for declaration that sale is partially void",
            "Apply for interim injunction to stop registration of sale deed",
        ],
        "documents_to_generate": [
            DocumentType.LEGAL_NOTICE,
        ],
        "court": "Civil Court (Declaratory + Injunction Suit)",
        "remedy": "Court declares sale void to the extent of other heirs' shares.",
        "urdu_title": "زبردستی فروخت",
        "urdu_action": "سول کورٹ میں دعوٰی دائر کریں",
    },

    # ── Pattern 3: Invalid Hiba (Gift Deed) ──────────────────────────────────
    # Property gifted to one child before death, but possession never actually transferred.
    DisputePattern.INVALID_HIBA: {
        "triggers": [
            "gift_deed_hiba_mentioned",
            "donor_still_occupying_property",    # father still living in gifted house
            "no_physical_delivery_of_possession",
            "hiba_made_under_duress_or_illness", # deathbed Hiba is void
        ],
        "fraud_score": 65,
        "severity":    "HIGH",
        "law_sections": {
            "Muslim Personal Law (Shariat) Application Act 1962": "Hiba requires three elements: (1) Offer (Ijab), (2) Acceptance (Qabool), (3) Delivery of Possession (Qabza). Missing any element = invalid Hiba.",
            "Transfer of Property Act 1882 §123": "Gift of immovable property requires registered instrument + delivery.",
            "PLD 2016 Lahore 865": "Hiba without possession is invalid under Pakistani courts.",
        },
        "penalty": "Hiba declared invalid; property reverts to estate.",
        "immediate_actions": [
            "Verify whether father vacated the property after gift",
            "Check if Hiba deed is registered (requirement for immovable property)",
            "Challenge Hiba in Civil Court if possession was not transferred",
        ],
        "documents_to_generate": [
            DocumentType.LEGAL_NOTICE,
        ],
        "court": "Civil Court",
        "remedy": "Court declares Hiba invalid; property included in estate for Faraid distribution.",
        "urdu_title": "غیر قانونی ہبہ",
        "urdu_action": "عدالت میں ہبہ کو چیلنج کریں",
    },

    # ── Pattern 4: Excessive Wasiyyat (Will > 1/3) ───────────────────────────
    DisputePattern.EXCESSIVE_WASIYYAT: {
        "triggers": [
            "will_mentioned",
            "will_bequest_exceeds_one_third",
            "will_leaves_everything_to_one_child",
            "will_excludes_legal_heirs_entirely",
        ],
        "fraud_score": 60,
        "severity":    "MEDIUM",
        "law_sections": {
            "Islamic Law (all Muslim sects)": "A Wasiyyat (will) is valid only up to 1/3 of the net estate after debts and funeral expenses. The remaining 2/3 MUST be distributed by Faraid rules. Heirs cannot be disinherited.",
            "Succession Act 1925 §118": "Applies to non-Muslims — they CAN bequeath more than 1/3.",
        },
        "penalty": "Excess portion of will is void; distributed by Faraid.",
        "immediate_actions": [
            "Calculate 1/3 of net estate",
            "Identify valid portion of will",
            "Recalculate Faraid for remaining 2/3",
            "Send notice to executor if they attempt to enforce excess portion",
        ],
        "documents_to_generate": [
            DocumentType.LEGAL_NOTICE,
        ],
        "court": "Civil Court (if executor refuses)",
        "remedy": "Will partially enforced up to 1/3; rest distributed by Faraid.",
        "urdu_title": "ایک تہائی سے زیادہ وصیت",
        "urdu_action": "وصیت کا ایک تہائی حصہ ہی قانوناً درست ہے",
    },

    # ── Pattern 5: Debt Priority Violation ───────────────────────────────────
    # Heirs distribute estate before paying debts — a very common error.
    DisputePattern.DEBT_PRIORITY: {
        "triggers": [
            "debts_or_loans_mentioned",
            "estate_distributed_without_paying_debts",
            "creditors_complaining",
        ],
        "fraud_score": 90,
        "severity":    "CRITICAL",
        "law_sections": {
            "Islamic Law": "Correct order: (1) Funeral expenses, (2) All debts (including Mehr), (3) Valid Wasiyyat max 1/3, (4) Faraid distribution of remainder.",
            "Succession Act 1925 §317": "Debts of deceased are paid before distribution.",
        },
        "penalty": "Heirs may be personally liable to creditors for underpaid debts.",
        "immediate_actions": [
            "Stop distribution immediately",
            "Collect all debt documents",
            "Pay funeral expenses first",
            "Pay all verified debts",
            "Then calculate Wasiyyat (max 1/3 of remainder)",
            "Then distribute by Faraid",
        ],
        "documents_to_generate": [],
        "court": "Civil Court (if creditors sue heirs)",
        "remedy": "Correct distribution order restores legal standing.",
        "urdu_title": "قرض ادا کیے بغیر تقسیم",
        "urdu_action": "پہلے قرض ادا کریں، پھر وراثت تقسیم کریں",
    },

    # ── Pattern 6: Minor Heir Present ────────────────────────────────────────
    DisputePattern.MINOR_HEIR: {
        "triggers": [
            "heir_age_under_18",
            "heir_described_as_child_or_infant",
            "no_guardian_appointed_for_minor",
        ],
        "fraud_score": 50,   # not fraud, but a process blocker
        "severity":    "MEDIUM",
        "law_sections": {
            "Guardians and Wards Act 1890": "A minor's property interests must be represented by a court-appointed guardian.",
            "Succession Act 1925": "NADRA will not issue succession certificate if any heir is a minor without a guardian order.",
            "MFLO 1961": "Minor heirs retain full inheritance rights — they cannot be excluded.",
        },
        "penalty": "NADRA will reject succession certificate application.",
        "immediate_actions": [
            "File guardian application in District Court (Guardian Judge)",
            "Attach: list of all heirs, minor's B-Form/birth certificate, property list",
            "Court appoints mother or nearest relative as guardian",
            "Then proceed with succession certificate application",
        ],
        "documents_to_generate": [],
        "court": "District Court (Guardian Judge — separate from inheritance court)",
        "remedy": "Guardian appointed; then normal succession process continues.",
        "urdu_title": "نابالغ وارث",
        "urdu_action": "پہلے ضلع عدالت سے سرپرست مقرر کرائیں",
    },

















    

    # ── Pattern 7: Buy-Out Negotiation ───────────────────────────────────────
    # One heir wants to keep property; others want their share in cash.
    DisputePattern.BUYOUT_NEGOTIATION: {
        "triggers": [
            "one_heir_wants_to_keep_property",
            "other_heirs_want_cash_value",
            "mutual_agreement_possible",
        ],
        "fraud_score": 0,    # not fraud — legitimate negotiation path
        "severity":    "INFO",
        "law_sections": {
            "Transfer of Property Act 1882": "Internal transfer between co-owners allowed. All heirs must sign NOC or sale deed.",
            "FBR Finance Act 2025": "Transfer between heirs treated as sale — 236K and 236C apply.",
        },
        "penalty": "None if done legally with registered deed.",
        "immediate_actions": [
            "Calculate each heir's monetary share value",
            "Obtain property valuation (market value)",
            "Generate buy-out agreement template",
            "Calculate 236K tax for buying heir",
            "Calculate 236C tax for each selling heir",
            "Register the transfer deed",
        ],
        "documents_to_generate": [
            DocumentType.BUYOUT_AGREEMENT,
        ],
        "court": "None needed if all heirs agree. Civil Court only if contested.",
        "remedy": "Buying heir pays exact calculated amount; property legally transferred.",
        "urdu_title": "حصہ خریدنا",
        "urdu_action": "تمام وارثین کی رضامندی سے بیع نامہ بنائیں",
    },

    # ── Pattern 8: Daughter's Share Denied ───────────────────────────────────
    # Most common violation in rural Pakistan. Daughters told they get nothing.
    # PPC §498A was specifically enacted for this exact situation.
    DisputePattern.DAUGHTER_SHARE_DENIED: {
        "triggers": [
            "daughters_told_they_inherit_nothing",
            "only_sons_listed_in_mutation",
            "daughters_pressured_to_sign_relinquishment",
            "daughters_threatened_or_coerced",
            "daughters_given_cash_gift_instead_of_legal_share",  # common workaround
        ],
        "fraud_score": 85,
        "severity":    "CRITICAL",
        "law_sections": {
            "PPC §498A": "Specifically enacted for this crime. Anyone who by deceit, coercion, or force deprives a woman of her inheritance is punishable with 5–10 years imprisonment and Rs 1,000,000 fine.",
            "Quran (Surah An-Nisa 4:11)": "Daughters are Quranic heirs. Their shares are fixed by divine law and cannot be altered by family consensus.",
            "PPC §406 (Criminal Breach of Trust)": "May also apply if daughter trusted brother to manage estate and he misappropriated her share.",
            "Constitution of Pakistan Art. 23": "Every citizen can acquire and hold property. No family can override this right.",
        },
        "penalty": "5–10 years imprisonment + Rs 1,000,000 fine (PPC §498A). Criminal — not just civil.",
        "important_note": (
            "A daughter can NEVER be legally disinherited under any Muslim sect. "
            "Not by family consensus. Not by a will (Wasiyyat cannot disinherit Quranic heirs). "
            "Not by a signed paper (relinquishment under pressure is void). "
            "Even if she 'agreed' to get nothing, that agreement is void if made under pressure."
        ),
        "immediate_actions": [
            "File FIR at local police station under PPC §498A",
            "File civil suit for recovery of inheritance share",
            "Send legal notice to brothers/family members denying share",
            "Apply for attachment of property pending court order",
            "Contact Women's Legal Aid: Aurat Foundation helpline 0800-09191 (Punjab)",
        ],
        "documents_to_generate": [
            DocumentType.FIR_DRAFT,
            DocumentType.LEGAL_NOTICE,
        ],
        "court": "Civil Court (for share recovery) + Criminal Court (FIR §498A)",
        "remedy": "Criminal case against perpetrators + full share recovery with interest.",
        "urdu_title": "بیٹی کا حصہ دینے سے انکار",
        "urdu_action": "بیٹی قرآنی وارث ہے۔ اس کا حصہ نہ دینا جرم ہے۔ FIR درج کریں",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — LEGAL DOCUMENT TEMPLATES
# Source: Standard Pakistani legal notice formats + Gemini-generated, reviewed by
#         legal resources at zahidlaw.com and the-legal.org
# ═══════════════════════════════════════════════════════════════════════════════

LEGAL_NOTICE_TEMPLATE_EN: str = """
LEGAL NOTICE
(Without Prejudice)

Date: {date}
Reference No: LN-{ref_no}

FROM:
{sender_name}
{sender_address}
CNIC: {sender_cnic}

TO:
{recipient_name}
{recipient_address}

SUBJECT: Legal Notice Regarding {fraud_title}

Sir / Madam,

I, {sender_name}, am a legal heir of the late {deceased_name} (deceased on {death_date}).
Under {sect} law as applicable in Pakistan, I am legally entitled to {sender_share_fraction}
of the estate of the deceased, amounting to approximately PKR {sender_share_amount:,.0f}.

It has come to my notice that you have committed the following illegal act:
{fraud_description}

This action is in violation of:
{law_sections_list}

You are hereby directed to:
{remedy}

within FIFTEEN (15) days of receiving this notice. Failure to comply will compel me
to initiate legal proceedings against you — both civil and criminal — without further notice.
All costs of such proceedings shall be borne by you.

Yours faithfully,

_________________________
{sender_name}
Legal Heir of late {deceased_name}
"""

LEGAL_NOTICE_TEMPLATE_URDU: str = """
بسم اللہ الرحمن الرحیم
قانونی نوٹس
(بلا تعصب)

تاریخ: {date}
حوالہ نمبر: LN-{ref_no}

ازطرف:
{sender_name}
{sender_address}
شناختی کارڈ: {sender_cnic}

بہ:
{recipient_name}
{recipient_address}

موضوع: {fraud_title} کے بارے میں قانونی نوٹس

محترم / محترمہ،

میں، {sender_name}، مرحوم {deceased_name} (وفات: {death_date}) کا قانونی وارث ہوں۔
{sect} قانون کے مطابق میں جائیداد کے {sender_share_fraction} کا حقدار ہوں جو کہ
تقریباً {sender_share_amount:,.0f} روپے بنتا ہے۔

آپ نے مندرجہ ذیل غیر قانونی کام کیا ہے:
{fraud_description}

یہ عمل مندرجہ ذیل قوانین کی خلاف ورزی ہے:
{law_sections_list}

آپ کو ہدایت کی جاتی ہے کہ پندرہ (15) دنوں کے اندر:
{remedy}

بصورت دیگر آپ کے خلاف دیوانی اور فوجداری دونوں طرح کی قانونی کارروائی کی جائے گی۔
تمام اخراجات آپ کی ذمہ داری ہوں گے۔

دستخط: ______________________
{sender_name}
مرحوم {deceased_name} کے قانونی وارث
"""

FIR_DRAFT_TEMPLATE_EN: str = """
APPLICATION FOR REGISTRATION OF FIR
Under PPC Section {ppc_sections}

TO:
The Station House Officer (SHO)
{police_station_name} Police Station
{police_station_address}

SUBJECT: Criminal complaint regarding inheritance fraud (PPC §{ppc_sections})

Respected Sir,

I, {complainant_name} (CNIC: {complainant_cnic}), son/daughter of {complainant_father_name},
resident of {complainant_address}, hereby submit this complaint:

1. THE DECEASED: Late {deceased_name} passed away on {death_date}.

2. THE LEGAL HEIRS: The legal heirs are:
{heirs_list}

3. THE ACCUSED: {accused_name}, resident of {accused_address}.

4. THE CRIME: The accused has committed the following act in violation of PPC §{ppc_sections}:
{crime_description}

5. EVIDENCE:
{evidence_list}

6. RELIEF SOUGHT:
Register FIR under PPC §{ppc_sections} and take legal action against the accused.
The accused should be arrested and the property/rights restored to all legal heirs.

Submitted by:
{complainant_name}
Date: {date}
Contact: {complainant_phone}
"""

FIR_DRAFT_TEMPLATE_URDU: str = """
درخواست برائے ایف آئی آر
دفعات: {ppc_sections} پاکستان پینل کوڈ

بخدمت:
انچارج تھانہ
تھانہ {police_station_name}
{police_station_address}

موضوع: وراثت میں دھوکہ دہی

جناب،

میں {complainant_name} (شناختی کارڈ: {complainant_cnic})، ولد {complainant_father_name}،
مقیم {complainant_address}، درج ذیل شکایت پیش کرتا/کرتی ہوں:

۱۔ مرحوم: {deceased_name} بتاریخ {death_date} انتقال کر گئے۔

۲۔ قانونی ورثا:
{heirs_list}

۳۔ مدعا علیہ: {accused_name}، مقیم {accused_address}

۴۔ جرم: مدعا علیہ نے دفعہ {ppc_sections} پی پی سی کی خلاف ورزی کرتے ہوئے:
{crime_description}

۵۔ ثبوت:
{evidence_list}

۶۔ استدعا: ایف آئی آر درج کی جائے اور مدعا علیہ کے خلاف قانونی کارروائی کی جائے۔

درخواست گزار: {complainant_name}
تاریخ: {date}
رابطہ: {complainant_phone}
"""

INHERITANCE_CERTIFICATE_TEMPLATE: str = """
══════════════════════════════════════════════════════════════
         WARISNAMA AI — INHERITANCE SHARE CERTIFICATE
══════════════════════════════════════════════════════════════
Certificate No : WN-{certificate_no}
Date Generated : {date}
Reference      : {ref_no}

DECEASED
  Name          : {deceased_name}
  Date of Death : {death_date}
  Religion/Sect : {sect}

ESTATE DETAILS
  Gross Estate Value    : PKR {total_estate:>15,.0f}
  Outstanding Debts     : PKR {debts:>15,.0f}
  Funeral Expenses      : PKR {funeral:>15,.0f}
  Valid Wasiyyat (≤1/3) : PKR {wasiyyat:>15,.0f}
  ─────────────────────────────────────────────
  Distributable Estate  : PKR {distributable:>15,.0f}

INHERITANCE SHARES (under {sect} law)
{share_table}

NEXT STEPS
  1. Obtain Death Certificate from NADRA / Union Council
  2. Apply for Succession Certificate at NADRA office or Civil Court
  3. All heirs sign property mutation at Arazi Record Centre
  4. Consult a lawyer before taking legal action

TAX NOTE
  Pakistan has ZERO inheritance tax. Tax is only applicable
  when an heir SELLS their inherited share (see FBR 2025 rates).

──────────────────────────────────────────────────────────────
DISCLAIMER: This is an AI-generated guide. Shares are calculated
based on {sect} law and MFLO 1961. Consult a qualified lawyer
before taking any legal action. WarisNama AI does not provide
legal advice.
══════════════════════════════════════════════════════════════
"""

BUYOUT_AGREEMENT_TEMPLATE: str = """
INHERITANCE PROPERTY BUY-OUT AGREEMENT
(Draft — for finalisation by a registered lawyer)

Date: {date}
Reference: BO-{ref_no}

PROPERTY: {property_description}
TOTAL VALUE: PKR {total_value:,.0f}

BUYING HEIR   : {buyer_name} (CNIC: {buyer_cnic})
                Share: {buyer_fraction} — buying out remaining heirs

SELLING HEIRS:
{selling_heirs_list}

BUY-OUT AMOUNTS PAYABLE BY {buyer_name}:
{payment_schedule}

TAX OBLIGATIONS:
  Buyer (236K advance tax): PKR {tax_236k:,.0f}
  Each selling heir's 236C: (see individual tax summaries attached)

TERMS:
  1. Payment to be made within 30 days of agreement signing.
  2. Upon payment, each selling heir signs NOC and sale deed.
  3. Property registered in buyer's name at Sub-Registrar office.
  4. All heirs must be present at Sub-Registrar or provide authorised power of attorney.

SIGNATURES:
{signature_blocks}

NOTE: This draft must be reviewed and stamped by a qualified lawyer
before signing. Stamp duty ({stamp_duty_pct}%) applicable at registration.
"""

ARAZI_COMPLAINT_TEMPLATE: str = """
APPLICATION FOR MUTATION REVERSAL / COMPLAINT
To: The District Collector / Arazi Record Centre
    {district_name} District

Date: {date}
Reference: ARC-{ref_no}

COMPLAINANT: {complainant_name} (CNIC: {complainant_cnic})
             Legal heir of late {deceased_name}

SUBJECT: Illegal mutation of property without succession certificate

Respected Sir,

It is stated that late {deceased_name} passed away on {death_date}.
The legal heirs are: {heirs_list}

It has come to our knowledge that {accused_name} (CNIC: {accused_cnic}) has
illegally caused the property described below to be mutated in their sole name
WITHOUT obtaining a succession certificate and WITHOUT the consent or signatures
of other legal heirs.

PROPERTY DETAILS: {property_description}
ILLEGAL MUTATION DATE: {mutation_date}

This mutation is void under the Succession Act 1925 as no succession certificate
was obtained. We request:
  1. Immediate cancellation / reversal of the illegal mutation
  2. Freezing of the property record pending court order
  3. Registration of our complaint in the official record

Supporting Documents Attached:
  - Death certificate of {deceased_name}
  - CNICs of all legal heirs
  - Previous property documents (Fard-e-Malkiat / Intiqal)

Submitted by: {complainant_name}
Contact: {complainant_phone}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — NADRA & COURT PROCESS STEPS
# Source: nadra.gov.pk (Succession Certificate), punjab.gov.pk (Arazi mutation)
#         Letters of Administration and Succession Certificates Act 2020
# ═══════════════════════════════════════════════════════════════════════════════

NADRA_SUCCESSION_PROCESS: Dict[str, Dict[str, Any]] = {

    "step_1": {
        "name":        "Obtain Death Certificate",
        "authority":   "NADRA or Union Council / Town Committee",
        "fee":         "Rs 50 (NADRA) or nominal at Union Council",
        "documents":   [
            "CNIC of deceased (if available)",
            "Medical certificate or hospital death summary",
            "Witness statements (2 witnesses) if no medical certificate",
            "CNIC of applicant (any heir)",
        ],
        "time":        "Same day to 3 working days",
        "note":        "This is mandatory before any other step. Without it, no process can begin.",
        "urdu_name":   "وفاتی سرٹیفکیٹ حاصل کریں",
    },

    "step_2": {
        "name":        "Apply for Succession Certificate",
        "authority":   "NADRA Succession Facilitation Unit (faster) OR Civil District Court (if disputes)",
        "fee":         "Rs 2,000–5,000 approximate. Court fee = 3% of estate value (refundable portion).",
        "documents":   [
            "Death certificate",
            "CNIC of ALL living heirs",
            "B-Form (birth certificate) for minor heirs",
            "Family Registration Certificate (from NADRA)",
            "Property ownership documents (Fard / Intiqal / title deed)",
            "List of all assets and liabilities",
        ],
        "time":        "NADRA route: 15–30 days. Court route: 30–90 days.",
        "note":        "CRITICAL: If any heir is under 18, court must appoint a guardian FIRST (see step_2b).",
        "urdu_name":   "وراثت سرٹیفکیٹ کے لیے درخواست دیں",
    },

    "step_2b_minor_guardian": {
        "name":        "Court Guardian Appointment (only if minor heir exists)",
        "authority":   "District Court — Guardian Judge",
        "fee":         "Court filing fee (nominal)",
        "documents":   [
            "B-Form / birth certificate of minor",
            "CNIC of proposed guardian (usually mother or nearest relative)",
            "Death certificate",
            "List of heirs",
        ],
        "time":        "30–60 days",
        "note":        "After guardian is appointed, proceed to step_2 with guardian representing minor.",
        "urdu_name":   "نابالغ کے لیے سرپرست کی تقرری",
    },

    "step_3": {
        "name":        "Mutation of Property at Arazi Record Centre",
        "authority":   "Arazi Record Centre / Patwari / Tehsildar",
        "fee":         "Rs 500–2,000 nominal government fee",
        "documents":   [
            "Succession certificate (original)",
            "Death certificate",
            "Original Fard-e-Malkiat (land record)",
            "Original Intiqal (mutation record)",
            "CNICs of ALL heirs",
            "NOC/signatures of ALL heirs (or their duly authorised representatives)",
        ],
        "time":        "30 days after complete application",
        "note":        "ALL heirs must sign or provide NOC. Single-heir mutation without others' consent is fraudulent and reversible under Succession Act 1925.",
        "urdu_name":   "ارازی ریکارڈ سینٹر میں انتقال",
    },

    "step_4": {
        "name":        "Registration of Transfer (if selling property)",
        "authority":   "Sub-Registrar Office (Stamp Registration Department)",
        "fee":         "Stamp Duty (1–3%) + Registration Fee (0.5–1%) + Advance Tax 236C (seller) + 236K (buyer)",
        "documents":   [
            "Registered sale deed (drafted by a lawyer)",
            "Succession certificate",
            "CNICs of buyer and all selling heirs",
            "FBR tax clearance / 7E certificate",
            "Mutation record (after step_3)",
            "NOC from all co-owners if partial sale",
        ],
        "time":        "7–14 working days",
        "note":        "FBR's IRIS system must be used to generate PSID payment slip for taxes. Registrar will not proceed without tax payment confirmation.",
        "urdu_name":   "رجسٹریشن (اگر فروخت کرنی ہو)",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — VALIDATION CONSTANTS & BUSINESS RULES
# ═══════════════════════════════════════════════════════════════════════════════

WASIYYAT_MAX_FRACTION: Fraction = Fraction(1, 3)   # will cannot exceed 1/3 of net estate
MINOR_AGE_THRESHOLD: int = 18                       # under 18 = minor in Pakistan
LEGAL_NOTICE_DEADLINE_DAYS: int = 15                # standard legal notice deadline
FIR_LAW_INHERITANCE_DENIAL: str = "PPC §498A"
MIN_ESTATE_VALUE_PKR: float = 1.0                   # sanity check: estate > 0
MAX_WIVES_HANAFI: int = 4                           # Islamic law max 4 wives
WOMEN_HELPLINE_PUNJAB: str = "0800-09191"           # Aurat Foundation Punjab
WOMEN_HELPLINE_NATIONAL: str = "1099"               # National Commission on Status of Women


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — COMPLETE HELPER FUNCTIONS (production-ready, fully validated)
# ═══════════════════════════════════════════════════════════════════════════════

# ── Tax Bracket ───────────────────────────────────────────────────────────────

def get_tax_bracket(value_pkr: float) -> str:
    """
    Return the FBR tax bracket key for a given property value.

    Args:
        value_pkr: Property value in Pakistani Rupees.

    Returns:
        Bracket key string: 'up_to_50M', '50M_to_100M', or 'over_100M'.

    Raises:
        ValueError: If value_pkr is negative.
    """
    if value_pkr < 0:
        raise ValueError(f"Property value cannot be negative. Got: {value_pkr}")
    if value_pkr <= 50_000_000:
        return "up_to_50M"
    elif value_pkr <= 100_000_000:
        return "50M_to_100M"
    else:
        return "over_100M"


# ── 236C (Seller Tax) ─────────────────────────────────────────────────────────

def get_236c_rate(value_pkr: float, filer_status: str) -> float:
    """
    Return the Section 236C advance tax rate for the SELLER.

    Args:
        value_pkr    : Property value in PKR (full property value, not heir's share).
        filer_status : 'filer', 'late_filer', or 'non_filer'.

    Returns:
        Tax rate as a decimal (e.g. 0.03 for 3%).

    Raises:
        ValueError: On invalid filer_status or negative value.
    """
    _validate_filer_status(filer_status)
    bracket = get_tax_bracket(value_pkr)
    return TAX_236C[bracket][filer_status]


def calculate_236c_tax(share_value_pkr: float, full_property_value_pkr: float,
                        filer_status: str) -> float:
    """
    Calculate the actual 236C advance tax amount payable by a selling heir.

    NOTE: The TAX RATE is determined by the FULL property value (FBR bracket),
    but the TAX AMOUNT is calculated on the heir's SHARE value only.

    Args:
        share_value_pkr        : The heir's share value in PKR.
        full_property_value_pkr: Full market value of the whole property.
        filer_status           : 'filer', 'late_filer', or 'non_filer'.

    Returns:
        Tax amount in PKR (rounded to nearest rupee).
    """
    rate = get_236c_rate(full_property_value_pkr, filer_status)
    return round(share_value_pkr * rate, 0)


# ── 236K (Buyer Tax) ──────────────────────────────────────────────────────────

def get_236k_rate(value_pkr: float, filer_status: str) -> float:
    """
    Return the Section 236K advance tax rate for the BUYER.

    Args:
        value_pkr    : Property value in PKR.
        filer_status : 'filer', 'late_filer', or 'non_filer'.

    Returns:
        Tax rate as a decimal.
    """
    _validate_filer_status(filer_status)
    bracket = get_tax_bracket(value_pkr)
    return TAX_236K[bracket][filer_status]


def calculate_236k_tax(purchase_value_pkr: float, filer_status: str) -> float:
    """
    Calculate the actual 236K advance tax amount payable by a buying heir.

    Args:
        purchase_value_pkr: Amount being paid to purchase the share.
        filer_status       : 'filer', 'late_filer', or 'non_filer'.

    Returns:
        Tax amount in PKR (rounded to nearest rupee).
    """
    rate = get_236k_rate(purchase_value_pkr, filer_status)
    return round(purchase_value_pkr * rate, 0)


# ── Capital Gains Tax ─────────────────────────────────────────────────────────

def get_cgt_rate(
    filer_status: str,
    acquisition_after_july_2024: bool,
    holding_years: Optional[int] = None,
    sale_value_pkr: float = 0.0,
) -> float:
    """
    Return the Capital Gains Tax rate for a property sale.

    IMPORTANT: For inherited property, use acquisition_after_july_2024=True
    and treat the inheritance date as the acquisition date (step-up basis).

    Args:
        filer_status              : 'filer', 'late_filer', or 'non_filer'.
        acquisition_after_july_2024: True if acquired (or inherited) on/after July 1, 2024.
        holding_years             : Years held (required if acquisition_after_july_2024=False).
        sale_value_pkr            : Sale value (required for non-filer sliding scale post-2024).

    Returns:
        CGT rate as a decimal.

    Raises:
        ValueError: If holding_years missing for pre-2024 acquisition.
    """
    _validate_filer_status(filer_status)

    if not acquisition_after_july_2024:
        # Pre-July 2024 sliding scale
        if holding_years is None:
            raise ValueError("holding_years required for pre-July-2024 property CGT calculation.")
        scale = CGT_RULES["pre_july_2024_sliding"]
        if holding_years <= 0:
            return scale["year_1"]
        elif holding_years == 1:
            return scale["year_1"]
        elif holding_years == 2:
            return scale["year_2"]
        elif holding_years == 3:
            return scale["year_3"]
        elif holding_years == 4:
            return scale["year_4"]
        elif holding_years == 5:
            return scale["year_5"]
        else:
            return scale["year_6_plus"]  # 0.0 after 6 years

    # Post-July 2024
    post = CGT_RULES["post_july_2024"]
    if filer_status == FilerStatus.FILER:
        return post["filer_flat_rate"]   # flat 15%

    # Non-filer: sliding scale by value
    sliding = post["non_filer_by_value"]
    if sale_value_pkr <= 25_000_000:
        return sliding["up_to_25M"]
    elif sale_value_pkr <= 50_000_000:
        return sliding["25M_to_50M"]
    else:
        return sliding["over_50M"]


def calculate_cgt(
    sale_value_pkr: float,
    inheritance_value_pkr: float,
    filer_status: str,
    acquisition_after_july_2024: bool = True,
    holding_years: Optional[int] = None,
) -> float:
    """
    Calculate Capital Gains Tax for an inherited property that is being sold.

    Inherited property uses STEP-UP BASIS: CGT is ONLY on gain since inheritance.
    If selling at or below inheritance value, CGT = 0.

    Args:
        sale_value_pkr          : Current sale price of heir's share.
        inheritance_value_pkr   : FMV of heir's share at date of inheritance (step-up basis).
        filer_status            : 'filer', 'late_filer', or 'non_filer'.
        acquisition_after_july_2024: Usually True for inherited property (inherited now).
        holding_years           : Relevant for pre-2024 properties.

    Returns:
        CGT amount in PKR. Returns 0 if no gain exists.
    """
    gain = sale_value_pkr - inheritance_value_pkr
    if gain <= 0:
        return 0.0   # no gain, no CGT

    rate = get_cgt_rate(
        filer_status=filer_status,
        acquisition_after_july_2024=acquisition_after_july_2024,
        holding_years=holding_years,
        sale_value_pkr=sale_value_pkr,
    )
    return round(gain * rate, 0)


# ── Stamp Duty & Registration ─────────────────────────────────────────────────

def get_stamp_duty_rate(province: str = Province.DEFAULT) -> float:
    """
    Return stamp duty rate for a given province.

    Args:
        province: Province name string or Province enum value.

    Returns:
        Stamp duty rate as a decimal (e.g. 0.01 for 1%).
    """
    return STAMP_DUTY.get(province, STAMP_DUTY[Province.DEFAULT])


def calculate_stamp_duty(property_value_pkr: float, province: str = Province.DEFAULT) -> float:
    """
    Calculate stamp duty amount.

    Args:
        property_value_pkr: Declared or FBR-valued property value.
        province          : Province name.

    Returns:
        Stamp duty amount in PKR.
    """
    rate = get_stamp_duty_rate(province)
    return round(property_value_pkr * rate, 0)


def calculate_cvt(property_value_pkr: float) -> float:
    """
    Calculate Capital Value Tax (buyer pays once at registration).

    Args:
        property_value_pkr: Property value.

    Returns:
        CVT amount in PKR.
    """
    return round(property_value_pkr * CVT_RATE, 0)


# ── Complete Tax Summary ──────────────────────────────────────────────────────

def calculate_full_tax_summary(
    share_value_pkr: float,
    full_property_value_pkr: float,
    filer_status: str,
    action: str,
    province: str = Province.DEFAULT,
    acquisition_after_july_2024: bool = True,
    holding_years: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculate ALL applicable taxes for an heir based on their intended action.

    Args:
        share_value_pkr         : Monetary value of this heir's inherited share.
        full_property_value_pkr : Full property market value (determines bracket).
        filer_status            : 'filer', 'late_filer', or 'non_filer'.
        action                  : 'sell', 'hold', or 'buyout' (buying others out).
        province                : Province for stamp duty.
        acquisition_after_july_2024: For CGT calculation.
        holding_years           : For pre-2024 CGT sliding scale.

    Returns:
        Dictionary with all tax amounts and a net-after-tax figure.
    """
    _validate_filer_status(filer_status)
    if action not in ("sell", "hold", "buyout"):
        raise ValueError(f"action must be 'sell', 'hold', or 'buyout'. Got: {action}")

    result: Dict[str, Any] = {
        "share_value_pkr":          share_value_pkr,
        "full_property_value_pkr":  full_property_value_pkr,
        "filer_status":             filer_status,
        "action":                   action,
        "inheritance_tax":          0.0,  # always zero
        "advance_tax_236C":         0.0,
        "advance_tax_236K":         0.0,
        "cgt":                      0.0,
        "cvt":                      0.0,
        "stamp_duty":               0.0,
        "registration_fee":         0.0,
        "total_tax_outflow":        0.0,
        "net_after_all_taxes":      0.0,
        "savings_if_filer":         0.0,
        "recommendation":           "",
    }

    if action == "hold":
        result["recommendation"] = (
            "No tax payable while holding. Only Section 7E (~1% annual deemed income tax) "
            "may apply if you own multiple properties. Exempt for single self-occupied home."
        )
        result["net_after_all_taxes"] = share_value_pkr
        return result

    elif action == "sell":
        tax_236c = calculate_236c_tax(share_value_pkr, full_property_value_pkr, filer_status)
        cgt      = calculate_cgt(
            sale_value_pkr=share_value_pkr,
            inheritance_value_pkr=share_value_pkr,  # step-up: no gain at time of inheritance
            filer_status=filer_status,
            acquisition_after_july_2024=acquisition_after_july_2024,
            holding_years=holding_years,
        )
        total = tax_236c + cgt
        result.update({
            "advance_tax_236C":   tax_236c,
            "cgt":                cgt,
            "total_tax_outflow":  total,
            "net_after_all_taxes": share_value_pkr - total,
        })

        # Show savings if they were a filer
        if filer_status != FilerStatus.FILER:
            filer_236c = calculate_236c_tax(share_value_pkr, full_property_value_pkr, FilerStatus.FILER)
            result["savings_if_filer"] = tax_236c - filer_236c
            result["recommendation"] = (
                f"Becoming an ATL filer before selling would save you "
                f"PKR {result['savings_if_filer']:,.0f}. "
                f"Register at iris.fbr.gov.pk before executing the sale deed."
            )
        else:
            result["recommendation"] = (
                f"As an ATL filer, you pay the minimum tax rate. "
                f"Total tax: PKR {total:,.0f} on share of PKR {share_value_pkr:,.0f}."
            )

    elif action == "buyout":
        # Buying heir pays 236K + CVT + Stamp Duty
        tax_236k  = calculate_236k_tax(share_value_pkr, filer_status)
        cvt       = calculate_cvt(share_value_pkr)
        stamp     = calculate_stamp_duty(share_value_pkr, province)
        reg_fee   = round(share_value_pkr * REGISTRATION_FEE, 0)
        total     = tax_236k + cvt + stamp + reg_fee
        result.update({
            "advance_tax_236K":  tax_236k,
            "cvt":               cvt,
            "stamp_duty":        stamp,
            "registration_fee":  reg_fee,
            "total_tax_outflow": total,
            "net_after_all_taxes": share_value_pkr + total,  # total cost to buyer
            "recommendation": (
                f"To buy out others' shares, you pay their share value PLUS taxes. "
                f"Total outflow: PKR {share_value_pkr + total:,.0f} "
                f"(share value PKR {share_value_pkr:,.0f} + taxes PKR {total:,.0f})."
            ),
        })

    return result


# ── Wasiyyat Validation ───────────────────────────────────────────────────────

def validate_wasiyyat(wasiyyat_pkr: float, net_estate_pkr: float) -> Tuple[float, bool, str]:
    """
    Validate a Wasiyyat (will) amount against the 1/3 Islamic limit.

    Args:
        wasiyyat_pkr : Amount bequeathed in the will.
        net_estate_pkr: Net estate after debts and funeral expenses.

    Returns:
        Tuple of (valid_wasiyyat_pkr, is_excessive, explanation_string).
    """
    if net_estate_pkr <= 0:
        return 0.0, False, "Net estate is zero or negative — no Wasiyyat applicable."

    max_allowed = float(WASIYYAT_MAX_FRACTION * Fraction(net_estate_pkr).limit_denominator(100))
    is_excessive = wasiyyat_pkr > max_allowed

    if is_excessive:
        explanation = (
            f"The will amount (PKR {wasiyyat_pkr:,.0f}) exceeds the Islamic maximum of 1/3 "
            f"(PKR {max_allowed:,.0f}). Under all Muslim sects, a Wasiyyat cannot exceed "
            f"1/3 of the net estate. The excess (PKR {wasiyyat_pkr - max_allowed:,.0f}) "
            f"is void and must be distributed by Faraid rules."
        )
        return max_allowed, True, explanation
    else:
        explanation = (
            f"The will amount (PKR {wasiyyat_pkr:,.0f}) is within the 1/3 limit "
            f"(PKR {max_allowed:,.0f}). It is valid."
        )
        return wasiyyat_pkr, False, explanation


# ── Dispute Detection ─────────────────────────────────────────────────────────

def detect_disputes(trigger_flags: List[str]) -> List[Dict[str, Any]]:
    """
    Match user-described situation flags against all 8 dispute patterns.

    Args:
        trigger_flags: List of trigger strings from user's scenario.
                       e.g. ['mutation_by_single_heir', 'no_succession_certificate_obtained']

    Returns:
        List of matched dispute dictionaries, sorted by fraud_score descending.
        Each dict contains the full pattern + 'pattern_key'.
    """
    if not trigger_flags:
        return []

    matched = []
    trigger_set = set(trigger_flags)

    for pattern_key, pattern in DISPUTE_PATTERNS.items():
        pattern_triggers = set(pattern.get("triggers", []))
        overlap = trigger_set & pattern_triggers
        if overlap:
            result = dict(pattern)
            result["pattern_key"]     = pattern_key
            result["matched_triggers"] = list(overlap)
            result["match_strength"]  = len(overlap) / max(len(pattern_triggers), 1)
            matched.append(result)

    matched.sort(key=lambda x: x["fraud_score"], reverse=True)
    return matched


def get_fraud_severity_label(fraud_score: int) -> str:
    """
    Return a human-readable severity label for a fraud score.

    Args:
        fraud_score: Integer 0–100.

    Returns:
        Severity label string.
    """
    if fraud_score >= 80:
        return "CRITICAL 🔴"
    elif fraud_score >= 60:
        return "HIGH 🟠"
    elif fraud_score >= 40:
        return "MEDIUM 🟡"
    elif fraud_score > 0:
        return "LOW 🟢"
    else:
        return "INFO ℹ️"


# ── NADRA Process Selector ────────────────────────────────────────────────────

def get_process_steps(has_minor_heir: bool = False, is_selling: bool = False) -> List[Dict]:
    """
    Return the relevant NADRA/court process steps for a given scenario.

    Args:
        has_minor_heir: True if any heir is under 18.
        is_selling    : True if heirs intend to sell the property.

    Returns:
        Ordered list of process step dictionaries.
    """
    steps = [NADRA_SUCCESSION_PROCESS["step_1"]]

    if has_minor_heir:
        steps.append(NADRA_SUCCESSION_PROCESS["step_2b_minor_guardian"])

    steps.append(NADRA_SUCCESSION_PROCESS["step_2"])
    steps.append(NADRA_SUCCESSION_PROCESS["step_3"])

    if is_selling:
        steps.append(NADRA_SUCCESSION_PROCESS["step_4"])

    return steps


# ── Heir Validation ───────────────────────────────────────────────────────────

def validate_heir_count(heir_type: str, count: int) -> Tuple[bool, str]:
    """
    Validate the count of a given heir type against legal constraints.

    Args:
        heir_type: Heir type string.
        count    : Number of heirs of this type.

    Returns:
        Tuple (is_valid, error_message_if_invalid).
    """
    if count < 0:
        return False, f"Heir count cannot be negative for {heir_type}."
    if heir_type == "husband" and count > 1:
        return False, "A woman can only have one husband."
    if heir_type == "wife" and count > MAX_WIVES_HANAFI:
        return False, f"Islamic law permits a maximum of {MAX_WIVES_HANAFI} wives."
    if heir_type in ("father", "mother") and count > 1:
        return False, f"A person can only have one {heir_type}."
    return True, ""


def is_minor(age: Optional[int]) -> bool:
    """Return True if age is below the legal minor threshold (18 years)."""
    if age is None:
        return False
    return age < MINOR_AGE_THRESHOLD


def check_any_minor(heirs: List[Dict[str, Any]]) -> bool:
    """
    Check if any heir in the list is a minor.

    Args:
        heirs: List of heir dicts, each optionally containing 'age' key.

    Returns:
        True if at least one heir is under 18.
    """
    return any(is_minor(h.get("age")) for h in heirs)


# ── Estate Validation ─────────────────────────────────────────────────────────

def validate_estate(total_estate_pkr: float, debts_pkr: float = 0.0,
                    funeral_pkr: float = 0.0) -> Tuple[float, str]:
    """
    Validate and compute the distributable estate after deductions.

    Correct Islamic order:
        1. Funeral expenses
        2. Outstanding debts (including unpaid Mehr)
        3. Valid Wasiyyat (max 1/3 of remainder)
        4. Faraid distribution of remainder

    Args:
        total_estate_pkr: Gross estate value.
        debts_pkr       : Total outstanding debts.
        funeral_pkr     : Funeral / burial expenses.

    Returns:
        Tuple (distributable_amount, warning_message).
    """
    warning = ""
    if total_estate_pkr <= 0:
        raise ValueError("Total estate value must be greater than zero.")

    distributable = total_estate_pkr - funeral_pkr - debts_pkr

    if distributable < 0:
        warning = (
            f"WARNING: Debts (PKR {debts_pkr:,.0f}) exceed the estate value "
            f"(PKR {total_estate_pkr:,.0f}). Heirs may be personally liable for excess debts. "
            f"Consult a lawyer immediately."
        )
        distributable = 0.0
    elif debts_pkr > 0:
        warning = (
            f"Debts of PKR {debts_pkr:,.0f} have been deducted first as required by Islamic law. "
            f"Distributable estate: PKR {distributable:,.0f}."
        )

    return distributable, warning


# ── Certificate & Reference Number Generation ─────────────────────────────────

def generate_certificate_number() -> str:
    """Generate a unique certificate reference number."""
    today = datetime.date.today().strftime("%Y%m%d")
    short_uuid = str(uuid.uuid4()).upper()[:8]
    return f"WN-{today}-{short_uuid}"


def generate_ref_number(prefix: str = "REF") -> str:
    """Generate a unique reference number for documents."""
    short_uuid = str(uuid.uuid4()).upper()[:6]
    return f"{prefix}-{short_uuid}"


# ── Awl (Proportional Reduction) ─────────────────────────────────────────────

def apply_awl(shares: Dict[str, Fraction]) -> Dict[str, Fraction]:
    """
    Apply Awl (proportional reduction) if fixed shares exceed the estate.

    When the sum of Quranic fixed shares is greater than 1 (the whole estate),
    each share is reduced proportionally so they sum to exactly 1.

    Args:
        shares: Dict mapping heir identifier → Fraction share.

    Returns:
        Adjusted shares dict (values sum to ≤ 1).
    """
    total = sum(shares.values())
    if total <= Fraction(1):
        return shares   # no Awl needed

    # Reduce proportionally
    return {heir: Fraction(share, total) for heir, share in shares.items()}


# ── Radd (Surplus Return) — Hanafi ───────────────────────────────────────────

def apply_hanafi_radd(shares: Dict[str, Fraction],
                       heir_types: Dict[str, str]) -> Dict[str, Fraction]:
    """
    Apply Hanafi Radd: return surplus to non-spouse Quranic heirs proportionally.

    Called when sum of fixed shares < 1 and no Asaba (residue) heir exists.
    Spouse (husband/wife) is EXCLUDED from Radd in Hanafi law.

    Args:
        shares    : Dict of heir_id → Fraction (current fixed shares).
        heir_types: Dict of heir_id → heir_type_string (e.g. 'wife', 'daughter').

    Returns:
        Adjusted shares after Radd applied.
    """
    total = sum(shares.values())
    surplus = Fraction(1) - total

    if surplus <= 0:
        return shares   # no surplus to return

    # Identify non-spouse heirs eligible for Radd
    radd_eligible = {
        heir_id: share
        for heir_id, share in shares.items()
        if heir_types.get(heir_id) not in ("husband", "wife")
    }

    if not radd_eligible:
        # Only spouses — surplus goes to Bayt-ul-Mal (public treasury)
        # In practice, courts often return to spouses in Pakistan
        return shares

    radd_total = sum(radd_eligible.values())
    adjusted = dict(shares)
    for heir_id, share in radd_eligible.items():
        # Proportional Radd: each eligible heir gets surplus in proportion to their share
        radd_amount = surplus * Fraction(share, radd_total)
        adjusted[heir_id] = share + radd_amount

    return adjusted


# ── Fraction Formatting ───────────────────────────────────────────────────────

def fraction_to_display(frac: Fraction) -> str:
    """
    Convert a Fraction to a human-readable string.

    Examples:
        Fraction(1, 8)  → "1/8"
        Fraction(1, 1)  → "Full estate"
        Fraction(2, 3)  → "2/3"

    Args:
        frac: A Python Fraction object.

    Returns:
        Display string.
    """
    if frac == Fraction(1):
        return "Full estate"
    if frac == Fraction(0):
        return "0 (excluded)"
    return f"{frac.numerator}/{frac.denominator}"


def fraction_to_urdu(frac: Fraction) -> str:
    """
    Convert a Fraction to an Urdu text representation.

    Args:
        frac: A Python Fraction object.

    Returns:
        Urdu string representation.
    """
    urdu_nums = {
        1: "ایک", 2: "دو", 3: "تین", 4: "چار",
        5: "پانچ", 6: "چھ", 7: "سات", 8: "آٹھ",
        9: "نو", 10: "دس", 12: "بارہ", 16: "سولہ",
    }
    if frac == Fraction(1):
        return "پوری جائیداد"
    if frac == Fraction(0):
        return "کوئی حصہ نہیں"
    n = urdu_nums.get(frac.numerator, str(frac.numerator))
    d = urdu_nums.get(frac.denominator, str(frac.denominator))
    return f"{d} میں سے {n} حصہ"


# ── Internal Validation Helper ────────────────────────────────────────────────

def _validate_filer_status(filer_status: str) -> None:
    """Raise ValueError if filer_status is not a valid FilerStatus value."""
    valid = {FilerStatus.FILER, FilerStatus.LATE_FILER, FilerStatus.NON_FILER}
    if filer_status not in valid:
        raise ValueError(
            f"Invalid filer_status '{filer_status}'. "
            f"Must be one of: {[v.value for v in valid]}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — QUICK REFERENCE LOOKUPS (for UI display)
# ═══════════════════════════════════════════════════════════════════════════════

SECT_DISPLAY_NAMES: Dict[str, str] = {
    Sect.HANAFI:    "Sunni Hanafi",
    Sect.SHIA:      "Shia Jafari (Ithna Ashari)",
    Sect.CHRISTIAN: "Christian (Succession Act 1925)",
    Sect.HINDU:     "Hindu (Hindu Succession Act 1956)",
}

SECT_DISPLAY_URDU: Dict[str, str] = {
    Sect.HANAFI:    "سنی حنفی",
    Sect.SHIA:      "شیعہ جعفری",
    Sect.CHRISTIAN: "مسیحی (ایکٹ 1925)",
    Sect.HINDU:     "ہندو (ایکٹ 1956)",
}

HEIR_DISPLAY_URDU: Dict[str, str] = {
    "husband":          "شوہر",
    "wife":             "بیوی",
    "son":              "بیٹا",
    "daughter":         "بیٹی",
    "father":           "والد",
    "mother":           "والدہ",
    "grandson":         "پوتا",
    "granddaughter":    "پوتی",
    "full_brother":     "سگا بھائی",
    "full_sister":      "سگی بہن",
    "paternal_uncle":   "چچا",
    "paternal_grandfather": "دادا",
    "paternal_grandmother": "دادی",
    "maternal_grandmother": "نانی",
}

ASSET_DISPLAY_URDU: Dict[str, str] = {
    "house":            "مکان",
    "plot":             "پلاٹ",
    "shop":             "دکان",
    "agricultural_land": "زرعی زمین",
    "apartment":        "فلیٹ",
    "car":              "گاڑی",
    "cash":             "نقد رقم",
    "bank_account":     "بینک اکاؤنٹ",
    "business":         "کاروبار",
    "jewelry":          "زیورات",
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 12 — SELF-TEST (run with: python knowledge_base.py)
# ═══════════════════════════════════════════════════════════════════════════════

def _run_self_tests() -> None:
    """Run basic sanity checks on all critical functions."""
    print("=" * 60)
    print("WarisNama AI — knowledge_base.py self-test")
    print("=" * 60)

    # Tax bracket tests
    assert get_tax_bracket(0) == "up_to_50M"
    assert get_tax_bracket(50_000_000) == "up_to_50M"
    assert get_tax_bracket(50_000_001) == "50M_to_100M"
    assert get_tax_bracket(100_000_001) == "over_100M"
    print("✓ Tax bracket detection")

    # 236C rate tests
    assert get_236c_rate(30_000_000, FilerStatus.FILER)      == 0.03
    assert get_236c_rate(30_000_000, FilerStatus.NON_FILER)  == 0.13
    assert get_236c_rate(60_000_000, FilerStatus.FILER)      == 0.035
    assert get_236c_rate(60_000_000, FilerStatus.NON_FILER)  == 0.16
    assert get_236c_rate(110_000_000, FilerStatus.NON_FILER) == 0.20
    print("✓ 236C rates")

    # 236K rate tests
    assert get_236k_rate(30_000_000, FilerStatus.FILER)      == 0.03
    assert get_236k_rate(30_000_000, FilerStatus.NON_FILER)  == 0.10
    assert get_236k_rate(110_000_000, FilerStatus.NON_FILER) == 0.10
    print("✓ 236K rates")

    # CGT tests
    rate = get_cgt_rate(FilerStatus.FILER, acquisition_after_july_2024=True)
    assert rate == 0.15
    rate_pre = get_cgt_rate(FilerStatus.FILER, acquisition_after_july_2024=False, holding_years=6)
    assert rate_pre == 0.00
    print("✓ CGT rates")

    # CGT with step-up basis — no gain at time of inheritance
    cgt_at_inheritance = calculate_cgt(
        sale_value_pkr=1_000_000, inheritance_value_pkr=1_000_000,
        filer_status=FilerStatus.FILER
    )
    assert cgt_at_inheritance == 0.0
    print("✓ CGT step-up basis (zero CGT at time of inheritance)")

    # Wasiyyat validation
    valid_w, excessive, _ = validate_wasiyyat(500_000, 1_500_000)
    assert not excessive
    assert valid_w == 500_000
    invalid_w, excessive2, _ = validate_wasiyyat(700_000, 1_500_000)
    assert excessive2
    assert abs(invalid_w - 500_000) < 1  # max = 1/3 of 1.5M = 500K
    print("✓ Wasiyyat validation")

    # Estate validation
    distributable, warning = validate_estate(10_000_000, debts_pkr=2_000_000, funeral_pkr=100_000)
    assert abs(distributable - 7_900_000) < 1
    print("✓ Estate validation")

    # Dispute detection
    flags = ["mutation_by_single_heir", "no_succession_certificate_obtained"]
    disputes = detect_disputes(flags)
    assert len(disputes) > 0
    assert disputes[0]["pattern_key"] == DisputePattern.FRAUDULENT_MUTATION
    print("✓ Dispute detection")

    # Daughter share denied pattern exists
    assert DisputePattern.DAUGHTER_SHARE_DENIED in DISPUTE_PATTERNS
    print("✓ Daughter's share denied pattern")

    # Awl test: shares summing to > 1
    test_shares = {"a": Fraction(1, 2), "b": Fraction(2, 3)}
    awl_result = apply_awl(test_shares)
    total_after = sum(awl_result.values())
    assert total_after == Fraction(1), f"Awl result should sum to 1, got {total_after}"
    print("✓ Awl (proportional reduction)")

    # Fraction display
    assert fraction_to_display(Fraction(1, 8)) == "1/8"
    assert fraction_to_display(Fraction(1, 1)) == "Full estate"
    print("✓ Fraction display helpers")

    # Heir validation
    valid, msg = validate_heir_count("wife", 5)
    assert not valid   # max 4 wives
    valid2, _ = validate_heir_count("wife", 2)
    assert valid2
    print("✓ Heir count validation")

    # Minor detection
    assert is_minor(17) is True
    assert is_minor(18) is False
    assert is_minor(None) is False
    print("✓ Minor heir detection")

    # Fractions are exact (no floating-point errors)
    total_hanafi = (
        HANAFI_FIXED_SHARES["wife_with_children"] +
        HANAFI_FIXED_SHARES["mother_with_children"] +
        HANAFI_FIXED_SHARES["father_fixed_minimum"]
    )
    assert isinstance(total_hanafi, Fraction)  # must stay as Fraction, never float
    print("✓ Fraction type integrity (no float contamination)")

    print()
    print("All self-tests passed. knowledge_base.py is production-ready.")
    print("=" * 60)


if __name__ == "__main__":
    _run_self_tests()