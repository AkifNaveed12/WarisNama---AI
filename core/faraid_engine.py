#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fractions import Fraction
from typing import Dict, Any, List

from core.knowledge_base import (
    HANAFI_FIXED_SHARES,
    HANAFI_MAHJUB,
    apply_awl,
    apply_hanafi_radd,
    validate_estate,
    fraction_to_display,
    MFLO_PREDECEASED_SON_APPLIES
)

# ─────────────────────────────────────────────
# Expand heirs
# ─────────────────────────────────────────────
def _expand_heirs(heirs: Dict[str, int]) -> Dict[str, str]:
    result = {}
    for h, count in heirs.items():
        for i in range(count):
            result[f"{h}_{i+1}"] = h
    return result


# ─────────────────────────────────────────────
# Apply Mahjub
# ─────────────────────────────────────────────
def _apply_mahjub(heirs: Dict[str, str]) -> Dict[str, str]:
    active = dict(heirs)
    types = set(active.values())

    for hid, htype in list(active.items()):
        blockers = HANAFI_MAHJUB.get(htype, [])
        if any(b in types for b in blockers):
            del active[hid]

    return active


# ─────────────────────────────────────────────
# Fixed Shares
# ─────────────────────────────────────────────
def _fixed_shares(heirs: Dict[str, str]) -> Dict[str, Fraction]:
    shares = {}

    has_son = any(h == "son" for h in heirs.values())
    has_children = any(h in ["son", "daughter"] for h in heirs.values())
    siblings = sum(1 for h in heirs.values() if "brother" in h or "sister" in h)

    # Wife
    wives = [h for h in heirs if heirs[h] == "wife"]
    if wives:
        share = HANAFI_FIXED_SHARES[
            "wife_with_children" if has_children else "wife_no_children"
        ]
        per = share / len(wives)
        for w in wives:
            shares[w] = per

    # Husband
    husbands = [h for h in heirs if heirs[h] == "husband"]
    if husbands:
        share = HANAFI_FIXED_SHARES[
            "husband_with_children" if has_children else "husband_no_children"
        ]
        shares[husbands[0]] = share

    # Mother
    mothers = [h for h in heirs if heirs[h] == "mother"]
    if mothers:
        if has_children or siblings >= 2:
            share = HANAFI_FIXED_SHARES["mother_with_children"]
        else:
            share = HANAFI_FIXED_SHARES["mother_no_children_no_siblings"]
        shares[mothers[0]] = share

    # Father initial
    fathers = [h for h in heirs if heirs[h] == "father"]
    if fathers:
        shares[fathers[0]] = HANAFI_FIXED_SHARES["father_fixed_minimum"]

    # Daughters (no sons)
    daughters = [h for h in heirs if heirs[h] == "daughter"]
    if daughters and not has_son:
        total = (
            HANAFI_FIXED_SHARES["daughter_sole"]
            if len(daughters) == 1
            else HANAFI_FIXED_SHARES["daughters_multiple"]
        )
        per = total / len(daughters)
        for d in daughters:
            shares[d] = per

    return shares


# ─────────────────────────────────────────────
# MFLO §4 Implementation
# ─────────────────────────────────────────────
def _apply_mflo(
    heirs: Dict[str, str],
    shares: Dict[str, Fraction],
    predeceased_sons: List[Dict]
):
    if not MFLO_PREDECEASED_SON_APPLIES or not predeceased_sons:
        return heirs, shares

    # Treat each predeceased son as a "virtual son"
    count_existing_sons = sum(1 for h in heirs.values() if h == "son")
    total_units = count_existing_sons + len(predeceased_sons)

    # Each son unit share
    unit_share = Fraction(1, total_units)

    # Distribute each predeceased son's share to his children
    for idx, pdata in enumerate(predeceased_sons):
        children = pdata.get("children", {})
        gsons = children.get("grandson", 0)
        gdaughters = children.get("granddaughter", 0)

        if gsons + gdaughters == 0:
            continue

        units = gsons * 2 + gdaughters
        per_unit = unit_share / units

        for i in range(gsons):
            shares[f"mflo_grandson_{idx+1}_{i+1}"] = per_unit * 2
        for i in range(gdaughters):
            shares[f"mflo_granddaughter_{idx+1}_{i+1}"] = per_unit

    return heirs, shares


# ─────────────────────────────────────────────
# Asaba
# ─────────────────────────────────────────────
def _asaba(heirs, shares, residue):
    if residue <= 0:
        return shares

    sons = [h for h in heirs if heirs[h] == "son"]
    daughters = [h for h in heirs if heirs[h] == "daughter"]

    # Sons
    if sons:
        units = len(sons) * 2 + len(daughters)
        unit = residue / units

        for s in sons:
            shares[s] = unit * 2
        for d in daughters:
            shares[d] = unit

        return shares

    # Father
    for hid, htype in heirs.items():
        if htype == "father":
            shares[hid] = shares.get(hid, Fraction(0)) + residue
            return shares

    # Grandfather
    for hid, htype in heirs.items():
        if htype == "paternal_grandfather":
            shares[hid] = shares.get(hid, Fraction(0)) + residue
            return shares

    # Brothers
    brothers = [h for h in heirs if heirs[h] == "full_brother"]
    sisters = [h for h in heirs if heirs[h] == "full_sister"]

    if brothers:
        units = len(brothers) * 2 + len(sisters)
        unit = residue / units

        for b in brothers:
            shares[b] = unit * 2
        for s in sisters:
            shares[s] = unit

    return shares


# ─────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────
def calculate_hanafi(
    heirs_input: Dict[str, int],
    total_estate: float,
    debts: float = 0,
    funeral: float = 0,
    wasiyyat: float = 0,
    predeceased_sons: List[Dict] = None
) -> Dict[str, Any]:

    # Estate
    distributable, warning = validate_estate(total_estate, debts, funeral)
    wasiyyat_cap = min(wasiyyat, distributable / 3)
    distributable -= wasiyyat_cap

    # Expand
    heirs = _expand_heirs(heirs_input)

    # Mahjub
    heirs = _apply_mahjub(heirs)

    # Fixed
    shares = _fixed_shares(heirs)

    # MFLO
    heirs, shares = _apply_mflo(heirs, shares, predeceased_sons or [])

    # Awl
    shares = apply_awl(shares)

    # Residue
    total = sum(shares.values())
    residue = Fraction(1) - total

    # Asaba
    shares = _asaba(heirs, shares, residue)

    # Radd
    shares = apply_hanafi_radd(shares, heirs)

    # Output
    result = {}
    for hid, frac in shares.items():
        result[hid] = {
            "fraction": fraction_to_display(frac),
            "amount": float(frac * distributable)
        }

    return {
        "distributable_estate": distributable,
        "warning": warning,
        "shares": result
    }


# ─────────────────────────────────────────────
# ENTRY
# ─────────────────────────────────────────────
def calculate_shares(sect, heirs, total_estate, **kwargs):
    if sect == "hanafi":
        return calculate_hanafi(heirs, total_estate, **kwargs)

    return {"error": "Other sects plug-in pending (engine ready)"}