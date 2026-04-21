#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Navigator – provides step-by-step guidance based on scenario.
Uses knowledge_base NADRA process and customizes for minor heirs, etc.
"""

from knowledge_base import NADRA_SUCCESSION_PROCESS

def get_succession_process(minor_heir: bool = False, has_dispute: bool = False) -> dict:
    """Return the process steps with additional notes if minor or dispute."""
    steps = NADRA_SUCCESSION_PROCESS.copy()
    if minor_heir:
        steps['step2']['note'] = "MINOR HEIR DETECTED: Before applying for succession certificate, you must obtain a court-appointed guardian. Add 30-60 days."
    if has_dispute:
        steps['step3']['note'] = "DISPUTE DETECTED: Mutation may be contested. Consider filing a declaratory suit first."
    return steps