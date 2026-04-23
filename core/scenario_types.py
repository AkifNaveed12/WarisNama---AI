
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WarisNama AI — scenario_types.py
=================================
Shared dataclasses used by every module as the canonical data model.

All modules (NLP parser, Faraid engine, dispute detector, tax engine,
doc generator, process navigator) exchange data using these types.
This file is the single source of truth for data shapes — no module
should define its own dict structure independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# HEIR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Heir:
    """Represents a single category of heir."""

    type: str                          # "son" | "daughter" | "wife" | "husband" | ...
    count: int = 1                     # Number of heirs of this type
    alive: bool = True                 # False → predeceased
    predeceased: bool = False          # True → triggers MFLO §4 check
    age: Optional[int] = None          # Used for minor detection (<18)
    name: Optional[str] = None         # Optional — for document generation
    cnic: Optional[str] = None         # Optional — for document generation
    children: Optional[Dict] = None    # For predeceased son: {grandsons: N, granddaughters: M}

    def is_minor(self) -> bool:
        return self.age is not None and self.age < 18

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "count": self.count,
            "alive": self.alive,
            "predeceased": self.predeceased,
            "age": self.age,
            "name": self.name,
            "cnic": self.cnic,
            "children": self.children,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Asset:
    """Represents a single asset in the estate."""

    type: str                              # "house" | "plot" | "shop" | "cash" | ...
    estimated_value_pkr: float = 0.0
    description: str = ""
    province: str = "Punjab"              # For stamp duty calculation
    is_immovable: bool = True             # False for cash, jewelry, etc.
    khasra_no: Optional[str] = None       # Land record number
    address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "estimated_value_pkr": self.estimated_value_pkr,
            "description": self.description,
            "province": self.province,
            "is_immovable": self.is_immovable,
            "khasra_no": self.khasra_no,
            "address": self.address,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DEBT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Debt:
    """Represents a debt/liability of the deceased."""

    description: str
    amount_pkr: float
    is_mehr: bool = False    # Unpaid dower — higher priority
    creditor: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "amount_pkr": self.amount_pkr,
            "is_mehr": self.is_mehr,
            "creditor": self.creditor,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HEIR SCENARIO (main input object)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HeirScenario:
    """
    The canonical input object.
    All three input modes (form, text, voice) must produce this object
    before any calculation module is called.
    """

    # Deceased
    deceased_name: str = ""
    deceased_gender: str = "male"        # "male" | "female"
    deceased_relation: str = "father"    # "father" | "mother" | "husband" | "wife"
    date_of_death: str = ""

    # Religion / sect
    sect: str = "hanafi"                 # "hanafi" | "shia" | "christian" | "hindu"

    # Estate
    heirs: List[Heir] = field(default_factory=list)
    assets: List[Asset] = field(default_factory=list)
    debts: List[Debt] = field(default_factory=list)
    funeral_expenses_pkr: float = 0.0
    wasiyyat_pkr: float = 0.0

    # Dispute signals (from NLP or form checkboxes)
    dispute_flags: Dict[str, Any] = field(default_factory=dict)
    disputes_mentioned: bool = False
    dispute_description: str = ""

    # Will
    will_mentioned: bool = False
    will_percentage: float = 0.0

    # Input metadata
    input_mode: str = "form"            # "form" | "text" | "voice"
    raw_input: str = ""                 # Original user text (for audit)
    parse_confidence: float = 1.0       # NLP confidence 0–1

    def total_estate_pkr(self) -> float:
        return sum(a.estimated_value_pkr for a in self.assets)

    def total_debts_pkr(self) -> float:
        return sum(d.amount_pkr for d in self.debts)

    def heirs_as_counts(self) -> Dict[str, int]:
        """
        Convert heirs list to the flat counts dict expected by calculate_shares().
        e.g. {"sons": 2, "daughters": 1, "wife": 1, "father": 1, ...}
        """
        counts: Dict[str, int] = {}
        for heir in self.heirs:
            if not heir.alive or heir.predeceased:
                continue
            key = self._normalize_heir_key(heir.type)
            counts[key] = counts.get(key, 0) + heir.count
        return counts

    def predeceased_sons_list(self) -> List[Dict]:
        """Return list of predeceased son dicts for MFLO §4 handling."""
        result = []
        for heir in self.heirs:
            if heir.type == "son" and heir.predeceased and heir.children:
                result.append({"children": heir.children})
        return result

    def has_minor_heir(self) -> bool:
        return any(h.is_minor() for h in self.heirs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deceased_name": self.deceased_name,
            "deceased_gender": self.deceased_gender,
            "deceased_relation": self.deceased_relation,
            "date_of_death": self.date_of_death,
            "sect": self.sect,
            "heirs": [h.to_dict() for h in self.heirs],
            "assets": [a.to_dict() for a in self.assets],
            "debts": [d.to_dict() for d in self.debts],
            "funeral_expenses_pkr": self.funeral_expenses_pkr,
            "wasiyyat_pkr": self.wasiyyat_pkr,
            "dispute_flags": self.dispute_flags,
            "disputes_mentioned": self.disputes_mentioned,
            "will_mentioned": self.will_mentioned,
            "will_percentage": self.will_percentage,
            "total_estate_pkr": self.total_estate_pkr(),
        }

    @staticmethod
    def _normalize_heir_key(heir_type: str) -> str:
        """Map heir_type strings to the keys used by faraid_engine."""
        mapping = {
            "son": "sons",
            "daughter": "daughters",
            "wife": "wife",           # count stored directly
            "husband": "husband",
            "mother": "mother",
            "father": "father",
            "grandson": "grandsons",
            "granddaughter": "granddaughters",
            "brother": "brothers",
            "sister": "sisters",
            "widow": "widow",         # for Hindu
            "children": "children",  # for Christian
            "spouse": "spouse",       # for Christian
        }
        return mapping.get(heir_type, heir_type)


# ═══════════════════════════════════════════════════════════════════════════════
# SHARE RESULT (output from faraid_engine)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ShareResult:
    """
    Typed wrapper around the dict returned by calculate_shares().
    Makes downstream code safer.
    """

    raw: Dict[str, Any]  # the full dict from calculate_shares()

    def distributable_estate(self) -> float:
        return float(self.raw.get("distributable_estate", 0))

    def warning(self) -> Optional[str]:
        return self.raw.get("warning")

    def error(self) -> Optional[str]:
        return self.raw.get("error")

    def heir_shares(self) -> Dict[str, Dict]:
        """Return only the heir entries (skip metadata keys)."""
        skip = {"distributable_estate", "warning", "error"}
        return {k: v for k, v in self.raw.items() if k not in skip and isinstance(v, dict)}

    def is_valid(self) -> bool:
        return "error" not in self.raw

    def to_dataframe_rows(self) -> List[Dict]:
        rows = []
        for heir_id, data in self.heir_shares().items():
            rows.append({
                "Heir": heir_id.replace("_", " ").title(),
                "Share": data.get("fraction", "N/A"),
                "Amount (PKR)": data.get("amount", 0),
                "Reference": data.get("reference", ""),
                "Reference URL": data.get("reference_url", ""),
            })
        return rows