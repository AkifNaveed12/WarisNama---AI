#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — dispute_detector.py
=================================

Production-grade dispute detection system.

✔ Fully aligned with knowledge_base.py
✔ Supports NLP + structured inputs
✔ No duplicated legal logic
✔ Covers all dispute patterns
✔ Deployment ready
"""

from typing import Dict, Any, List

from knowledge_base import (
    detect_disputes,
    get_fraud_severity_label,
    DocumentType
)


# ─────────────────────────────────────────────
# INPUT NORMALIZATION (CRITICAL LAYER)
# ─────────────────────────────────────────────
def build_trigger_flags(user_input: Dict[str, Any]) -> List[str]:
    """
    Convert structured user input into KB-compatible trigger flags.

    Supports:
    ✔ Aliyan prototype keys
    ✔ Future NLP outputs
    ✔ Manual API inputs
    """

    flags = []

    # ───────── FRAUDULENT MUTATION ─────────
    if user_input.get("mutation_done_by_one_heir") or user_input.get("mutation_by_single_heir"):
        flags.append("mutation_by_single_heir")

    if not user_input.get("has_succession_certificate", True) or user_input.get("no_succession_certificate"):
        flags.append("no_succession_certificate_obtained")

    if not user_input.get("heirs_informed", True):
        flags.append("other_heirs_not_informed")

    # ───────── FORCED SALE ─────────
    if user_input.get("selling_without_consent") or user_input.get("one_heir_wants_sell"):
        flags.append("one_heir_selling_without_consent")

    # ───────── HIBA (GIFT) ─────────
    if user_input.get("gift_hiba_present") or user_input.get("gift_deed_mentioned"):
        flags.append("gift_deed_hiba_mentioned")

    if not user_input.get("possession_transferred", True) or user_input.get("donor_still_in_possession"):
        flags.append("donor_still_occupying_property")

    # ───────── WASIYYAT ─────────
    if user_input.get("will_present") or user_input.get("will_mentioned"):
        flags.append("will_mentioned")

    if user_input.get("will_exceeds_limit") or user_input.get("will_percentage", 0) > 33.33:
        flags.append("will_bequest_exceeds_one_third")

    # ───────── DEBT VIOLATION ─────────
    if user_input.get("debts_present") or user_input.get("debts_mentioned"):
        if not user_input.get("debts_paid", True) or user_input.get("estate_distributed_before_debt"):
            flags.append("estate_distributed_without_paying_debts")

    # ───────── MINOR HEIR ─────────
    if user_input.get("minor_heir_present") or user_input.get("heir_age_under_18"):
        flags.append("heir_age_under_18")

    # ───────── DAUGHTER DENIED ─────────
    if user_input.get("daughters_denied_share"):
        flags.append("daughters_told_they_inherit_nothing")

    if user_input.get("forced_relinquishment"):
        flags.append("daughters_pressured_to_sign_relinquishment")

    # ───────── BUYOUT ─────────
    if user_input.get("buyout_scenario"):
        flags.append("one_heir_wants_to_keep_property")

    return flags


# ─────────────────────────────────────────────
# MAIN DETECTOR ENGINE
# ─────────────────────────────────────────────
def detect_inheritance_disputes(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full dispute detection pipeline.

    Input:
        scenario → structured dict (from NLP or UI)

    Output:
        Structured dispute analysis
    """

    flags = build_trigger_flags(scenario)

    matches = detect_disputes(flags)

    results = []

    for m in matches:
        results.append({
            "pattern": str(m["pattern_key"]),
            "fraud_score": m["fraud_score"],
            "severity": get_fraud_severity_label(m["fraud_score"]),
            "matched_triggers": m.get("matched_triggers", []),

            # Legal info
            "law_sections": m.get("law_sections", {}),
            "penalty": m.get("penalty"),
            "court": m.get("court"),
            "remedy": m.get("remedy"),

            # Actions
            "recommended_actions": m.get("immediate_actions", []),

            # Documents
            "documents_to_generate": [
                d.value if isinstance(d, DocumentType) else d
                for d in m.get("documents_to_generate", [])
            ],

            # Urdu support
            "urdu_title": m.get("urdu_title"),
            "urdu_action": m.get("urdu_action")
        })

    highest = results[0] if results else None

    return {
        "flags_detected": flags,
        "total_patterns_detected": len(results),
        "disputes": results,
        "highest_risk": highest,
        "summary": _generate_summary(results)
    }


# ─────────────────────────────────────────────
# SUMMARY GENERATOR
# ─────────────────────────────────────────────
def _generate_summary(results: List[Dict]) -> str:
    """
    Generate human-readable summary.
    """

    if not results:
        return "No major inheritance dispute or fraud risk detected."

    top = results[0]

    return (
        f"⚠️ {len(results)} issue(s) detected. "
        f"Highest Risk: {top['pattern']} "
        f"({top['severity']}). "
        f"Recommended: "
        f"{top['recommended_actions'][0] if top['recommended_actions'] else 'Consult a lawyer.'}"
    )