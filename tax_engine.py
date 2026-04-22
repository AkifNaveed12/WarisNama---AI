#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FBR Tax Engine 2025 – calculates taxes for each heir based on filer status and action.
Uses knowledge_base.py tables.
"""

from typing import Dict, Any
from knowledge_base import TAX_236C, TAX_236K, get_tax_bracket, CVT_RATE, STAMP_DUTY, REGISTRATION_FEE

def calculate_heir_tax(share_value: float, filer_status: str, action: str,
                       province: str = 'default', value_bracket: str = None) -> Dict[str, Any]:
    """
    share_value: value of heir's share in PKR
    filer_status: 'filer', 'late_filer', 'non_filer'
    action: 'sell', 'buy', 'hold'
    province: for stamp duty
    Returns dict with tax components.
    """
    if value_bracket is None:
        value_bracket = get_tax_bracket(share_value)

    result = {
        'share_value': share_value,
        'filer_status': filer_status,
        'action': action
    }

    if action == 'sell':
        tax_236C = TAX_236C[value_bracket][filer_status] * share_value
        result['advance_tax_236C'] = tax_236C
        result['cgt'] = 0  # For MVP, inherited property has stepped-up basis, no gain
        result['total_tax'] = tax_236C
        result['net_after_tax'] = share_value - tax_236C
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
        result['note'] = "No tax due until sale. Pakistan has no inheritance tax."

    return result

def calculate_all_heirs_tax(heirs_shares: Dict[str, Dict], filer_status_map: Dict[str, str],
                            action: str = 'sell', province: str = 'default') -> Dict[str, Dict]:
    """
    heirs_shares: { heir_id: {'amount': float, ...} }
    filer_status_map: { heir_id: 'filer'/'late_filer'/'non_filer' }
    Returns tax results per heir.
    """
    tax_results = {}
    for heir_id, data in heirs_shares.items():
        amount = data['amount']
        status = filer_status_map.get(heir_id, 'non_filer')
        tax_results[heir_id] = calculate_heir_tax(amount, status, action, province)
    return tax_results