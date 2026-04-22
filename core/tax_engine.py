#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — tax_engine.py
=================================
Thin orchestration layer over knowledge_base tax system.

All tax calculations MUST come from knowledge_base to ensure:
✔ Legal accuracy (FBR 2025)
✔ No duplication
✔ Consistency across modules
"""

from typing import Dict, Any

from core.knowledge_base import (
    calculate_full_tax_summary,
    FilerStatus,
    Province
)


# ─────────────────────────────────────────────
# Single Heir Tax Calculation
# ─────────────────────────────────────────────
def calculate_heir_tax(
    share_value_pkr: float,
    full_property_value_pkr: float,
    filer_status: str,
    action: str,
    province: str = Province.DEFAULT,
    acquisition_after_july_2024: bool = True,
    holding_years: int = None
) -> Dict[str, Any]:
    """
    Calculate ALL taxes for a single heir.

    Args:
        share_value_pkr         : Heir's share value
        full_property_value_pkr : FULL property value (CRITICAL for tax brackets)
        filer_status            : 'filer', 'late_filer', 'non_filer'
        action                  : 'sell', 'hold', 'buyout'
        province                : Province for stamp duty
        acquisition_after_july_2024 : CGT rule selector
        holding_years           : Needed for pre-2024 CGT

    Returns:
        Complete tax breakdown dict
    """

    return calculate_full_tax_summary(
        share_value_pkr=share_value_pkr,
        full_property_value_pkr=full_property_value_pkr,
        filer_status=filer_status,
        action=action,
        province=province,
        acquisition_after_july_2024=acquisition_after_july_2024,
        holding_years=holding_years
    )


# ─────────────────────────────────────────────
# Multi-Heir Tax Calculation
# ─────────────────────────────────────────────
def calculate_all_heirs_tax(
    heirs_shares: Dict[str, Dict],
    filer_status_map: Dict[str, str],
    full_property_value_pkr: float,
    action: str = "sell",
    province: str = Province.DEFAULT,
    acquisition_after_july_2024: bool = True,
    holding_years: int = None
) -> Dict[str, Dict]:
    """
    Calculate taxes for ALL heirs.

    Args:
        heirs_shares: {
            heir_id: {
                'amount': float,
                ...
            }
        }
        filer_status_map: {
            heir_id: 'filer' / 'late_filer' / 'non_filer'
        }
        full_property_value_pkr: FULL estate/property value
        action: 'sell', 'hold', 'buyout'
        province: Province
        acquisition_after_july_2024: CGT rule
        holding_years: for pre-2024 CGT

    Returns:
        Dict of heir_id → tax breakdown
    """

    results = {}

    for heir_id, data in heirs_shares.items():

        share_value = data.get("amount", 0.0)

        filer_status = filer_status_map.get(
            heir_id,
            FilerStatus.NON_FILER  # default
        )

        results[heir_id] = calculate_heir_tax(
            share_value_pkr=share_value,
            full_property_value_pkr=full_property_value_pkr,
            filer_status=filer_status,
            action=action,
            province=province,
            acquisition_after_july_2024=acquisition_after_july_2024,
            holding_years=holding_years
        )

    return results