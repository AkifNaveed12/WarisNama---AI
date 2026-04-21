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


def _distribute_residue_children(residue: Fraction, sons: int, daughters: int, 
                                  grandsons: int = 0, granddaughters: int = 0) -> Dict[str, Fraction]:
    """Distribute residue to children (sons get 2x daughters)."""
    shares = {}
    total_units = sons * 2 + daughters * 1 + grandsons * 2 + granddaughters * 1
    if total_units == 0:
        return shares
    per_unit = residue / total_units
    if sons > 0:
        shares['son'] = per_unit * 2
    if daughters > 0:
        shares['daughter'] = per_unit
    if grandsons > 0:
        shares['grandson'] = per_unit * 2
    if granddaughters > 0:
        shares['granddaughter'] = per_unit
    return shares


def _apply_mflo_predeceased_son(heirs: Dict[str, int]) -> Dict[str, int]:
    """MFLO 1961 Section 4: Grandchildren of a predeceased son inherit the son's share."""
    if not MFLO_PREDECEASED_SON_RULE:
        return heirs
    
    if heirs.get('sons', 0) > 0:
        return heirs
    
    predeceased_sons = heirs.get('predeceased_sons', 0)
    if predeceased_sons > 0:
        heirs['grandsons'] = heirs.get('grandsons_from_predeceased_son', 0)
        heirs['granddaughters'] = heirs.get('granddaughters_from_predeceased_son', 0)
    
    return heirs


def calculate_hanafi(heirs: Dict[str, int], total_estate: float, debts: float = 0, 
                     wasiyyat: float = 0) -> Dict[str, Dict]:
    """Sunni Hanafi calculation with MFLO §4."""
    
    heirs = _apply_mflo_predeceased_son(heirs.copy())
    
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
    grandsons = heirs.get('grandsons', 0)
    granddaughters = heirs.get('granddaughters', 0)
    
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
        if sons > 0 or daughters > 0 or grandsons > 0 or granddaughters > 0:
            child_shares = _distribute_residue_children(residue, sons, daughters, grandsons, granddaughters)
            ref = REFERENCES['hanafi_asaba_children']
            if sons > 0:
                for i in range(sons):
                    shares[f'son_{i+1}'] = {'fraction': str(child_shares['son']), 'amount': float(child_shares['son'] * distributable), 'reference': ref}
            if daughters > 0 and sons > 0:
                for i in range(daughters):
                    shares[f'daughter_{i+1}'] = {'fraction': str(child_shares['daughter']), 'amount': float(child_shares['daughter'] * distributable), 'reference': ref}
            if grandsons > 0 and sons == 0:
                for i in range(grandsons):
                    shares[f'grandson_{i+1}'] = {'fraction': str(child_shares['grandson']), 'amount': float(child_shares['grandson'] * distributable), 'reference': 'MFLO 1961 §4: Grandchild of predeceased son inherits father\'s share'}
        elif 'father' in shares:
            new_fraction = Fraction(shares['father']['fraction']) + residue
            shares['father']['fraction'] = str(new_fraction)
            shares['father']['amount'] = float(new_fraction * distributable)
            shares['father']['reference'] += " + residue as Asaba."

    return shares


def calculate_shia(heirs: Dict[str, int], total_estate: float, movable_estate: float = None, 
                   debts: float = 0, wasiyyat: float = 0) -> Dict[str, Dict]:
    """Shia Jafari calculation – wife does NOT inherit land."""
    distributable = total_estate - debts - min(wasiyyat, total_estate * 1/3)
    if distributable <= 0:
        return {"error": "Estate exhausted"}
    
    if movable_estate is not None and heirs.get('wife', 0) > 0:
        wife_distributable = movable_estate - debts - min(wasiyyat, movable_estate * 1/3)
        other_distributable = (total_estate - movable_estate) - debts - min(wasiyyat, (total_estate - movable_estate) * 1/3)
        
        wife_heirs = {'wife': heirs.get('wife', 0)}
        wife_result = calculate_hanafi(wife_heirs, wife_distributable, 0, 0)
        
        other_heirs = {k: v for k, v in heirs.items() if k != 'wife'}
        other_result = calculate_hanafi(other_heirs, other_distributable, 0, 0)
        
        result = {**wife_result, **other_result}
        for key in result:
            if key.startswith('wife'):
                result[key]['reference'] = REFERENCES.get('shia_wife_no_land', 'Shia: Wife inherits only movable assets') + " " + result[key].get('reference', '')
        return result
    
    hanafi_result = calculate_hanafi(heirs, distributable, 0, 0)
    for key in hanafi_result:
        if key.startswith('wife'):
            hanafi_result[key]['reference'] = REFERENCES.get('shia_wife_no_land', 'Shia: Wife inherits only movable assets') + " " + hanafi_result[key].get('reference', '')
    return hanafi_result


def calculate_christian(heirs: Dict[str, int], total_estate: float, debts: float = 0) -> Dict[str, Dict]:
    """Christian – Succession Act 1925."""
    distributable = total_estate - debts
    spouse = heirs.get('spouse', 0)
    children = heirs.get('children', 0)

    if spouse > 0 and children > 0:
        spouse_share = Fraction(1, 3)
        children_share = Fraction(2, 3)
        per_child = children_share / children
        result = {'spouse': {'fraction': str(spouse_share), 'amount': float(spouse_share * distributable), 'reference': REFERENCES.get('christian_spouse_children')}}
        for i in range(children):
            result[f'child_{i+1}'] = {'fraction': str(per_child), 'amount': float(per_child * distributable), 'reference': REFERENCES.get('christian_spouse_children')}
        return result
    elif spouse > 0 and children == 0:
        return {'spouse': {'fraction': '1/1', 'amount': float(distributable), 'reference': REFERENCES.get('christian_spouse_only')}}
    elif spouse == 0 and children > 0:
        per_child = Fraction(1, 1) / children
        result = {}
        for i in range(children):
            result[f'child_{i+1}'] = {'fraction': str(per_child), 'amount': float(per_child * distributable), 'reference': REFERENCES.get('christian_children_only')}
        return result
    else:
        return {"error": "No valid heirs (spouse or children)"}


def calculate_hindu(heirs: Dict[str, int], total_estate: float, debts: float = 0) -> Dict[str, Dict]:
    """Hindu – Hindu Succession Act 1956."""
    distributable = total_estate - debts
    class_i_count = heirs.get('widow', 0) + heirs.get('sons', 0) + heirs.get('daughters', 0)
    
    if class_i_count == 0:
        return {"error": "No Class I heirs. Please consult a lawyer for Class II or coparcenary property."}
    
    per_heir = Fraction(1, 1) / class_i_count
    result = {}
    ref = REFERENCES.get('hindu_class_I')
    
    if heirs.get('widow', 0):
        result['widow'] = {'fraction': str(per_heir), 'amount': float(per_heir * distributable), 'reference': ref}
    for i in range(heirs.get('sons', 0)):
        result[f'son_{i+1}'] = {'fraction': str(per_heir), 'amount': float(per_heir * distributable), 'reference': ref}
    for i in range(heirs.get('daughters', 0)):
        result[f'daughter_{i+1}'] = {'fraction': str(per_heir), 'amount': float(per_heir * distributable), 'reference': ref}
    return result


def calculate_shares(sect: str, heirs: Dict[str, int], total_estate: float,
                     debts: float = 0, wasiyyat: float = 0, **kwargs) -> Dict[str, Dict]:
    """Main entry point for share calculation."""
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


if __name__ == "__main__":
    # Test
    test_heirs = {'sons': 2, 'daughters': 1, 'wife': 1}
    result = calculate_shares('hanafi', test_heirs, 8_000_000, 500_000, 0)
    print(result)