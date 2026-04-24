# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# from fractions import Fraction
# from typing import Dict, Any, List

# from core.knowledge_base import (
#     HANAFI_FIXED_SHARES,
#     HANAFI_MAHJUB,
#     apply_awl,
#     apply_hanafi_radd,
#     validate_estate,
#     fraction_to_display,
#     MFLO_PREDECEASED_SON_APPLIES
# )

# # ─────────────────────────────────────────────
# # Expand heirs
# # ─────────────────────────────────────────────
# def _expand_heirs(heirs: Dict[str, int]) -> Dict[str, str]:
#     result = {}
#     for h, count in heirs.items():
#         for i in range(count):
#             result[f"{h}_{i+1}"] = h
#     return result


# # ─────────────────────────────────────────────
# # Apply Mahjub
# # ─────────────────────────────────────────────
# def _apply_mahjub(heirs: Dict[str, str]) -> Dict[str, str]:
#     active = dict(heirs)
#     types = set(active.values())

#     for hid, htype in list(active.items()):
#         blockers = HANAFI_MAHJUB.get(htype, [])
#         if any(b in types for b in blockers):
#             del active[hid]

#     return active


# # ─────────────────────────────────────────────
# # Fixed Shares
# # ─────────────────────────────────────────────
# def _fixed_shares(heirs: Dict[str, str]) -> Dict[str, Fraction]:
#     shares = {}

#     has_son = any(h == "son" for h in heirs.values())
#     has_children = any(h in ["son", "daughter"] for h in heirs.values())
#     siblings = sum(1 for h in heirs.values() if "brother" in h or "sister" in h)

#     # Wife
#     wives = [h for h in heirs if heirs[h] == "wife"]
#     if wives:
#         share = HANAFI_FIXED_SHARES[
#             "wife_with_children" if has_children else "wife_no_children"
#         ]
#         per = share / len(wives)
#         for w in wives:
#             shares[w] = per

#     # Husband
#     husbands = [h for h in heirs if heirs[h] == "husband"]
#     if husbands:
#         share = HANAFI_FIXED_SHARES[
#             "husband_with_children" if has_children else "husband_no_children"
#         ]
#         shares[husbands[0]] = share

#     # Mother
#     mothers = [h for h in heirs if heirs[h] == "mother"]
#     if mothers:
#         if has_children or siblings >= 2:
#             share = HANAFI_FIXED_SHARES["mother_with_children"]
#         else:
#             share = HANAFI_FIXED_SHARES["mother_no_children_no_siblings"]
#         shares[mothers[0]] = share

#     # Father initial
#     fathers = [h for h in heirs if heirs[h] == "father"]
#     if fathers:
#         shares[fathers[0]] = HANAFI_FIXED_SHARES["father_fixed_minimum"]

#     # Daughters (no sons)
#     daughters = [h for h in heirs if heirs[h] == "daughter"]
#     if daughters and not has_son:
#         total = (
#             HANAFI_FIXED_SHARES["daughter_sole"]
#             if len(daughters) == 1
#             else HANAFI_FIXED_SHARES["daughters_multiple"]
#         )
#         per = total / len(daughters)
#         for d in daughters:
#             shares[d] = per

#     return shares


# # ─────────────────────────────────────────────
# # MFLO §4 Implementation
# # ─────────────────────────────────────────────
# def _apply_mflo(
#     heirs: Dict[str, str],
#     shares: Dict[str, Fraction],
#     predeceased_sons: List[Dict]
# ):
#     if not MFLO_PREDECEASED_SON_APPLIES or not predeceased_sons:
#         return heirs, shares

#     # Treat each predeceased son as a "virtual son"
#     count_existing_sons = sum(1 for h in heirs.values() if h == "son")
#     total_units = count_existing_sons + len(predeceased_sons)

#     # Each son unit share
#     unit_share = Fraction(1, total_units)

#     # Distribute each predeceased son's share to his children
#     for idx, pdata in enumerate(predeceased_sons):
#         children = pdata.get("children", {})
#         gsons = children.get("grandson", 0)
#         gdaughters = children.get("granddaughter", 0)

#         if gsons + gdaughters == 0:
#             continue

#         units = gsons * 2 + gdaughters
#         per_unit = unit_share / units

#         for i in range(gsons):
#             shares[f"mflo_grandson_{idx+1}_{i+1}"] = per_unit * 2
#         for i in range(gdaughters):
#             shares[f"mflo_granddaughter_{idx+1}_{i+1}"] = per_unit

#     return heirs, shares


# # ─────────────────────────────────────────────
# # Asaba
# # ─────────────────────────────────────────────
# def _asaba(heirs, shares, residue):
#     if residue <= 0:
#         return shares

#     sons = [h for h in heirs if heirs[h] == "son"]
#     daughters = [h for h in heirs if heirs[h] == "daughter"]

#     # Sons
#     if sons:
#         units = len(sons) * 2 + len(daughters)
#         unit = residue / units

#         for s in sons:
#             shares[s] = unit * 2
#         for d in daughters:
#             shares[d] = unit

#         return shares

#     # Father
#     for hid, htype in heirs.items():
#         if htype == "father":
#             shares[hid] = shares.get(hid, Fraction(0)) + residue
#             return shares

#     # Grandfather
#     for hid, htype in heirs.items():
#         if htype == "paternal_grandfather":
#             shares[hid] = shares.get(hid, Fraction(0)) + residue
#             return shares

#     # Brothers
#     brothers = [h for h in heirs if heirs[h] == "full_brother"]
#     sisters = [h for h in heirs if heirs[h] == "full_sister"]

#     if brothers:
#         units = len(brothers) * 2 + len(sisters)
#         unit = residue / units

#         for b in brothers:
#             shares[b] = unit * 2
#         for s in sisters:
#             shares[s] = unit

#     return shares


# # ─────────────────────────────────────────────
# # MAIN ENGINE
# # ─────────────────────────────────────────────
# def calculate_hanafi(
#     heirs_input: Dict[str, int],
#     total_estate: float,
#     debts: float = 0,
#     funeral: float = 0,
#     wasiyyat: float = 0,
#     predeceased_sons: List[Dict] = None
# ) -> Dict[str, Any]:

#     # Estate
#     distributable, warning = validate_estate(total_estate, debts, funeral)
#     wasiyyat_cap = min(wasiyyat, distributable / 3)
#     distributable -= wasiyyat_cap

#     # Expand
#     heirs = _expand_heirs(heirs_input)

#     # Mahjub
#     heirs = _apply_mahjub(heirs)

#     # Fixed
#     shares = _fixed_shares(heirs)

#     # MFLO
#     heirs, shares = _apply_mflo(heirs, shares, predeceased_sons or [])

#     # Awl
#     shares = apply_awl(shares)

#     # Residue
#     total = sum(shares.values())
#     residue = Fraction(1) - total

#     # Asaba
#     shares = _asaba(heirs, shares, residue)

#     # Radd
#     shares = apply_hanafi_radd(shares, heirs)

#     # Output
#     result = {}
#     for hid, frac in shares.items():
#         result[hid] = {
#             "fraction": fraction_to_display(frac),
#             "amount": float(frac * distributable)
#         }

#     return {
#         "distributable_estate": distributable,
#         "warning": warning,
#         "shares": result
#     }


# # ─────────────────────────────────────────────
# # ENTRY
# # ─────────────────────────────────────────────
# def calculate_shares(sect, heirs, total_estate, **kwargs):
#     if sect == "hanafi":
#         return calculate_hanafi(heirs, total_estate, **kwargs)

#     return {"error": "Other sects plug-in pending (engine ready)"}



#########################
# Alyan's fixes
#########################

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
#                 "amount": float(fraction * distributable),
#                 "reference": REFERENCES.get("hanafi_asaba_children", "Hanafi Faraid rules")
#             }

#     # Step 9: Apply MFLO §4 for predeceased sons (simplified – add grandchildren as heirs)
#     if predeceased_sons and MFLO_PREDECEASED_SON_APPLIES:
#         living_sons = heirs_input.get("sons", 0)
#         total_son_units = living_sons + len(predeceased_sons)
        
#         if total_son_units > 0:
#             grand_share = Fraction(1, total_son_units)
            
#             for idx, son_data in enumerate(predeceased_sons):
#                 grandsons = son_data.get("grandsons", 0)
#                 granddaughters = son_data.get("granddaughters", 0)
                
#                 if grandsons + granddaughters > 0:
#                     units = grandsons * 2 + granddaughters
#                     per_unit = grand_share / units
                    
#                     for i in range(grandsons):
#                         heir_id = f"mflo_grandson_{idx+1}_{i+1}"
#                         result_shares[heir_id] = {
#                             "fraction": fraction_to_display(per_unit * 2),
#                             "amount": float(per_unit * 2 * distributable),
#                             "reference": REFERENCES.get("hanafi_mflo_predeceased_son", "MFLO 1961 Section 4")
#                         }
#                     for i in range(granddaughters):
#                         heir_id = f"mflo_granddaughter_{idx+1}_{i+1}"
#                         result_shares[heir_id] = {
#                             "fraction": fraction_to_display(per_unit),
#                             "amount": float(per_unit * distributable),
#                             "reference": REFERENCES.get("hanafi_mflo_predeceased_son", "MFLO 1961 Section 4")
#                         }

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
#     new_shares = {}
#     for heir_id, data in result["shares"].items():
#         new_shares[heir_id] = data.copy()
#         if heir_id.startswith("wife"):
#             new_shares[heir_id]["reference"] = REFERENCES.get("shia_wife_no_land", "Shia Jafari rule: Wife excludes immovable property")
#             new_shares[heir_id]["note"] = "Under Shia law, wife does NOT inherit land/buildings – only movable assets."
    
#     result["shares"] = new_shares
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
#             "distributable_estate": 0,
#             "warning": warning,
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
#         return {
#             "error": "No valid heirs (spouse or children required)",
#             "distributable_estate": net_estate,
#             "warning": warning,
#             "shares": {}
#         }

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
#             "distributable_estate": 0,
#             "warning": warning,
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
#             "distributable_estate": net_estate,
#             "warning": HINDU_RULES.get("coparcenary_mvp_note", ""),
#             "shares": {}
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
#         return {"error": f"Unknown sect: {sect}", "distributable_estate": 0, "warning": None, "shares": {}}

































######################3
# Version 3
##########################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — faraid_engine.py
Fixed version - properly handles all heirs
"""

from fractions import Fraction
from typing import Dict, Any, List, Optional

from core.knowledge_base import (
    HANAFI_FIXED_SHARES,
    HANAFI_MAHJUB,
    apply_awl,
    apply_hanafi_radd,
    validate_estate,
    fraction_to_display,
    MFLO_PREDECEASED_SON_APPLIES
)

# Safe REFERENCES fallback
try:
    from core.knowledge_base import REFERENCES
except ImportError:
    REFERENCES = {
        "hanafi_asaba_children": "Hanafi Faraid rules: Sons get double daughters' share",
        "hanafi_mflo_predeceased_son": "MFLO 1961 Section 4",
        "shia_wife_no_land": "Shia: Wife excludes immovable property",
        "christian_spouse_children": "Succession Act 1925, Section 33(c)",
        "christian_spouse_only": "Succession Act 1925, Section 33(b)",
        "christian_children_only": "Succession Act 1925, Section 33(a)",
        "hindu_class_I": "Hindu Succession Act 1956, Class I"
    }


def calculate_hanafi(
    heirs_input: Dict[str, int],
    total_estate: float,
    debts: float = 0,
    funeral: float = 0,
    wasiyyat: float = 0
) -> Dict[str, Any]:
    """
    Calculate Hanafi inheritance shares.
    
    heirs_input format: {'sons': 2, 'daughters': 3, 'wife': 1, 'husband': 0, 'mother': 0, 'father': 0}
    """
    # Step 1: Calculate net estate
    net_estate, warning = validate_estate(total_estate, debts, funeral)
    
    if net_estate <= 0:
        return {
            "error": f"Estate exhausted: PKR {net_estate:,.0f}",
            "distributable_estate": 0,
            "warning": warning,
            "shares": {}
        }
    
    # Step 2: Cap Wasiyyat at 1/3
    max_wasiyyat = net_estate / 3
    valid_wasiyyat = min(wasiyyat, max_wasiyyat)
    distributable = net_estate - valid_wasiyyat
    
    # Step 3: Get heir counts
    sons = heirs_input.get('sons', 0)
    daughters = heirs_input.get('daughters', 0)
    wives = heirs_input.get('wife', 0)
    husband = heirs_input.get('husband', 0)
    mother = heirs_input.get('mother', 0)
    father = heirs_input.get('father', 0)
    
    has_children = (sons + daughters) > 0
    
    # Step 4: Calculate fixed shares
    shares = {}
    fixed_total = Fraction(0, 1)
    
    # ─── Wife/Wives ─────────────────────────────────────────
    if wives > 0:
        if has_children:
            wife_share = HANAFI_FIXED_SHARES["wife_with_children"]  # 1/8
        else:
            wife_share = HANAFI_FIXED_SHARES["wife_no_children"]    # 1/4
        per_wife = wife_share / wives
        for i in range(wives):
            heir_id = f"wife_{i+1}"
            shares[heir_id] = per_wife
        fixed_total += wife_share
    
    # ─── Husband ────────────────────────────────────────────
    if husband > 0:
        if has_children:
            husband_share = HANAFI_FIXED_SHARES["husband_with_children"]  # 1/4
        else:
            husband_share = HANAFI_FIXED_SHARES["husband_no_children"]    # 1/2
        shares["husband"] = husband_share
        fixed_total += husband_share
    
    # ─── Mother ─────────────────────────────────────────────
    if mother > 0:
        # Check siblings for mother's share reduction
        siblings = heirs_input.get('brothers', 0) + heirs_input.get('sisters', 0)
        if has_children or siblings >= 2:
            mother_share = HANAFI_FIXED_SHARES["mother_with_children"]  # 1/6
        else:
            mother_share = HANAFI_FIXED_SHARES["mother_no_children_no_siblings"]  # 1/3
        shares["mother"] = mother_share
        fixed_total += mother_share
    
    # ─── Father ─────────────────────────────────────────────
    if father > 0:
        father_share = HANAFI_FIXED_SHARES["father_fixed_minimum"]  # 1/6
        shares["father"] = father_share
        fixed_total += father_share
    
    # ─── Daughters (fixed share only when no sons) ──────────
    if sons == 0 and daughters > 0:
        if daughters == 1:
            daughter_share = HANAFI_FIXED_SHARES["daughter_sole"]  # 1/2
        else:
            daughter_share = HANAFI_FIXED_SHARES["daughters_multiple"]  # 2/3
        per_daughter = daughter_share / daughters
        for i in range(daughters):
            heir_id = f"daughter_{i+1}"
            shares[heir_id] = per_daughter
        fixed_total += daughter_share
    
    # Step 5: Calculate residue and distribute to sons/daughters (Asaba)
    residue = Fraction(1, 1) - fixed_total
    
    if residue > 0 and (sons > 0 or (sons == 0 and daughters > 0)):
        if sons > 0:
            # Sons and daughters share residue (son gets double)
            total_units = (sons * 2) + daughters
            per_unit = residue / total_units
            
            # Distribute to sons
            for i in range(sons):
                heir_id = f"son_{i+1}"
                son_share = per_unit * 2
                shares[heir_id] = shares.get(heir_id, Fraction(0)) + son_share
            
            # Distribute to daughters (when sons exist, they get residue, not fixed)
            for i in range(daughters):
                heir_id = f"daughter_{i+1}"
                daughter_share = per_unit
                shares[heir_id] = daughter_share
        
        elif sons == 0 and daughters > 0:
            # Only daughters - they already got fixed shares
            # Residue goes back to daughters via Radd
            pass
    
    # Step 6: Apply Radd if needed (surplus returns to heirs)
    total_shares = sum(shares.values())
    if total_shares < Fraction(1, 1):
        surplus = Fraction(1, 1) - total_shares
        # Distribute surplus to non-spouse heirs proportionally
        eligible = {k: v for k, v in shares.items() 
                   if not k.startswith('wife') and k != 'husband'}
        if eligible:
            eligible_total = sum(eligible.values())
            for heir_id in eligible:
                ratio = eligible[heir_id] / eligible_total
                shares[heir_id] = shares[heir_id] + (surplus * ratio)
    
    # Step 7: Convert to output format
    result_shares = {}
    for heir_id, fraction in shares.items():
        if fraction > 0:
            amount = float(fraction * Fraction(distributable).limit_denominator())
            result_shares[heir_id] = {
                "fraction": fraction_to_display(fraction),
                "amount": amount,
                "reference": REFERENCES.get("hanafi_asaba_children", "Hanafi Faraid rules")
            }
    
    return {
        "distributable_estate": distributable,
        "warning": warning if warning else None,
        "shares": result_shares
    }


def calculate_shia(
    heirs_input: Dict[str, int],
    total_estate: float,
    debts: float = 0,
    funeral: float = 0,
    wasiyyat: float = 0
) -> Dict[str, Any]:
    """Shia Jafari calculation - wife excludes land."""
    result = calculate_hanafi(heirs_input, total_estate, debts, funeral, wasiyyat)
    if "error" in result:
        return result
    
    # Add Shia note for wife
    for heir_id, data in result["shares"].items():
        if heir_id.startswith("wife"):
            data["reference"] = REFERENCES.get("shia_wife_no_land", "Shia: Wife excludes land")
            data["note"] = "Under Shia law, wife does not inherit land/buildings"
    
    return result


def calculate_christian(
    heirs_input: Dict[str, int],
    total_estate: float,
    debts: float = 0,
    funeral: float = 0
) -> Dict[str, Any]:
    """Christian inheritance (Succession Act 1925)."""
    net_estate, warning = validate_estate(total_estate, debts, funeral)
    
    if net_estate <= 0:
        return {"error": f"Estate exhausted: PKR {net_estate:,.0f}", "shares": {}}
    
    spouse = heirs_input.get('spouse', 0)
    children = heirs_input.get('children', 0)
    shares = {}
    
    if spouse and children:
        spouse_share = Fraction(1, 3)
        per_child = Fraction(2, 3) / children
        shares["spouse"] = {
            "fraction": fraction_to_display(spouse_share),
            "amount": float(spouse_share * net_estate),
            "reference": REFERENCES.get("christian_spouse_children", "Succession Act 1925")
        }
        for i in range(children):
            shares[f"child_{i+1}"] = {
                "fraction": fraction_to_display(per_child),
                "amount": float(per_child * net_estate),
                "reference": REFERENCES.get("christian_spouse_children", "Succession Act 1925")
            }
    elif spouse and not children:
        shares["spouse"] = {
            "fraction": "Full estate",
            "amount": float(net_estate),
            "reference": REFERENCES.get("christian_spouse_only", "Succession Act 1925")
        }
    elif not spouse and children:
        per_child = Fraction(1, 1) / children
        for i in range(children):
            shares[f"child_{i+1}"] = {
                "fraction": fraction_to_display(per_child),
                "amount": float(per_child * net_estate),
                "reference": REFERENCES.get("christian_children_only", "Succession Act 1925")
            }
    else:
        return {"error": "No valid heirs", "shares": {}}
    
    return {
        "distributable_estate": net_estate,
        "warning": warning if warning else None,
        "shares": shares
    }


def calculate_hindu(
    heirs_input: Dict[str, int],
    total_estate: float,
    debts: float = 0,
    funeral: float = 0
) -> Dict[str, Any]:
    """Hindu inheritance (Class I only)."""
    net_estate, warning = validate_estate(total_estate, debts, funeral)
    
    if net_estate <= 0:
        return {"error": f"Estate exhausted: PKR {net_estate:,.0f}", "shares": {}}
    
    widow = heirs_input.get('widow', 0)
    sons = heirs_input.get('sons', 0)
    daughters = heirs_input.get('daughters', 0)
    
    total_heirs = widow + sons + daughters
    
    if total_heirs == 0:
        return {"error": "No Class I heirs found", "shares": {}}
    
    per_heir = Fraction(1, 1) / total_heirs
    shares = {}
    ref = REFERENCES.get("hindu_class_I", "Hindu Succession Act 1956")
    
    if widow:
        shares["widow"] = {
            "fraction": fraction_to_display(per_heir),
            "amount": float(per_heir * net_estate),
            "reference": ref
        }
    for i in range(sons):
        shares[f"son_{i+1}"] = {
            "fraction": fraction_to_display(per_heir),
            "amount": float(per_heir * net_estate),
            "reference": ref
        }
    for i in range(daughters):
        shares[f"daughter_{i+1}"] = {
            "fraction": fraction_to_display(per_heir),
            "amount": float(per_heir * net_estate),
            "reference": ref
        }
    
    return {
        "distributable_estate": net_estate,
        "warning": warning if warning else None,
        "shares": shares
    }


def calculate_shares(
    sect: str,
    heirs: Dict[str, int],
    total_estate: float,
    debts: float = 0,
    funeral: float = 0,
    wasiyyat: float = 0,
    **kwargs
) -> Dict[str, Any]:
    """Main dispatcher for inheritance calculation."""
    
    if sect == "hanafi":
        return calculate_hanafi(heirs, total_estate, debts, funeral, wasiyyat)
    elif sect == "shia":
        return calculate_shia(heirs, total_estate, debts, funeral, wasiyyat)
    elif sect == "christian":
        return calculate_christian(heirs, total_estate, debts, funeral)
    elif sect == "hindu":
        return calculate_hindu(heirs, total_estate, debts, funeral)
    else:
        return {"error": f"Unknown sect: {sect}", "shares": {}}
    
















