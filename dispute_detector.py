#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dispute & Fraud Detector – rule-based engine using knowledge_base.py patterns.
Returns fraud score, legal violations, and recommended actions.
"""

from typing import Dict, List, Any
from knowledge_base import DISPUTE_PATTERNS

def detect_disputes(scenario_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    scenario_data should include flags like:
        mutation_by_single_heir, no_succession_certificate, one_heir_wants_sell,
        others_refuse, gift_deed_mentioned, donor_still_in_possession,
        will_mentioned, will_percentage, debts_mentioned, estate_distributed_before_debt,
        heir_age_under_18, no_legal_guardian, etc.
    Returns a summary of triggered disputes.
    """
    triggered = []
    highest_score = 0

    # Pattern 1: Fraudulent Mutation
    if scenario_data.get('mutation_by_single_heir') and scenario_data.get('no_succession_certificate'):
        pattern = DISPUTE_PATTERNS['fraudulent_mutation']
        triggered.append({
            'type': 'fraudulent_mutation',
            'score': pattern['fraud_score'],
            'law': pattern['law'],
            'penalty': pattern['penalty'],
            'actions': pattern['actions'],
            'court': pattern['court'],
            'remedy': pattern['remedy']
        })
        highest_score = max(highest_score, pattern['fraud_score'])

    # Pattern 2: Forced Partial Sale
    if scenario_data.get('one_heir_wants_sell') and scenario_data.get('others_refuse'):
        pattern = DISPUTE_PATTERNS['forced_partial_sale']
        triggered.append({
            'type': 'forced_partial_sale',
            'score': pattern['fraud_score'],
            'law': pattern['law'],
            'actions': pattern['actions'],
            'court': pattern['court'],
            'remedy': pattern['remedy']
        })
        highest_score = max(highest_score, pattern['fraud_score'])

    # Pattern 3: Invalid Hiba
    if scenario_data.get('gift_deed_mentioned') and scenario_data.get('donor_still_in_possession'):
        pattern = DISPUTE_PATTERNS['invalid_hiba']
        triggered.append({
            'type': 'invalid_hiba',
            'score': pattern['fraud_score'],
            'law': pattern['law'],
            'actions': pattern['actions'],
            'court': pattern['court'],
            'remedy': pattern['remedy']
        })
        highest_score = max(highest_score, pattern['fraud_score'])

    # Pattern 4: Excessive Wasiyyat
    if scenario_data.get('will_mentioned') and scenario_data.get('will_percentage', 0) > 33.33:
        pattern = DISPUTE_PATTERNS['excessive_wasiyyat']
        triggered.append({
            'type': 'excessive_wasiyyat',
            'score': pattern['fraud_score'],
            'law': pattern['law'],
            'actions': pattern['actions'],
            'court': pattern['court'],
            'remedy': pattern['remedy']
        })
        highest_score = max(highest_score, pattern['fraud_score'])

    # Pattern 5: Debt Priority Violation
    if scenario_data.get('debts_mentioned') and scenario_data.get('estate_distributed_before_debt'):
        pattern = DISPUTE_PATTERNS['debt_priority_violation']
        triggered.append({
            'type': 'debt_priority_violation',
            'score': pattern['fraud_score'],
            'law': pattern['law'],
            'actions': pattern['actions'],
            'court': pattern['court'],
            'remedy': pattern['remedy']
        })
        highest_score = max(highest_score, pattern['fraud_score'])

    # Pattern 6: Minor Heir
    if scenario_data.get('heir_age_under_18') and not scenario_data.get('legal_guardian_appointed'):
        pattern = DISPUTE_PATTERNS['minor_heir']
        triggered.append({
            'type': 'minor_heir',
            'score': pattern['fraud_score'],
            'law': pattern['law'],
            'actions': pattern['actions'],
            'court': pattern['court'],
            'remedy': pattern['remedy']
        })
        highest_score = max(highest_score, pattern['fraud_score'])

    # Pattern 7: Buy-out Negotiation (non-fraud but we include)
    if scenario_data.get('buyout_scenario'):
        pattern = DISPUTE_PATTERNS['buyout_negotiation']
        triggered.append({
            'type': 'buyout_negotiation',
            'score': pattern['fraud_score'],
            'law': pattern['law'],
            'actions': pattern['actions'],
            'court': pattern['court'],
            'remedy': pattern['remedy']
        })

    return {
        'disputes_found': triggered,
        'fraud_score': highest_score,
        'severity': 'high' if highest_score > 70 else 'medium' if highest_score > 40 else 'low',
        'summary': f"{len(triggered)} dispute pattern(s) detected."
    }