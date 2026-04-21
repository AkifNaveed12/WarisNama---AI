#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Faraid Calculation Engine – uses knowledge_base.py to compute exact shares.
Handles Sunni Hanafi, Shia Jafari, Christian, and Hindu (basic) rules.
All calculations use Python fractions for exact results.
"""

from fractions import Fraction
from typing import Dict, Any
from knowledge_base import (
    HANAFI_FIXED_SHARES, MFLO_PREDECEASED_SON_RULE,
    SHIA_RULES, CHRISTIAN_RULES, HINDU_RULES, REFERENCES
)

def _distribute_residue_children(residue: Fraction, sons: int, daughters: int) -> Dict[str, Fraction]:
    shares = {}
    if sons + daughters == 0:
        return shares
    units = sons * 2 + daughters
    per_unit = residue / units
    if sons > 0:
        shares['son'] = per_unit * 2
    if daughters > 0:
        shares['daughter'] = per_unit
    return shares

def calculate_hanafi(heirs: Dict[str, int], total_estate: float, debts: float = 0, wasiyyat: float = 0) -> Dict[str, Dict]:
    distributable = total_estate - debts - min(wasiyyat, total_estate * 1/3)
    if distributable <= 0:
        return {"error": "Estate exhausted by debts and wasiyyat"}

    shares = {}
    fixed_total = Fraction(0, 1)

    # Wife/Wives
    wife_count = heirs.get('wife', 0)
    if wife_count > 0:
        has_children = (heirs.get('sons', 0) + heirs.get('daughters', 0) +
                        heirs.get('grandsons', 0) + heirs.get('granddaughters', 0)) > 0
        if has_children:
            wife_share = HANAFI_FIXED_SHARES['wife_with_children']
            ref = REFERENCES['hanafi_wife_with_children']
        else:
            wife_share = HANAFI_FIXED_SHARES['wife_no_children']
            ref = REFERENCES['hanafi_wife_no_children']
        per_wife = wife_share / wife_count
        for i in range(wife_count):
            shares[f'wife_{i+1}'] = {'fraction': str(per_wife), 'amount': float(per_wife * distributable), 'reference': ref}
        fixed_total += wife_share

    # Husband
    husband_count = heirs.get('husband', 0)
    if husband_count > 0:
        has_children = (heirs.get('sons', 0) + heirs.get('daughters', 0) +
                        heirs.get('grandsons', 0) + heirs.get('granddaughters', 0)) > 0
        if has_children:
            husband_share = HANAFI_FIXED_SHARES['husband_with_children']
            ref = REFERENCES['hanafi_husband_with_children']
        else:
            husband_share = HANAFI_FIXED_SHARES['husband_no_children']
            ref = REFERENCES['hanafi_husband_no_children']
        shares['husband'] = {'fraction': str(husband_share), 'amount': float(husband_share * distributable), 'reference': ref}
        fixed_total += husband_share

    # Mother
    mother_count = heirs.get('mother', 0)
    if mother_count > 0:
        has_children = (heirs.get('sons', 0) + heirs.get('daughters', 0) +
                        heirs.get('grandsons', 0) + heirs.get('granddaughters', 0)) > 0
        siblings = heirs.get('brothers', 0) + heirs.get('sisters', 0)
        if has_children or siblings >= 2:
            mother_share = HANAFI_FIXED_SHARES['mother_with_children']
            ref = REFERENCES['hanafi_mother_with_children']
        else:
            mother_share = HANAFI_FIXED_SHARES['mother_no_children_no_siblings']
            ref = REFERENCES['hanafi_mother_no_children_no_siblings']
        shares['mother'] = {'fraction': str(mother_share), 'amount': float(mother_share * distributable), 'reference': ref}
        fixed_total += mother_share

    # Father
    father_count = heirs.get('father', 0)
    if father_count > 0:
        father_share = HANAFI_FIXED_SHARES['father_minimum']
        shares['father'] = {'fraction': str(father_share), 'amount': float(father_share * distributable), 'reference': REFERENCES['hanafi_father_minimum']}
        fixed_total += father_share

    # Daughters (only if no sons)
    sons = heirs.get('sons', 0)
    daughters = heirs.get('daughters', 0)
    if sons == 0 and daughters > 0:
        if daughters == 1:
            daughter_share = HANAFI_FIXED_SHARES['daughter_sole']
            ref = REFERENCES['hanafi_daughter_sole']
        else:
            daughter_share = HANAFI_FIXED_SHARES['daughters_multiple']
            ref = REFERENCES['hanafi_daughters_multiple']
        per_daughter = daughter_share / daughters
        for i in range(daughters):
            shares[f'daughter_{i+1}'] = {'fraction': str(per_daughter), 'amount': float(per_daughter * distributable), 'reference': ref}
        fixed_total += daughter_share

    # Residue (Asaba)
    residue = Fraction(1, 1) - fixed_total
    if residue > 0:
        if sons > 0 or daughters > 0:
            child_shares = _distribute_residue_children(residue, sons, daughters)
            ref = REFERENCES['hanafi_asaba_children']
            if sons > 0:
                for i in range(sons):
                    shares[f'son_{i+1}'] = {'fraction': str(child_shares['son']), 'amount': float(child_shares['son'] * distributable), 'reference': ref}
            if daughters > 0 and sons > 0:
                for i in range(daughters):
                    shares[f'daughter_{i+1}'] = {'fraction': str(child_shares['daughter']), 'amount': float(child_shares['daughter'] * distributable), 'reference': ref}
        elif 'father' in shares:
            shares['father']['fraction'] = str(Fraction(shares['father']['fraction']) + residue)
            shares['father']['amount'] = float((Fraction(shares['father']['fraction']) * distributable))
            shares['father']['reference'] += " + residue as Asaba."

    return shares

def calculate_shia(heirs: Dict[str, int], total_estate: float, movable_estate: float = None, debts: float = 0, wasiyyat: float = 0) -> Dict[str, Dict]:
    distributable = total_estate - debts - min(wasiyyat, total_estate * 1/3)
    if distributable <= 0:
        return {"error": "Estate exhausted"}
    # Use same logic but add Shia-specific notes
    hanafi_result = calculate_hanafi(heirs, distributable, debts=0, wasiyyat=0)
    # Add Shia reference notes
    for key in hanafi_result:
        if key.startswith('wife'):
            hanafi_result[key]['reference'] = REFERENCES['shia_wife_no_land'] + " " + hanafi_result[key].get('reference', '')
    return hanafi_result

def calculate_christian(heirs: Dict[str, int], total_estate: float, debts: float = 0) -> Dict[str, Dict]:
    distributable = total_estate - debts
    spouse = heirs.get('spouse', 0)
    children = heirs.get('children', 0)

    if spouse and children:
        spouse_share = CHRISTIAN_RULES['spouse_with_children']['spouse']
        children_share = CHRISTIAN_RULES['spouse_with_children']['children']
        per_child = children_share / children
        result = {'spouse': {'fraction': str(spouse_share), 'amount': float(spouse_share * distributable), 'reference': REFERENCES['christian_spouse_children']}}
        for i in range(children):
            result[f'child_{i+1}'] = {'fraction': str(per_child), 'amount': float(per_child * distributable), 'reference': REFERENCES['christian_spouse_children']}
        return result
    elif spouse and not children:
        return {'spouse': {'fraction': '1/1', 'amount': float(distributable), 'reference': REFERENCES['christian_spouse_only']}}
    elif not spouse and children:
        per_child = Fraction(1, 1) / children
        result = {}
        for i in range(children):
            result[f'child_{i+1}'] = {'fraction': str(per_child), 'amount': float(per_child * distributable), 'reference': REFERENCES['christian_children_only']}
        return result
    else:
        return {"error": "No valid heirs (spouse or children)"}

def calculate_hindu(heirs: Dict[str, int], total_estate: float, debts: float = 0) -> Dict[str, Dict]:
    distributable = total_estate - debts
    class_i_count = heirs.get('widow', 0) + heirs.get('sons', 0) + heirs.get('daughters', 0)
    if class_i_count == 0:
        return {"error": "No Class I heirs. Please consult a lawyer for Class II or coparcenary property."}
    per_heir = Fraction(1, 1) / class_i_count
    result = {}
    ref = REFERENCES['hindu_class_I']
    if heirs.get('widow', 0):
        result['widow'] = {'fraction': str(per_heir), 'amount': float(per_heir * distributable), 'reference': ref}
    for i in range(heirs.get('sons', 0)):
        result[f'son_{i+1}'] = {'fraction': str(per_heir), 'amount': float(per_heir * distributable), 'reference': ref}
    for i in range(heirs.get('daughters', 0)):
        result[f'daughter_{i+1}'] = {'fraction': str(per_heir), 'amount': float(per_heir * distributable), 'reference': ref}
    return result

def calculate_shares(sect: str, heirs: Dict[str, int], total_estate: float,
                     debts: float = 0, wasiyyat: float = 0, **kwargs) -> Dict[str, Dict]:
    if sect == 'hanafi':
        return calculate_hanafi(heirs, total_estate, debts, wasiyyat)
    elif sect == 'shia':
        movable = kwargs.get('movable_estate', total_estate)
        return calculate_shia(heirs, total_estate, movable, debts, wasiyyat)
    elif sect == 'christian':
        return calculate_christian(heirs, total_estate, debts)
    elif sect == 'hindu':
        return calculate_hindu(heirs, total_estate, debts)
    else:
        raise ValueError(f"Unknown sect: {sect}")