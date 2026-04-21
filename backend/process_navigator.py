#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Navigator – provides step-by-step guidance based on scenario.
Uses knowledge_base NADRA process and customizes for minor heirs, disputes, etc.
"""

from typing import Dict, List, Any
from knowledge_base import NADRA_SUCCESSION_PROCESS


STEP_NAMES_URDU = {
    'step1': 'موت کا سرٹیفکیٹ حاصل کریں',
    'step2': 'وراثت نامے کے لیے درخواست دیں',
    'step3': 'آراضی ریکارڈ سینٹر میں منتقلی کروائیں',
    'step4': 'منتقلی کا اندراج کروائیں (اگر فروخت کر رہے ہیں)'
}


def get_succession_process(minor_heir: bool = False, has_dispute: bool = False) -> dict:
    """Return the process steps with additional notes if minor or dispute."""
    steps = NADRA_SUCCESSION_PROCESS.copy()
    if minor_heir:
        steps['step2']['note'] = "MINOR HEIR DETECTED: Before applying for succession certificate, you must obtain a court-appointed guardian. Add 30-60 days."
    if has_dispute:
        steps['step3']['note'] = "DISPUTE DETECTED: Mutation may be contested. Consider filing a declaratory suit first."
    return steps


def get_bilingual_steps(minor_heir: bool = False, has_dispute: bool = False) -> List[Dict[str, str]]:
    """Get steps with both English and Urdu descriptions."""
    steps = get_succession_process(minor_heir, has_dispute)
    bilingual_steps = []
    
    for key, step in steps.items():
        bilingual_steps.append({
            'key': key,
            'name_en': step['name'],
            'name_ur': STEP_NAMES_URDU.get(key, step['name']),
            'authority_en': step['authority'],
            'fee_en': step.get('fee', 'Varies'),
            'documents': step.get('documents', []),
            'time_en': step.get('time', 'Varies'),
            'note_en': step.get('note', ''),
        })
    
    return bilingual_steps


def get_process_summary(minor_heir: bool = False, has_dispute: bool = False) -> Dict[str, Any]:
    """Get a quick summary of the process."""
    critical_alerts = []
    
    if minor_heir:
        critical_alerts.append({
            'type': 'minor_heir',
            'message': 'A minor heir (under 18) is present. A court-appointed guardian is required.',
            'action': 'Apply to District Court for guardian appointment first.'
        })
    
    if has_dispute:
        critical_alerts.append({
            'type': 'dispute',
            'message': 'A dispute has been detected. The mutation process may be contested.',
            'action': 'Consider filing a declaratory suit in Civil Court before proceeding.'
        })
    
    return {
        'total_estimated_time': '15-90 days',
        'total_estimated_cost': 'Rs 2,500 - 10,000',
        'critical_alerts': critical_alerts,
        'requires_lawyer': has_dispute or minor_heir,
    }


if __name__ == "__main__":
    steps = get_bilingual_steps(minor_heir=True, has_dispute=True)
    for step in steps:
        print(f"{step['key']}: {step['name_en']} / {step['name_ur']}")
    
    summary = get_process_summary(minor_heir=True)
    print(f"\nSummary: {summary}")