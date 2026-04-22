#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — nlp_parser.py
=================================

Conversational NLP Engine using Gemini 1.5 Flash

✔ Urdu + English support
✔ Voice + text compatible
✔ Robust JSON parsing
✔ Engine-ready normalization
✔ Production + hackathon ready
"""

import os
import json
import re
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai


# ─────────────────────────────────────────────
# CONFIGURATION (SAFE)
# ─────────────────────────────────────────────
def _configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "❌ GEMINI_API_KEY not found. Set it in .env or environment variables."
        )

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


model = _configure_gemini()


# ─────────────────────────────────────────────
# STRONG PROMPT (VOICE + LEGAL)
# ─────────────────────────────────────────────
NLP_PROMPT = """
You are WarisNama AI — a Pakistani inheritance law assistant.

Your job:
Extract structured legal data from user speech (Urdu, English, or mixed).

IMPORTANT RULES:
- Return ONLY valid JSON
- No explanations
- No markdown
- No ```json blocks

Understand conversational context:
Users may speak casually, emotionally, or partially.

Extract:

{
"deceased": {
    "gender": "male/female",
    "relation": "father/mother/husband/wife"
},

"heirs": [
    {
        "type": "son/daughter/wife/husband/father/mother/brother/sister/grandson/granddaughter",
        "count": number,
        "alive": true/false,
        "predeceased": true/false
    }
],

"assets": [
    {
        "type": "house/plot/shop/agricultural_land/car/cash/business",
        "estimated_value_pkr": number,
        "description": "string"
    }
],

"debts": [
    {
        "description": "string",
        "amount_pkr": number
    }
],

"will_mentioned": boolean,
"will_percentage": number or 0,

"dispute_flags": {
    "mutation_done_by_one_heir": boolean,
    "has_succession_certificate": boolean,
    "heirs_informed": boolean,
    "selling_without_consent": boolean,
    "gift_hiba_present": boolean,
    "possession_transferred": boolean,
    "will_exceeds_limit": boolean,
    "debts_present": boolean,
    "debts_paid": boolean,
    "minor_heir_present": boolean,
    "daughters_denied_share": boolean,
    "forced_relinquishment": boolean
},

"sect": "hanafi/shia/christian/hindu/null"
}

User input:
{user_text}
"""


# ─────────────────────────────────────────────
# SAFE JSON PARSER
# ─────────────────────────────────────────────
def _safe_json_parse(text: str) -> Dict[str, Any]:
    """
    Clean and safely parse JSON from Gemini response.
    """

    text = text.strip()

    # Remove markdown if present
    text = re.sub(r"```json|```", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to fix common issues
        text = text.replace("\n", "").replace("\t", "")
        return json.loads(text)


# ─────────────────────────────────────────────
# NORMALIZATION (CRITICAL)
# ─────────────────────────────────────────────
def _normalize_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert NLP output → engine-ready format
    """

    normalized = {}

    # ───── HEIRS → dict format ─────
    heirs_dict = {}

    for h in data.get("heirs", []):
        h_type = h.get("type")
        count = h.get("count", 0)

        if h_type:
            # normalize plural
            if h_type == "son":
                heirs_dict["sons"] = heirs_dict.get("sons", 0) + count
            elif h_type == "daughter":
                heirs_dict["daughters"] = heirs_dict.get("daughters", 0) + count
            else:
                heirs_dict[h_type] = count

    normalized["heirs"] = heirs_dict

    # ───── ESTATE VALUE ─────
    total_estate = sum(a.get("estimated_value_pkr", 0) for a in data.get("assets", []))
    normalized["total_estate"] = total_estate

    # ───── DEBTS ─────
    total_debts = sum(d.get("amount_pkr", 0) for d in data.get("debts", []))
    normalized["debts"] = total_debts

    # ───── WASIYYAT ─────
    normalized["wasiyyat"] = (
        (data.get("will_percentage", 0) / 100.0) * total_estate
        if data.get("will_mentioned")
        else 0
    )

    # ───── SECT ─────
    normalized["sect"] = data.get("sect") or "hanafi"

    # ───── DISPUTE FLAGS ─────
    normalized["dispute_flags"] = data.get("dispute_flags", {})

    return normalized


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────
def parse_scenario(user_text: str) -> Dict[str, Any]:
    """
    Main NLP pipeline.
    """

    prompt = NLP_PROMPT.format(user_text=user_text)

    response = model.generate_content(prompt)

    raw = response.text

    parsed = _safe_json_parse(raw)

    normalized = _normalize_output(parsed)

    return {
        "raw": parsed,
        "normalized": normalized
    }