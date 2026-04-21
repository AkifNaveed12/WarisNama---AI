#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FBR Tax Engine 2025 – calculates taxes for each heir based on filer status and action.
Uses knowledge_base.py tables.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from knowledge_base import (
    TAX_236C, TAX_236K, CGT_RULES, get_tax_bracket,
    CVT_RATE, STAMP_DUTY, REGISTRATION_FEE
)


def get_cgt_rate(acquisition_date: datetime, sale_date: datetime,
                 filer_status: str, property_value: float) -> float:
    """Calculate Capital Gains Tax rate."""
    years_held = (sale_date - acquisition_date).days / 365.25
    cutoff_date = datetime(2024, 6, 30)
    
    if acquisition_date < cutoff_date:
        if years_held < 1:
            return CGT_RULES['before_30_june_2024']['year1']
        elif years_held < 2:
            return CGT_RULES['before_30_june_2024']['year2']
        elif years_held < 3:
            return CGT_RULES['before_30_june_2024']['year3']
        elif years_held < 4:
            return CGT_RULES['before_30_june_2024']['year4']
        elif years_held < 5:
            return CGT_RULES['before_30_june_2024']['year5']
        else:
            return CGT_RULES['before_30_june_2024']['year6_plus']
    else:
        if filer_status == 'filer':
            return CGT_RULES['after_1_july_2024']['filer_flat']
        else:
            sliding = CGT_RULES['after_1_july_2024']['non_filer_sliding']
            if property_value <= 25_000_000:
                return sliding['up_to_25M']
            elif property_value <= 50_000_000:
                return sliding['25M_to_50M']
            else:
                return sliding['over_50M']


def calculate_heir_tax(share_value: float, filer_status: str, action: str,
                       province: str = 'default', value_bracket: str = None,
                       share_value_at_inheritance: Optional[float] = None,
                       inheritance_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Calculate all taxes for an heir's share."""
    if value_bracket is None:
        value_bracket = get_tax_bracket(share_value)
    
    result = {
        'share_value': share_value,
        'filer_status': filer_status,
        'action': action,
        'inheritance_tax_note': '✅ Pakistan has ZERO inheritance tax.'
    }
    
    if action == 'sell':
        tax_236C = TAX_236C[value_bracket][filer_status] * share_value
        result['advance_tax_236C'] = tax_236C
        result['advance_tax_236C_rate'] = TAX_236C[value_bracket][filer_status]
        
        if share_value_at_inheritance is not None and inheritance_date is not None:
            gain = max(0, share_value - share_value_at_inheritance)
            cgt_rate = get_cgt_rate(inheritance_date, datetime.now(), filer_status, share_value)
            cgt_amount = gain * cgt_rate
            result['cgt'] = {'gain_amount': gain, 'cgt_rate': cgt_rate, 'cgt_amount': cgt_amount}
        else:
            result['cgt'] = {'gain_amount': 0, 'cgt_rate': 0, 'cgt_amount': 0}
        
        cgt_amount = result['cgt']['cgt_amount'] if isinstance(result['cgt'], dict) else 0
        result['total_tax'] = tax_236C + cgt_amount
        result['net_after_tax'] = share_value - result['total_tax']
        
        # Filer recommendation
        if filer_status != 'filer':
            filer_tax = TAX_236C[value_bracket]['filer'] * share_value
            savings = tax_236C - filer_tax
            result['filer_recommendation'] = f"💡 Become a filer before selling to save PKR {savings:,.0f}!"
        else:
            result['filer_recommendation'] = "You are already a filer."
            
    elif action == 'buy':
        tax_236K = TAX_236K[value_bracket][filer_status] * share_value
        cvt = CVT_RATE * share_value
        stamp = STAMP_DUTY.get(province, STAMP_DUTY['default']) * share_value
        reg_fee = REGISTRATION_FEE * share_value
        
        result['advance_tax_236K'] = tax_236K
        result['cvt'] = cvt
        result['stamp_duty'] = stamp
        result['registration_fee'] = reg_fee
        result['total_tax'] = tax_236K + cvt + stamp + reg_fee
        result['total_cost'] = share_value + result['total_tax']
        
    else:  # hold
        result['tax_liability'] = 0
        result['note'] = "No tax due until sale."
    
    return result


def calculate_all_heirs_tax(heirs_shares: Dict[str, Dict], filer_status_map: Dict[str, str],
                            action: str = 'sell', province: str = 'default') -> Dict[str, Dict]:
    """Calculate taxes for all heirs."""
    tax_results = {}
    for heir_id, data in heirs_shares.items():
        amount = data.get('amount', 0)
        status = filer_status_map.get(heir_id, 'non_filer')
        tax_results[heir_id] = calculate_heir_tax(amount, status, action, province)
    return tax_results


def get_family_tax_summary(tax_results: Dict[str, Dict]) -> Dict[str, Any]:
    """Generate family-level tax summary."""
    total_tax = 0
    total_net = 0
    
    for result in tax_results.values():
        total_tax += result.get('total_tax', 0)
        total_net += result.get('net_after_tax', 0)
    
    return {
        'total_family_tax': total_tax,
        'total_family_net': total_net,
        'average_tax_rate': (total_tax / (total_net + total_tax)) if (total_net + total_tax) > 0 else 0,
    }


if __name__ == "__main__":
    result = calculate_heir_tax(8_000_000, 'non_filer', 'sell', 'Punjab')
    print(result)