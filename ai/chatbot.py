#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI – Chatbot (Groq)
- Converses to collect inheritance information
- Provides legal references
- Helps distribute indivisible assets (house, car, land)
- Never outputs raw JSON – shows structured summary instead
"""

import json
import re
from typing import Dict, Any, Optional
import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

from core.knowledge_base import (
    HANAFI_FIXED_SHARES,
    DISPUTE_PATTERNS,
    SECT_DISPLAY_NAMES,
    NADRA_SUCCESSION_PROCESS,
    get_fraud_severity_label,
    WASIYYAT_MAX_FRACTION,
    INHERITANCE_TAX,
)

# ----------------------------------------------------------------------
# Legal references (displayed to user)
# ----------------------------------------------------------------------
LEGAL_REFERENCES = {
    "hanafi_wife_children": "📖 Mulla's Mohammedan Law §272 – Wife gets 1/8 if children exist",
    "hanafi_wife_no_children": "📖 Mulla's Mohammedan Law §273 – Wife gets 1/4 if no children",
    "hanafi_husband": "📖 Mulla's Mohammedan Law §274‑275 – Husband gets 1/4 (children) or 1/2 (no children)",
    "hanafi_mother": "📖 Mulla's Mohammedan Law §276‑277 – Mother gets 1/6 (with children or 2+ siblings) else 1/3",
    "hanafi_father": "📖 Mulla's Mohammedan Law §278 – Father gets 1/6 + residue",
    "hanafi_son_daughter": "📖 Mulla's Mohammedan Law §279‑285 – Son gets double daughter's share",
    "mflo_predeceased_son": "📜 Muslim Family Laws Ordinance 1961 §4 – Grandchildren inherit predeceased son's share",
    "ppc_498a": "⚠️ PPC Section 498A – 5‑10 years imprisonment for denying inheritance",
    "transfer_property_act": "📜 Transfer of Property Act 1882 §44 – Co‑owner cannot sell whole property without consent",
    "hiba_rules": "📜 Muslim Personal Law (Shariat) Application Act 1962 – Hiba requires possession transfer",
    "succession_act": "📜 Succession Act 1925 – For Christians and Hindus",
    "guardians_wards": "📜 Guardians and Wards Act 1890 – Minor heirs require court‑appointed guardian",
    "fbr_236c": "💰 FBR Finance Act 2025 §236C – Seller's tax: 3%‑20%",
    "zero_inheritance_tax": "💰 Pakistan has ZERO inheritance tax on the act of inheritance itself.",
    "asset_distribution": "🏠 Indivisible assets (house, car, plot) can be: (1) sold and cash divided, (2) one heir takes asset and pays others, (3) kept jointly."
}

# ----------------------------------------------------------------------
# Groq client (cached)
# ----------------------------------------------------------------------
@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", None)
    except Exception:
        api_key = None
    if not api_key:
        import os
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key or Groq is None:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        print(f"Groq error: {e}")
        return None

# ----------------------------------------------------------------------
# System prompt – now includes asset distribution advice and references
# ----------------------------------------------------------------------
SYSTEM_PROMPT = f"""
You are WarisNama AI, a Pakistani inheritance assistant. Your answers must follow Pakistani law (Hanafi/Shia/Christian/Hindu), FBR 2025 tax, and 8 fraud patterns.

**Inheritance rules (with references):**
- Hanafi: Wife gets 1/8 if children exist else 1/4 ({LEGAL_REFERENCES['hanafi_wife_children']}). Husband 1/4 or 1/2. Mother 1/6 or 1/3. Father 1/6 + residue. Sons get double daughters.
- Shia: Wife does NOT inherit land/buildings. (Source: Zafar & Associates)
- Christian: Spouse 1/3 if children exist, else full; children equal (Succession Act 1925).
- Hindu: Class I heirs (widow, sons, daughters) equal shares (Hindu Succession Act 1956).

**Fraud patterns – detect and cite law:**
1. Fraudulent mutation – PPC 498A, 5‑10 years.
2. Forced partial sale – Transfer of Property Act §44.
3. Invalid Hiba – need possession transfer.
4. Excessive Wasiyyat – max 1/3 of net estate.
5. Debt priority – funeral → debts → wasiyyat → faraid.
6. Minor heir – guardian required (Guardians and Wards Act 1890).
7. Buy‑out negotiation – internal transfer allowed.
8. Daughter's share denied – Quranic right, PPC 498A.

**Tax rules (FBR 2025):**
- ZERO inheritance tax. Tax only when selling.
- 236C (seller): 3%‑20% depending on filer status.
- CGT: 15% flat for filers (post‑July 2024), step‑up basis for inherited property.

**Asset distribution help (very important):**
- Ask the user about the assets (house, car, land, cash, bank accounts, etc.).
- After shares are calculated, suggest how to distribute INDIVISIBLE assets (e.g., a house).
- If cash is available, recommend selling the asset and dividing cash proportionally.
- If one heir wants to keep the asset, they can buy out others: calculate buy‑out amount = (heir's share fraction) × asset value? Actually the buying heir pays the other heirs their share of the asset.
- Provide formulas and examples. Use simple language.

**Your job:**
- Ask clarifying questions step by step.
- Detect fraud and suggest legal actions (with references).
- When you have ALL required fields (sect, heirs, total estate, debts, funeral, wasiyyat, dispute flags), produce a FINAL SUMMARY in plain English, NOT JSON. The summary should include:
    - The collected information (sect, heirs list, estate value, debts, funeral, will amount).
    - Any fraud detected and recommended actions.
    - A suggested asset distribution method (ask first about assets, then advise).
- After the summary, ask: "Would you like me to calculate the exact shares now?" If yes, you will output a special marker `<!--CALCULATE_NOW-->` so the system can run the engine.

Do not output raw JSON. Output only natural language with the marker when ready.
"""

class InheritanceChatbot:
    def __init__(self):
        self.client = get_groq_client()
        self.reset()

    def reset(self):
        self.conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.extracted_scenario = None
        self.ready_to_calculate = False

    def add_message(self, role: str, content: str):
        self.conversation.append({"role": role, "content": content})

    def chat(self, user_message: str) -> str:
        if not self.client:
            return "⚠️ Groq API key not found. Please set GROQ_API_KEY in secrets.toml or environment variable."

        self.add_message("user", user_message)
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.conversation,
                temperature=0.3,
                max_tokens=2000,
            )
            reply = response.choices[0].message.content
            self.add_message("assistant", reply)
            # Check for calculation marker
            self.ready_to_calculate = "<!--CALCULATE_NOW-->" in reply
            # Try to extract a structured scenario from the reply (for internal use)
            self._extract_scenario_from_reply(reply)
            return reply
        except Exception as e:
            error_msg = f"⚠️ API error: {str(e)}"
            self.add_message("assistant", error_msg)
            return error_msg

    def _extract_scenario_from_reply(self, text: str):
        """Attempt to extract key fields from the assistant's natural language reply (for internal use)."""
        # Very basic extraction – we rely on the conversation, but we can try regex.
        # However, the main extraction still happens from the final summary.
        # For simplicity, we don't need full JSON here; we'll use the user's session state later.
        pass

    def get_scenario(self) -> Optional[Dict[str, Any]]:
        """Return the last extracted scenario (if any) – kept for compatibility."""
        # This method is still used by app.py. We'll keep it but it may be empty.
        # The real scenario will be built by the app from the user's conversation history.
        # For now, return None to trigger the app to use the direct chat response.
        return None

    def is_ready_to_calculate(self) -> bool:
        return self.ready_to_calculate