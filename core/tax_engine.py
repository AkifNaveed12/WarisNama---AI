# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# """
# WarisNama AI — tax_engine.py
# =================================
# Thin orchestration layer over knowledge_base tax system.

# All tax calculations MUST come from knowledge_base to ensure:
# ✔ Legal accuracy (FBR 2025)
# ✔ No duplication
# ✔ Consistency across modules
# """

# from typing import Dict, Any

# from core.knowledge_base import (
#     calculate_full_tax_summary,
#     FilerStatus,
#     Province
# )


# # ─────────────────────────────────────────────
# # Single Heir Tax Calculation
# # ─────────────────────────────────────────────
# def calculate_heir_tax(
#     share_value_pkr: float,
#     full_property_value_pkr: float,
#     filer_status: str,
#     action: str,
#     province: str = Province.DEFAULT,
#     acquisition_after_july_2024: bool = True,
#     holding_years: int = None
# ) -> Dict[str, Any]:
#     """
#     Calculate ALL taxes for a single heir.

#     Args:
#         share_value_pkr         : Heir's share value
#         full_property_value_pkr : FULL property value (CRITICAL for tax brackets)
#         filer_status            : 'filer', 'late_filer', 'non_filer'
#         action                  : 'sell', 'hold', 'buyout'
#         province                : Province for stamp duty
#         acquisition_after_july_2024 : CGT rule selector
#         holding_years           : Needed for pre-2024 CGT

#     Returns:
#         Complete tax breakdown dict
#     """

#     return calculate_full_tax_summary(
#         share_value_pkr=share_value_pkr,
#         full_property_value_pkr=full_property_value_pkr,
#         filer_status=filer_status,
#         action=action,
#         province=province,
#         acquisition_after_july_2024=acquisition_after_july_2024,
#         holding_years=holding_years
#     )


# # ─────────────────────────────────────────────
# # Multi-Heir Tax Calculation
# # ─────────────────────────────────────────────
# def calculate_all_heirs_tax(
#     heirs_shares: Dict[str, Dict],
#     filer_status_map: Dict[str, str],
#     full_property_value_pkr: float,
#     action: str = "sell",
#     province: str = Province.DEFAULT,
#     acquisition_after_july_2024: bool = True,
#     holding_years: int = None
# ) -> Dict[str, Dict]:
#     """
#     Calculate taxes for ALL heirs.

#     Args:
#         heirs_shares: {
#             heir_id: {
#                 'amount': float,
#                 ...
#             }
#         }
#         filer_status_map: {
#             heir_id: 'filer' / 'late_filer' / 'non_filer'
#         }
#         full_property_value_pkr: FULL estate/property value
#         action: 'sell', 'hold', 'buyout'
#         province: Province
#         acquisition_after_july_2024: CGT rule
#         holding_years: for pre-2024 CGT

#     Returns:
#         Dict of heir_id → tax breakdown
#     """

#     results = {}

#     for heir_id, data in heirs_shares.items():

#         share_value = data.get("amount", 0.0)

#         filer_status = filer_status_map.get(
#             heir_id,
#             FilerStatus.NON_FILER  # default
#         )

#         results[heir_id] = calculate_heir_tax(
#             share_value_pkr=share_value,
#             full_property_value_pkr=full_property_value_pkr,
#             filer_status=filer_status,
#             action=action,
#             province=province,
#             acquisition_after_july_2024=acquisition_after_july_2024,
#             holding_years=holding_years
#         )

#     return results

# # Add this export at the bottom of tax_engine.py
# def calculate_heir_tax(
#     share_value_pkr: float,
#     full_property_value_pkr: float,
#     filer_status: str,
#     action: str,
#     province: str = Province.DEFAULT,
#     acquisition_after_july_2024: bool = True,
#     holding_years: int = None
# ) -> Dict[str, Any]:
#     """Convenience wrapper for single heir tax calculation."""
#     return calculate_full_tax_summary(
#         share_value_pkr=share_value_pkr,
#         full_property_value_pkr=full_property_value_pkr,
#         filer_status=filer_status,
#         action=action,
#         province=province,
#         acquisition_after_july_2024=acquisition_after_july_2024,
#         holding_years=holding_years
#     )



###################
# Alyan fixes and improvements
##################

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# """
# WarisNama AI — faraid_engine.py
# =================================

# Deterministic Faraid calculation engine.

# ✔ Sunni Hanafi (with MFLO 1961 §4)
# ✔ Shia Jafari
# ✔ Christian (Succession Act 1925)
# ✔ Hindu (Hindu Succession Act 1956 — Class I only)

# All calculations use Python Fractions for exact results.
# """

# from fractions import Fraction
# from typing import Dict, Any, List, Optional

# from core.knowledge_base import (
#     HANAFI_FIXED_SHARES,
#     HANAFI_MAHJUB,
#     apply_awl,
#     apply_hanafi_radd,
#     validate_estate,
#     fraction_to_display,
#     MFLO_PREDECEASED_SON_APPLIES,
#     SHIA_RULES,
#     CHRISTIAN_RULES,
#     HINDU_RULES,
#     REFERENCES
# )


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 1: HELPER FUNCTIONS
# # ═══════════════════════════════════════════════════════════════════════════════

# def _expand_heirs(heirs: Dict[str, int]) -> Dict[str, str]:
#     """
#     Expand heir counts into individual heir IDs.

#     Input:  {'sons': 2, 'daughters': 1}
#     Output: {'son_1': 'son', 'son_2': 'son', 'daughter_1': 'daughter'}
#     """
#     result = {}
#     for heir_type, count in heirs.items():
#         for i in range(count):
#             result[f"{heir_type}_{i+1}"] = heir_type
#     return result


# def _apply_mahjub(heirs: Dict[str, str]) -> Dict[str, str]:
#     """
#     Apply Hanafi Mahjub (exclusion/blocking) rules.
#     Removes heirs who are completely blocked by closer relatives.
#     """
#     active = dict(heirs)
#     heir_types = set(active.values())

#     for heir_id, heir_type in list(active.items()):
#         blockers = HANAFI_MAHJUB.get(heir_type, [])
#         if any(blocker in heir_types for blocker in blockers):
#             del active[heir_id]

#     return active


# def _fixed_shares_hanafi(heirs: Dict[str, str]) -> Dict[str, Fraction]:
#     """
#     Calculate fixed Quranic shares for Hanafi.
#     Does NOT include Asaba (residue) – that's handled separately.
#     """
#     shares = {}

#     has_son = any(h == "son" for h in heirs.values())
#     has_children = any(h in ["son", "daughter"] for h in heirs.values())
#     has_grandchildren = any(h in ["grandson", "granddaughter"] for h in heirs.values())
#     siblings = sum(1 for h in heirs.values() if "brother" in h or "sister" in h)

#     # ─── Wife/Wives ──────────────────────────────────────────────────────────
#     wives = [h for h in heirs if heirs[h] == "wife"]
#     if wives:
#         if has_children or has_grandchildren:
#             share = HANAFI_FIXED_SHARES["wife_with_children"]
#         else:
#             share = HANAFI_FIXED_SHARES["wife_no_children"]
#         per_wife = share / len(wives)
#         for wife in wives:
#             shares[wife] = per_wife

#     # ─── Husband ────────────────────────────────────────────────────────────
#     husbands = [h for h in heirs if heirs[h] == "husband"]
#     if husbands:
#         if has_children or has_grandchildren:
#             share = HANAFI_FIXED_SHARES["husband_with_children"]
#         else:
#             share = HANAFI_FIXED_SHARES["husband_no_children"]
#         shares[husbands[0]] = share

#     # ─── Mother ─────────────────────────────────────────────────────────────
#     mothers = [h for h in heirs if heirs[h] == "mother"]
#     if mothers:
#         if has_children or has_grandchildren or siblings >= 2:
#             share = HANAFI_FIXED_SHARES["mother_with_children"]
#         else:
#             share = HANAFI_FIXED_SHARES["mother_no_children_no_siblings"]
#         shares[mothers[0]] = share

#     # ─── Father (fixed portion only – residue handled separately) ───────────
#     fathers = [h for h in heirs if heirs[h] == "father"]
#     if fathers:
#         shares[fathers[0]] = HANAFI_FIXED_SHARES["father_fixed_minimum"]

#     # ─── Daughters (only when NO sons present) ──────────────────────────────
#     daughters = [h for h in heirs if heirs[h] == "daughter"]
#     if daughters and not has_son:
#         if len(daughters) == 1:
#             total = HANAFI_FIXED_SHARES["daughter_sole"]
#         else:
#             total = HANAFI_FIXED_SHARES["daughters_multiple"]
#         per_daughter = total / len(daughters)
#         for daughter in daughters:
#             shares[daughter] = per_daughter

#     return shares


# def _asaba_hanafi(
#     heirs: Dict[str, str],
#     shares: Dict[str, Fraction],
#     residue: Fraction
# ) -> Dict[str, Fraction]:
#     """
#     Distribute residue (Asaba) to agnatic heirs.
#     Priority: sons → father → paternal grandfather → brothers → etc.
#     """
#     if residue <= 0:
#         return shares

#     sons = [h for h in heirs if heirs[h] == "son"]
#     daughters = [h for h in heirs if heirs[h] == "daughter"]

#     # ─── Sons + Daughters (son gets double daughter) ────────────────────────
#     if sons:
#         units = len(sons) * 2 + len(daughters)
#         per_unit = residue / units

#         for son in sons:
#             shares[son] = shares.get(son, Fraction(0)) + per_unit * 2
#         for daughter in daughters:
#             shares[daughter] = shares.get(daughter, Fraction(0)) + per_unit

#         return shares

#     # ─── Father (as Asaba) ──────────────────────────────────────────────────
#     for heir_id, heir_type in heirs.items():
#         if heir_type == "father":
#             shares[heir_id] = shares.get(heir_id, Fraction(0)) + residue
#             return shares

#     # ─── Paternal Grandfather ───────────────────────────────────────────────
#     for heir_id, heir_type in heirs.items():
#         if heir_type == "paternal_grandfather":
#             shares[heir_id] = shares.get(heir_id, Fraction(0)) + residue
#             return shares

#     # ─── Full Brothers + Full Sisters ───────────────────────────────────────
#     brothers = [h for h in heirs if heirs[h] == "full_brother"]
#     sisters = [h for h in heirs if heirs[h] == "full_sister"]

#     if brothers:
#         units = len(brothers) * 2 + len(sisters)
#         per_unit = residue / units

#         for brother in brothers:
#             shares[brother] = shares.get(brother, Fraction(0)) + per_unit * 2
#         for sister in sisters:
#             shares[sister] = shares.get(sister, Fraction(0)) + per_unit

#     return shares


# def _apply_mflo_rule(
#     heirs_input: Dict[str, int],
#     total_estate: float,
#     distributable: float,
#     predeceased_sons: Optional[List[Dict]] = None
# ) -> Dict[str, Fraction]:
#     """
#     Apply MFLO 1961 Section 4: Predeceased son's children inherit his share.
#     This is the MOST CRITICAL rule for Pakistani inheritance.
#     """
#     shares = {}

#     if not MFLO_PREDECEASED_SON_APPLIES or not predeceased_sons:
#         return shares

#     living_sons = heirs_input.get("sons", 0)

#     # Each son (living or predeceased) gets equal share
#     total_son_units = living_sons + len(predeceased_sons)
#     if total_son_units == 0:
#         return shares

#     # The "son pool" share (will be filled by Asaba later)
#     # For now, we mark that grandchildren will inherit
#     for idx, predeceased in enumerate(predeceased_sons):
#         grandsons = predeceased.get("grandsons", 0)
#         granddaughters = predeceased.get("granddaughters", 0)

#         if grandsons + granddaughters == 0:
#             continue

#         # Predeceased son's share is 1/total_son_units of the residue
#         # We'll calculate actual amounts in the main function
#         pass

#     return shares


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 2: SUNNI HANAFI CALCULATION
# # ═══════════════════════════════════════════════════════════════════════════════

# def calculate_hanafi(
#     heirs_input: Dict[str, int],
#     total_estate: float,
#     debts: float = 0,
#     funeral: float = 0,
#     wasiyyat: float = 0,
#     predeceased_sons: Optional[List[Dict]] = None
# ) -> Dict[str, Any]:
#     """
#     Calculate inheritance shares under Sunni Hanafi law + MFLO 1961.

#     Args:
#         heirs_input: {'sons': 2, 'daughters': 3, 'wife': 1, ...}
#         total_estate: Gross estate value in PKR
#         debts: Outstanding debts
#         funeral: Funeral expenses
#         wasiyyat: Will amount (capped at 1/3 of net estate)
#         predeceased_sons: List of predeceased sons with their children

#     Returns:
#         Dict with 'distributable_estate', 'warning', and 'shares'
#     """
#     # Step 1: Validate estate and deduct debts/funeral
#     net_estate, warning = validate_estate(total_estate, debts, funeral)

#     if net_estate <= 0:
#         return {
#             "error": f"Estate exhausted after deductions. Net estate: PKR {net_estate:,.0f}",
#             "distributable_estate": 0,
#             "warning": warning,
#             "shares": {}
#         }

#     # Step 2: Cap Wasiyyat at 1/3 of net estate
#     max_wasiyyat = net_estate / 3
#     valid_wasiyyat = min(wasiyyat, max_wasiyyat)
#     distributable = net_estate - valid_wasiyyat

#     if wasiyyat > max_wasiyyat:
#         warning += f" Wasiyyat reduced from PKR {wasiyyat:,.0f} to PKR {valid_wasiyyat:,.0f} (max 1/3)."

#     # Step 3: Expand heirs and apply Mahjub
#     heirs = _expand_heirs(heirs_input)
#     heirs = _apply_mahjub(heirs)

#     # Step 4: Calculate fixed Quranic shares
#     shares = _fixed_shares_hanafi(heirs)

#     # Step 5: Apply Awl (proportional reduction if fixed shares exceed estate)
#     shares = apply_awl(shares)

#     # Step 6: Calculate residue and apply Asaba
#     total_fixed = sum(shares.values())
#     residue = Fraction(1, 1) - total_fixed

#     if residue > 0:
#         shares = _asaba_hanafi(heirs, shares, residue)

#     # Step 7: Apply Radd (return surplus to non-spouse Quranic heirs if no Asaba)
#     if residue > 0 and not any(h in ["son", "father", "full_brother"] for h in heirs.values()):
#         shares = apply_hanafi_radd(shares, heirs)

#     # Step 8: Convert fractions to monetary amounts
#     result_shares = {}
#     for heir_id, fraction in shares.items():
#         if fraction > 0:
#             result_shares[heir_id] = {
#                 "fraction": fraction_to_display(fraction),
#                 "amount": float(fraction * Fraction(distributable).limit_denominator()),
#                 "reference": REFERENCES.get("hanafi_asaba_children", "Hanafi Faraid rules")
#             }

#     # Step 9: Apply MFLO §4 for predeceased sons (simplified – add grandchildren as heirs)
#     if predeceased_sons and MFLO_PREDECEASED_SON_APPLIES:
#         # For MVP, we add grandchildren to the heirs list
#         grand_share = Fraction(1, len(predeceased_sons) + heirs_input.get("sons", 0))
#         for idx, son_data in enumerate(predeceased_sons):
#             grandsons = son_data.get("grandsons", 0)
#             granddaughters = son_data.get("granddaughters", 0)
#             if grandsons + granddaughters > 0:
#                 units = grandsons * 2 + granddaughters
#                 per_unit = grand_share / units
#                 for i in range(grandsons):
#                     heir_id = f"mflo_grandson_{idx+1}_{i+1}"
#                     result_shares[heir_id] = {
#                         "fraction": fraction_to_display(per_unit * 2),
#                         "amount": float(per_unit * 2 * Fraction(distributable).limit_denominator()),
#                         "reference": REFERENCES.get("hanafi_mflo_predeceased_son", "MFLO 1961 Section 4")
#                     }
#                 for i in range(granddaughters):
#                     heir_id = f"mflo_granddaughter_{idx+1}_{i+1}"
#                     result_shares[heir_id] = {
#                         "fraction": fraction_to_display(per_unit),
#                         "amount": float(per_unit * Fraction(distributable).limit_denominator()),
#                         "reference": REFERENCES.get("hanafi_mflo_predeceased_son", "MFLO 1961 Section 4")
#                     }

#     return {
#         "distributable_estate": distributable,
#         "warning": warning if warning else None,
#         "shares": result_shares
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 3: SHIA JAFARI CALCULATION
# # ═══════════════════════════════════════════════════════════════════════════════

# def calculate_shia(
#     heirs_input: Dict[str, int],
#     total_estate: float,
#     debts: float = 0,
#     funeral: float = 0,
#     wasiyyat: float = 0,
#     movable_estate: Optional[float] = None
# ) -> Dict[str, Any]:
#     """
#     Calculate inheritance shares under Shia Jafari law.

#     KEY DIFFERENCE: Wife does NOT inherit immovable property (land/buildings).
#     """
#     # For MVP, we use Hanafi logic but add Shia-specific notes
#     result = calculate_hanafi(heirs_input, total_estate, debts, funeral, wasiyyat)

#     if "error" in result:
#         return result

#     # Add Shia-specific notes for wife
#     for heir_id, data in result["shares"].items():
#         if heir_id.startswith("wife"):
#             data["reference"] = REFERENCES.get("shia_wife_no_land", "Shia Jafari rule: Wife excludes immovable property")
#             data["note"] = "Under Shia law, wife does NOT inherit land/buildings – only movable assets."

#     return result


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 4: CHRISTIAN CALCULATION (Succession Act 1925)
# # ═══════════════════════════════════════════════════════════════════════════════

# def calculate_christian(
#     heirs_input: Dict[str, int],
#     total_estate: float,
#     debts: float = 0,
#     funeral: float = 0
# ) -> Dict[str, Any]:
#     """
#     Calculate inheritance shares under Christian law (Succession Act 1925).

#     Key principles:
#     - NO gender discrimination (sons and daughters equal)
#     - Spouse gets 1/3 if children exist, otherwise full estate
#     """
#     net_estate, warning = validate_estate(total_estate, debts, funeral)

#     if net_estate <= 0:
#         return {
#             "error": f"Estate exhausted. Net: PKR {net_estate:,.0f}",
#             "shares": {}
#         }

#     spouse = heirs_input.get("spouse", 0)
#     children = heirs_input.get("children", 0)

#     shares = {}

#     if spouse and children:
#         spouse_share = Fraction(1, 3)
#         children_share = Fraction(2, 3)
#         per_child = children_share / children

#         shares["spouse"] = {
#             "fraction": fraction_to_display(spouse_share),
#             "amount": float(spouse_share * net_estate),
#             "reference": REFERENCES.get("christian_spouse_children", "Succession Act 1925, Section 33(c)")
#         }
#         for i in range(children):
#             shares[f"child_{i+1}"] = {
#                 "fraction": fraction_to_display(per_child),
#                 "amount": float(per_child * net_estate),
#                 "reference": REFERENCES.get("christian_spouse_children", "Succession Act 1925, Section 33(c)")
#             }

#     elif spouse and not children:
#         shares["spouse"] = {
#             "fraction": "Full estate",
#             "amount": float(net_estate),
#             "reference": REFERENCES.get("christian_spouse_only", "Succession Act 1925, Section 33(b)")
#         }

#     elif not spouse and children:
#         per_child = Fraction(1, 1) / children
#         for i in range(children):
#             shares[f"child_{i+1}"] = {
#                 "fraction": fraction_to_display(per_child),
#                 "amount": float(per_child * net_estate),
#                 "reference": REFERENCES.get("christian_children_only", "Succession Act 1925, Section 33(a)")
#             }

#     else:
#         return {"error": "No valid heirs (spouse or children required)", "shares": {}}

#     return {
#         "distributable_estate": net_estate,
#         "warning": warning if warning else None,
#         "shares": shares
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 5: HINDU CALCULATION (Hindu Succession Act 1956 – Class I only)
# # ═══════════════════════════════════════════════════════════════════════════════

# def calculate_hindu(
#     heirs_input: Dict[str, int],
#     total_estate: float,
#     debts: float = 0,
#     funeral: float = 0
# ) -> Dict[str, Any]:
#     """
#     Calculate inheritance shares under Hindu Succession Act 1956 (Class I only).

#     NOTE: For coparcenary/ancestral property, consult a lawyer.
#     """
#     net_estate, warning = validate_estate(total_estate, debts, funeral)

#     if net_estate <= 0:
#         return {
#             "error": f"Estate exhausted. Net: PKR {net_estate:,.0f}",
#             "shares": {}
#         }

#     # Class I heirs: widow, sons, daughters (all equal)
#     widow_count = heirs_input.get("widow", 0)
#     sons = heirs_input.get("sons", 0)
#     daughters = heirs_input.get("daughters", 0)

#     total_class_I = widow_count + sons + daughters

#     if total_class_I == 0:
#         return {
#             "error": "No Class I heirs found. For Class II or coparcenary property, please consult a lawyer.",
#             "shares": {},
#             "warning": HINDU_RULES.get("coparcenary_mvp_note", "")
#         }

#     per_heir = Fraction(1, 1) / total_class_I

#     shares = {}

#     if widow_count:
#         shares["widow"] = {
#             "fraction": fraction_to_display(per_heir),
#             "amount": float(per_heir * net_estate),
#             "reference": REFERENCES.get("hindu_class_I", "Hindu Succession Act 1956, Class I")
#         }

#     for i in range(sons):
#         shares[f"son_{i+1}"] = {
#             "fraction": fraction_to_display(per_heir),
#             "amount": float(per_heir * net_estate),
#             "reference": REFERENCES.get("hindu_class_I", "Hindu Succession Act 1956, Class I")
#         }

#     for i in range(daughters):
#         shares[f"daughter_{i+1}"] = {
#             "fraction": fraction_to_display(per_heir),
#             "amount": float(per_heir * net_estate),
#             "reference": REFERENCES.get("hindu_class_I", "Hindu Succession Act 1956, Class I")
#         }

#     return {
#         "distributable_estate": net_estate,
#         "warning": warning if warning else HINDU_RULES.get("coparcenary_mvp_note", ""),
#         "shares": shares
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 6: MAIN DISPATCHER
# # ═══════════════════════════════════════════════════════════════════════════════

# def calculate_shares(
#     sect: str,
#     heirs: Dict[str, int],
#     total_estate: float,
#     debts: float = 0,
#     funeral: float = 0,
#     wasiyyat: float = 0,
#     **kwargs
# ) -> Dict[str, Any]:
#     """
#     Main dispatcher for inheritance calculation across all sects.

#     Args:
#         sect: 'hanafi', 'shia', 'christian', or 'hindu'
#         heirs: Dictionary of heir types and counts
#         total_estate: Gross estate value in PKR
#         debts: Outstanding debts
#         funeral: Funeral expenses
#         wasiyyat: Will amount (capped at 1/3 of net estate)
#         **kwargs: Additional sect-specific parameters

#     Returns:
#         Dict with 'distributable_estate', 'warning', and 'shares'
#     """
#     if sect == "hanafi":
#         return calculate_hanafi(
#             heirs, total_estate, debts, funeral, wasiyyat,
#             predeceased_sons=kwargs.get("predeceased_sons")
#         )
#     elif sect == "shia":
#         return calculate_shia(
#             heirs, total_estate, debts, funeral, wasiyyat,
#             movable_estate=kwargs.get("movable_estate")
#         )
#     elif sect == "christian":
#         return calculate_christian(heirs, total_estate, debts, funeral)
#     elif sect == "hindu":
#         return calculate_hindu(heirs, total_estate, debts, funeral)
#     else:
#         return {"error": f"Unknown sect: {sect}", "shares": {}}
    




#########################
# Verion 3
#######################

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — tax_engine.py
=================================
Thin orchestration layer over knowledge_base tax system.

All tax calculations MUST come from knowledge_base to ensure:
✔ Legal accuracy (FBR 2025)
✔ No duplication
✔ Consistency across modules
"""

from typing import Dict, Any

from core.knowledge_base import (
    calculate_full_tax_summary,
    FilerStatus,
    Province
)


# ─────────────────────────────────────────────
# Single Heir Tax Calculation
# ─────────────────────────────────────────────
def calculate_heir_tax(
    share_value_pkr: float,
    full_property_value_pkr: float,
    filer_status: str,
    action: str,
    province: str = Province.DEFAULT,
    acquisition_after_july_2024: bool = True,
    holding_years: int = None
) -> Dict[str, Any]:
    """
    Calculate ALL taxes for a single heir.

    Args:
        share_value_pkr         : Heir's share value
        full_property_value_pkr : FULL property value (CRITICAL for tax brackets)
        filer_status            : 'filer', 'late_filer', 'non_filer'
        action                  : 'sell', 'hold', 'buyout'
        province                : Province for stamp duty
        acquisition_after_july_2024 : CGT rule selector
        holding_years           : Needed for pre-2024 CGT

    Returns:
        Complete tax breakdown dict
    """
    return calculate_full_tax_summary(
        share_value_pkr=share_value_pkr,
        full_property_value_pkr=full_property_value_pkr,
        filer_status=filer_status,
        action=action,
        province=province,
        acquisition_after_july_2024=acquisition_after_july_2024,
        holding_years=holding_years
    )


# ─────────────────────────────────────────────
# Multi-Heir Tax Calculation
# ─────────────────────────────────────────────
def calculate_all_heirs_tax(
    heirs_shares: Dict[str, Dict],
    filer_status_map: Dict[str, str],
    full_property_value_pkr: float,
    action: str = "sell",
    province: str = Province.DEFAULT,
    acquisition_after_july_2024: bool = True,
    holding_years: int = None
) -> Dict[str, Dict]:
    """
    Calculate taxes for ALL heirs.

    Args:
        heirs_shares: {
            heir_id: {
                'amount': float,
                ...
            }
        }
        filer_status_map: {
            heir_id: 'filer' / 'late_filer' / 'non_filer'
        }
        full_property_value_pkr: FULL estate/property value
        action: 'sell', 'hold', 'buyout'
        province: Province
        acquisition_after_july_2024: CGT rule
        holding_years: for pre-2024 CGT

    Returns:
        Dict of heir_id → tax breakdown
    """
    results = {}

    for heir_id, data in heirs_shares.items():
        share_value = data.get("amount", 0.0)
        filer_status = filer_status_map.get(heir_id, FilerStatus.NON_FILER)

        results[heir_id] = calculate_heir_tax(
            share_value_pkr=share_value,
            full_property_value_pkr=full_property_value_pkr,
            filer_status=filer_status,
            action=action,
            province=province,
            acquisition_after_july_2024=acquisition_after_july_2024,
            holding_years=holding_years
        )

    return results





















































