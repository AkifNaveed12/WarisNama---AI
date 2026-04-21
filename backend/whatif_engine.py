#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
What-If Scenario Simulator – allows users to test alternative scenarios.
Supports: excluding an heir, forcing a sale, buy-out simulation.
"""

from typing import Dict, List, Any, Optional
from copy import deepcopy

from faraid_engine import calculate_shares
from tax_engine import calculate_heir_tax, calculate_all_heirs_tax


def simulate_exclude_heir(original_heirs: Dict[str, int], excluded_heir_type: str,
                          sect: str, total_estate: float, debts: float = 0,
                          wasiyyat: float = 0, **kwargs) -> Dict[str, Any]:
    """Simulate distribution if a certain heir is excluded."""
    modified_heirs = deepcopy(original_heirs)
    
    if excluded_heir_type in modified_heirs:
        del modified_heirs[excluded_heir_type]
    
    original_result = calculate_shares(sect, original_heirs, total_estate, debts, wasiyyat, **kwargs)
    modified_result = calculate_shares(sect, modified_heirs, total_estate, debts, wasiyyat, **kwargs)
    
    differences = {}
    for heir, data in original_result.items():
        if heir in modified_result:
            diff = modified_result[heir]['amount'] - data['amount']
            differences[heir] = {
                'original': data['amount'],
                'new': modified_result[heir]['amount'],
                'difference': diff,
                'percentage_change': (diff / data['amount'] * 100) if data['amount'] > 0 else 0
            }
    
    return {
        'scenario': f"Exclude {excluded_heir_type}",
        'excluded_heir': excluded_heir_type,
        'original_shares': original_result,
        'modified_shares': modified_result,
        'differences': differences,
        'warning': "Excluding a legal heir is generally ILLEGAL under Pakistani law."
    }


def simulate_forced_sale(heirs_shares: Dict[str, float], filer_status_map: Dict[str, str],
                         province: str = 'Punjab') -> Dict[str, Any]:
    """Simulate forced sale of inherited property."""
    heirs_data = {heir_id: {'amount': amount} for heir_id, amount in heirs_shares.items()}
    tax_results = calculate_all_heirs_tax(heirs_data, filer_status_map, action='sell', province=province)
    
    total_gross = sum(heirs_shares.values())
    total_tax = sum(result.get('total_tax', 0) for result in tax_results.values())
    total_net = total_gross - total_tax
    
    return {
        'scenario': 'Forced Sale to Third Party',
        'total_gross_proceeds': total_gross,
        'total_tax_liability': total_tax,
        'total_net_to_heirs': total_net,
        'per_heir_breakdown': tax_results,
        'effective_tax_rate': (total_tax / total_gross * 100) if total_gross > 0 else 0
    }


def simulate_buyout(buying_heir_id: str, heirs_shares: Dict[str, float],
                    total_property_value: float, filer_status_map: Dict[str, str],
                    province: str = 'Punjab') -> Dict[str, Any]:
    """Simulate one heir buying out all others."""
    total_payout = 0
    payouts = {}
    
    for heir_id, share_value in heirs_shares.items():
        if heir_id != buying_heir_id:
            payouts[heir_id] = {'share_value': share_value}
            total_payout += share_value
    
    for heir_id in payouts.keys():
        status = filer_status_map.get(heir_id, 'non_filer')
        tax_result = calculate_heir_tax(payouts[heir_id]['share_value'], status, 'sell', province)
        payouts[heir_id]['tax_on_sale'] = tax_result.get('total_tax', 0)
        payouts[heir_id]['net_to_seller'] = tax_result.get('net_after_tax', payouts[heir_id]['share_value'])
    
    buyer_tax = calculate_heir_tax(total_payout, filer_status_map.get(buying_heir_id, 'non_filer'), 'buy', province)
    total_buyer_cost = total_payout + buyer_tax.get('total_tax', 0)
    
    return {
        'scenario': f'Buyout by {buying_heir_id}',
        'buying_heir': buying_heir_id,
        'buying_heir_original_share': heirs_shares.get(buying_heir_id, 0),
        'buying_heir_final_share': total_property_value,
        'total_payout_to_others': total_payout,
        'buyer_tax_liability': buyer_tax.get('total_tax', 0),
        'total_buyer_cost': total_buyer_cost,
        'payouts': payouts,
        'recommendation': f"{buying_heir_id} needs PKR {total_buyer_cost:,.0f} to complete buyout."
    }


def simulate_compare_scenarios(heirs_shares: Dict[str, float], filer_status_map: Dict[str, str],
                                total_property_value: float, province: str = 'Punjab') -> Dict[str, Any]:
    """Compare multiple scenarios side-by-side."""
    hold_scenario = {'name': 'Hold Property', 'immediate_tax': 0, 'net_to_heirs': total_property_value}
    
    sell_result = simulate_forced_sale(heirs_shares, filer_status_map, province)
    sell_scenario = {
        'name': 'Sell to Third Party',
        'immediate_tax': sell_result['total_tax_liability'],
        'net_to_heirs': sell_result['total_net_to_heirs']
    }
    
    first_heir = list(heirs_shares.keys())[0] if heirs_shares else None
    if first_heir:
        buyout_result = simulate_buyout(first_heir, heirs_shares, total_property_value, filer_status_map, province)
        buyout_scenario = {
            'name': f'Buyout by {first_heir}',
            'immediate_tax': buyout_result['buyer_tax_liability'] + sum(p['tax_on_sale'] for p in buyout_result['payouts'].values()),
            'net_to_heirs': total_property_value - buyout_result['buyer_tax_liability']
        }
    else:
        buyout_scenario = {'name': 'Buyout', 'immediate_tax': 0, 'net_to_heirs': 0}
    
    return {
        'comparison': {'hold': hold_scenario, 'sell_to_third_party': sell_scenario, 'buyout': buyout_scenario}
    }


def simulate_what_if(sect: str, heirs: Dict[str, int], total_estate: float,
                     scenario_type: str, **kwargs) -> Dict[str, Any]:
    """Main entry point for what-if simulations."""
    if scenario_type == 'exclude_heir':
        excluded = kwargs.get('excluded_heir_type')
        if not excluded:
            return {'error': 'excluded_heir_type required'}
        return simulate_exclude_heir(heirs, excluded, sect, total_estate, **kwargs)
    
    elif scenario_type == 'forced_sale':
        shares_result = calculate_shares(sect, heirs, total_estate, **kwargs)
        heirs_shares = {k: v['amount'] for k, v in shares_result.items() if 'amount' in v}
        filer_map = kwargs.get('filer_status_map', {h: 'non_filer' for h in heirs_shares.keys()})
        return simulate_forced_sale(heirs_shares, filer_map, kwargs.get('province', 'Punjab'))
    
    elif scenario_type == 'buyout':
        shares_result = calculate_shares(sect, heirs, total_estate, **kwargs)
        heirs_shares = {k: v['amount'] for k, v in shares_result.items() if 'amount' in v}
        buying_heir = kwargs.get('buying_heir_id', list(heirs_shares.keys())[0] if heirs_shares else None)
        filer_map = kwargs.get('filer_status_map', {h: 'non_filer' for h in heirs_shares.keys()})
        return simulate_buyout(buying_heir, heirs_shares, total_estate, filer_map, kwargs.get('province', 'Punjab'))
    
    elif scenario_type == 'compare':
        shares_result = calculate_shares(sect, heirs, total_estate, **kwargs)
        heirs_shares = {k: v['amount'] for k, v in shares_result.items() if 'amount' in v}
        filer_map = kwargs.get('filer_status_map', {h: 'non_filer' for h in heirs_shares.keys()})
        return simulate_compare_scenarios(heirs_shares, filer_map, total_estate, kwargs.get('province', 'Punjab'))
    
    else:
        return {'error': f"Unknown scenario_type: {scenario_type}"}


if __name__ == "__main__":
    test_heirs = {'sons': 2, 'daughters': 1, 'wife': 1}
    result = simulate_what_if('hanafi', test_heirs, 8_000_000, 'compare')
    print(result)