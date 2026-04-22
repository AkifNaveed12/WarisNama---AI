#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — process_navigator.py
=================================

Process orchestration engine.

✔ Uses knowledge_base process system
✔ Integrates dispute detection
✔ Handles minor heirs
✔ Provides guided flow (not just steps)
✔ Deployment-ready
"""

from typing import Dict, Any, List

from core.knowledge_base import get_process_steps


# ─────────────────────────────────────────────
# MAIN NAVIGATOR
# ─────────────────────────────────────────────
def get_succession_process(
    has_minor_heir: bool = False,
    has_dispute: bool = False,
    dispute_result: Dict[str, Any] = None,
    is_selling: bool = False
) -> Dict[str, Any]:
    """
    Generate complete process guidance.

    Args:
        has_minor_heir: True if any heir is minor
        has_dispute: True if dispute detected
        dispute_result: Output from dispute_detector
        is_selling: True if user plans to sell property

    Returns:
        Structured process plan
    """

    # ✅ Use knowledge_base engine (correct way)
    steps = get_process_steps(
        has_minor_heir=has_minor_heir,
        is_selling=is_selling
    )

    enriched_steps: List[Dict[str, Any]] = []

    for step in steps:
        step_copy = dict(step)

        # ───── Minor handling ─────
        if has_minor_heir and "guardian" in step_copy.get("name", "").lower():
            step_copy["alert"] = (
                "⚠️ Minor heir detected — this step is mandatory before proceeding."
            )

        # ───── Dispute handling ─────
        if has_dispute and "mutation" in step_copy.get("name", "").lower():
            step_copy["alert"] = (
                "⚠️ Dispute detected — mutation may be blocked. Legal action may be required first."
            )

        enriched_steps.append(step_copy)

    return {
        "process_steps": enriched_steps,
        "summary": _generate_process_summary(
            has_minor_heir,
            has_dispute,
            is_selling,
            dispute_result
        ),
        "priority_actions": _get_priority_actions(dispute_result),
        "estimated_complexity": _estimate_complexity(has_minor_heir, has_dispute)
    }


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
def _generate_process_summary(
    has_minor_heir: bool,
    has_dispute: bool,
    is_selling: bool,
    dispute_result: Dict[str, Any]
) -> str:

    parts = []

    if has_minor_heir:
        parts.append("Minor heir present → Guardian court step required.")

    if has_dispute:
        parts.append("Dispute detected → Legal intervention may be needed.")

    if is_selling:
        parts.append("Property sale → Tax + registration steps included.")

    if not parts:
        return "Standard inheritance process applies via NADRA."

    return " | ".join(parts)


# ─────────────────────────────────────────────
# PRIORITY ACTIONS (SMART)
# ─────────────────────────────────────────────
def _get_priority_actions(dispute_result: Dict[str, Any]) -> List[str]:
    """
    Extract most important legal actions.
    """

    if not dispute_result or not dispute_result.get("disputes"):
        return ["Proceed with normal succession certificate process."]

    top = dispute_result["disputes"][0]

    return top.get("recommended_actions", [])[:3]


# ─────────────────────────────────────────────
# COMPLEXITY ESTIMATION
# ─────────────────────────────────────────────
def _estimate_complexity(has_minor: bool, has_dispute: bool) -> str:
    """
    Simple UX metric for frontend.
    """

    if has_dispute:
        return "HIGH 🔴"
    if has_minor:
        return "MEDIUM 🟠"
    return "LOW 🟢"