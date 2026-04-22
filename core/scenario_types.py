#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — scenario_types.py
================================

Lightweight schema + validation layer.

✔ No duplication of knowledge_base
✔ Ensures clean data before engines
✔ Prevents runtime errors
✔ Future-proof for API layer
"""

from typing import Dict, Any, Tuple


# ─────────────────────────────────────────────
# REQUIRED KEYS
# ─────────────────────────────────────────────
REQUIRED_FIELDS = [
    "heirs",
    "total_estate",
    "sect"
]


# ─────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────
def validate_scenario(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate normalized NLP output before processing.
    """

    if not isinstance(data, dict):
        return False, "Scenario must be a dictionary."

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Estate validation
    if data.get("total_estate", 0) <= 0:
        return False, "Total estate must be greater than zero."

    # Heirs validation
    heirs = data.get("heirs", {})
    if not heirs:
        return False, "At least one heir must be present."

    for heir, count in heirs.items():
        if count < 0:
            return False, f"Invalid count for {heir}"

    # Sect validation
    valid_sects = {"hanafi", "shia", "christian", "hindu"}
    if data.get("sect") not in valid_sects:
        return False, f"Invalid sect: {data.get('sect')}"

    return True, "Valid scenario"