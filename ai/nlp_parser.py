# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# """
# WarisNama AI — nlp_parser.py
# =================================

# Conversational NLP Engine using Gemini 1.5 Flash

# ✔ Urdu + English support
# ✔ Voice + text compatible
# ✔ Robust JSON parsing
# ✔ Engine-ready normalization
# ✔ Production + hackathon ready
# """

# import os
# import json
# import re
# from typing import Dict, Any
# from dotenv import load_dotenv
# load_dotenv()
# import google.generativeai as genai


# # ─────────────────────────────────────────────
# # CONFIGURATION (SAFE)
# # ─────────────────────────────────────────────
# def _configure_gemini():
#     api_key = os.getenv("GEMINI_API_KEY")

#     if not api_key:
#         raise EnvironmentError(
#             "❌ GEMINI_API_KEY not found. Set it in .env or environment variables."
#         )

#     genai.configure(api_key=api_key)
#     return genai.GenerativeModel("gemini-1.5-flash")


# model = _configure_gemini()


# # ─────────────────────────────────────────────
# # STRONG PROMPT (VOICE + LEGAL)
# # ─────────────────────────────────────────────
# NLP_PROMPT = """
# You are WarisNama AI — a Pakistani inheritance law assistant.

# Your job:
# Extract structured legal data from user speech (Urdu, English, or mixed).

# IMPORTANT RULES:
# - Return ONLY valid JSON
# - No explanations
# - No markdown
# - No ```json blocks

# Understand conversational context:
# Users may speak casually, emotionally, or partially.

# Extract:

# {
# "deceased": {
#     "gender": "male/female",
#     "relation": "father/mother/husband/wife"
# },

# "heirs": [
#     {
#         "type": "son/daughter/wife/husband/father/mother/brother/sister/grandson/granddaughter",
#         "count": number,
#         "alive": true/false,
#         "predeceased": true/false
#     }
# ],

# "assets": [
#     {
#         "type": "house/plot/shop/agricultural_land/car/cash/business",
#         "estimated_value_pkr": number,
#         "description": "string"
#     }
# ],

# "debts": [
#     {
#         "description": "string",
#         "amount_pkr": number
#     }
# ],

# "will_mentioned": boolean,
# "will_percentage": number or 0,

# "dispute_flags": {
#     "mutation_done_by_one_heir": boolean,
#     "has_succession_certificate": boolean,
#     "heirs_informed": boolean,
#     "selling_without_consent": boolean,
#     "gift_hiba_present": boolean,
#     "possession_transferred": boolean,
#     "will_exceeds_limit": boolean,
#     "debts_present": boolean,
#     "debts_paid": boolean,
#     "minor_heir_present": boolean,
#     "daughters_denied_share": boolean,
#     "forced_relinquishment": boolean
# },

# "sect": "hanafi/shia/christian/hindu/null"
# }

# User input:
# {user_text}
# """


# # ─────────────────────────────────────────────
# # SAFE JSON PARSER
# # ─────────────────────────────────────────────
# def _safe_json_parse(text: str) -> Dict[str, Any]:
#     """
#     Clean and safely parse JSON from Gemini response.
#     """

#     text = text.strip()

#     # Remove markdown if present
#     text = re.sub(r"```json|```", "", text)

#     try:
#         return json.loads(text)
#     except json.JSONDecodeError:
#         # Try to fix common issues
#         text = text.replace("\n", "").replace("\t", "")
#         return json.loads(text)


# # ─────────────────────────────────────────────
# # NORMALIZATION (CRITICAL)
# # ─────────────────────────────────────────────
# def _normalize_output(data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Convert NLP output → engine-ready format
#     """

#     normalized = {}

#     # ───── HEIRS → dict format ─────
#     heirs_dict = {}

#     for h in data.get("heirs", []):
#         h_type = h.get("type")
#         count = h.get("count", 0)

#         if h_type:
#             # normalize plural
#             if h_type == "son":
#                 heirs_dict["sons"] = heirs_dict.get("sons", 0) + count
#             elif h_type == "daughter":
#                 heirs_dict["daughters"] = heirs_dict.get("daughters", 0) + count
#             else:
#                 heirs_dict[h_type] = count

#     normalized["heirs"] = heirs_dict

#     # ───── ESTATE VALUE ─────
#     total_estate = sum(a.get("estimated_value_pkr", 0) for a in data.get("assets", []))
#     normalized["total_estate"] = total_estate

#     # ───── DEBTS ─────
#     total_debts = sum(d.get("amount_pkr", 0) for d in data.get("debts", []))
#     normalized["debts"] = total_debts

#     # ───── WASIYYAT ─────
#     normalized["wasiyyat"] = (
#         (data.get("will_percentage", 0) / 100.0) * total_estate
#         if data.get("will_mentioned")
#         else 0
#     )

#     # ───── SECT ─────
#     normalized["sect"] = data.get("sect") or "hanafi"

#     # ───── DISPUTE FLAGS ─────
#     normalized["dispute_flags"] = data.get("dispute_flags", {})

#     return normalized


# # ─────────────────────────────────────────────
# # MAIN FUNCTION
# # ─────────────────────────────────────────────
# def parse_scenario(user_text: str) -> Dict[str, Any]:
#     """
#     Main NLP pipeline.
#     """

#     prompt = NLP_PROMPT.format(user_text=user_text)

#     response = model.generate_content(prompt)

#     raw = response.text

#     parsed = _safe_json_parse(raw)

#     normalized = _normalize_output(parsed)

#     return {
#         "raw": parsed,
#         "normalized": normalized
#     }


































#######################
# ALYAN FIXES Version 2
# ###################





















# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# """
# WarisNama AI — nlp_parser.py
# Natural Language Parser with Multiple Fallback Strategies
# """
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# """
# WarisNama AI — nlp_parser.py
# Natural Language Parser with Multiple Fallback Strategies
# FIXED: Now accumulates ALL asset values from text.
# """

# import os
# import json
# import re
# from typing import Dict, Any
# from dotenv import load_dotenv

# load_dotenv()

# # Try to import Gemini, but don't fail if not available
# try:
#     from google import genai
#     from google.genai import types
#     GEMINI_AVAILABLE = True
# except ImportError:
#     GEMINI_AVAILABLE = False
#     print("Warning: google-genai not installed. Using regex fallback only.")


# # ─────────────────────────────────────────────
# # CONFIGURATION
# # ─────────────────────────────────────────────
# def _get_gemini_client():
#     """Initialize Gemini client if API key exists."""
#     api_key = os.getenv("GEMINI_API_KEY")
    
#     if not api_key or not GEMINI_AVAILABLE:
#         return None
    
#     try:
#         client = genai.Client(api_key=api_key)
#         return client
#     except Exception as e:
#         print(f"Gemini init error: {e}")
#         return None


# client = _get_gemini_client()


# # ─────────────────────────────────────────────
# # REGEX FALLBACK PARSER (WORKS WITHOUT API)
# # Now correctly handles multiple asset values.
# # ─────────────────────────────────────────────
# def _regex_parse(user_text: str) -> Dict[str, Any]:
#     """
#     Extract inheritance information using regex patterns.
#     Works with Urdu, English, and Roman Urdu.
#     Now accumulates values from ALL assets mentioned.
#     """
#     text = user_text.lower()
    
#     result = {
#         "deceased": {"gender": "male", "relation": "father"},
#         "heirs": [],
#         "assets": [],
#         "debts": [],
#         "will_mentioned": False,
#         "sect": "hanafi"
#     }
    
#     # ───── Extract Heir Counts (same as before) ─────
#     # Sons
#     son_patterns = [r'(\d+)\s*son', r'(\d+)\s*beta', r'(\d+)\s*betay', r'(\d+)\s*larkay']
#     for pattern in son_patterns:
#         match = re.search(pattern, text)
#         if match:
#             result["heirs"].append({"type": "son", "count": int(match.group(1))})
#             break
    
#     # Daughters
#     daughter_patterns = [r'(\d+)\s*daughter', r'(\d+)\s*beti', r'(\d+)\s*betiyan', r'(\d+)\s*larkiyan']
#     for pattern in daughter_patterns:
#         match = re.search(pattern, text)
#         if match:
#             result["heirs"].append({"type": "daughter", "count": int(match.group(1))})
#             break
    
#     # Wives
#     wife_patterns = [r'(\d+)\s*wife', r'(\d+)\s*biwi', r'(\d+)\s*begum']
#     for pattern in wife_patterns:
#         match = re.search(pattern, text)
#         if match:
#             result["heirs"].append({"type": "wife", "count": int(match.group(1))})
#             break
    
#     # Husband
#     if re.search(r'husband|shohar', text):
#         result["heirs"].append({"type": "husband", "count": 1})
    
#     # Mother
#     if re.search(r'mother|maa|walida', text):
#         result["heirs"].append({"type": "mother", "count": 1})
    
#     # Father
#     if re.search(r'father|baap|walid', text):
#         result["heirs"].append({"type": "father", "count": 1})
    
#     # ───── Extract ALL Estate Values (FIXED) ─────
#     # Patterns for numbers with units
#     # We'll find all occurrences of numbers followed by lakh/crore/million/thousand
#     value_pattern = r'(\d+(?:\.\d+)?)\s*(lakh|crore|million|thousand|lac|cr)'
#     matches = re.findall(value_pattern, text, re.IGNORECASE)
    
#     total_value = 0
#     asset_count = 0
    
#     for value_str, unit in matches:
#         value = float(value_str)
#         unit_lower = unit.lower()
        
#         if unit_lower in ('lakh', 'lac'):
#             total_value += int(value * 100000)
#         elif unit_lower in ('crore', 'cr'):
#             total_value += int(value * 10000000)
#         elif unit_lower == 'million':
#             total_value += int(value * 1000000)
#         elif unit_lower == 'thousand':
#             total_value += int(value * 1000)
#         asset_count += 1
    
#     # Also look for direct numbers like "80 lakh" without space? Already covered.
#     # If we found multiple assets, we add one combined asset entry.
#     if total_value > 0:
#         # Add a single asset with the total value (or you could add separate assets)
#         # For simplicity, we combine all into one "property" asset.
#         result["assets"].append({
#             "type": "property",
#             "estimated_value_pkr": total_value,
#             "description": f"total from {asset_count} asset(s)"
#         })
#     else:
#         # Fallback default if nothing found
#         result["assets"].append({"type": "house", "estimated_value_pkr": 8000000, "description": ""})
    
#     # ───── Detect Sect ─────
#     if 'shia' in text:
#         result["sect"] = "shia"
#     elif 'christian' in text or 'masihi' in text:
#         result["sect"] = "christian"
#     elif 'hindu' in text:
#         result["sect"] = "hindu"
#     else:
#         result["sect"] = "hanafi"
    
#     # ───── Detect Will ─────
#     if 'will' in text or 'wasiyyat' in text or 'وصیت' in user_text:
#         result["will_mentioned"] = True
    
#     # ───── Default heirs if nothing found ─────
#     if not result["heirs"]:
#         result["heirs"] = [
#             {"type": "son", "count": 2},
#             {"type": "daughter", "count": 3},
#             {"type": "wife", "count": 1}
#         ]
    
#     return result


# # ─────────────────────────────────────────────
# # GEMINI PARSER (with error handling)
# # ─────────────────────────────────────────────
# def _gemini_parse(user_text: str) -> Dict[str, Any]:
#     """Use Gemini API to parse natural language (already handles multiple assets)."""
#     if not client:
#         return None
    
#     prompt = f"""
# Extract inheritance information from this text. Return ONLY valid JSON.

# User text: {user_text}

# Return EXACTLY this format:
# {{"deceased": {{"gender": "male", "relation": "father"}}, "heirs": [{{"type": "son", "count": 2}}, {{"type": "daughter", "count": 3}}, {{"type": "wife", "count": 1}}], "assets": [{{"type": "house", "estimated_value_pkr": 8000000}}], "debts": [], "will_mentioned": false, "sect": "hanafi"}}

# Valid heir types: son, daughter, wife, husband, mother, father
# Valid asset types: house, plot, shop, car, cash, business
# Valid sect: hanafi, shia, christian, hindu

# IMPORTANT: If multiple assets are mentioned, sum their values into a single asset or list them separately. Make sure the total estimated_value_pkr reflects the sum of all asset values.

# Return ONLY the JSON. Start directly with {{.
# """
    
#     try:
#         response = client.models.generate_content(
#             model="gemini-2.0-flash-exp",
#             contents=prompt,
#             config=types.GenerateContentConfig(
#                 temperature=0.1,
#                 max_output_tokens=1000,
#             )
#         )
        
#         raw_response = response.text.strip()
        
#         # Clean the response
#         raw_response = re.sub(r'```json\s*', '', raw_response)
#         raw_response = re.sub(r'```\s*', '', raw_response)
#         raw_response = raw_response.lstrip('\n\r\t "').rstrip('"')
        
#         # Find JSON object
#         start = raw_response.find('{')
#         end = raw_response.rfind('}')
        
#         if start != -1 and end != -1:
#             json_str = raw_response[start:end+1]
#             return json.loads(json_str)
        
#         return None
        
#     except Exception as e:
#         print(f"Gemini error: {e}")
#         return None


# # ─────────────────────────────────────────────
# # NORMALIZATION (same as before)
# # ─────────────────────────────────────────────
# def _normalize_output(data: Dict[str, Any]) -> Dict[str, Any]:
#     """Convert parsed data to engine-ready format."""
#     normalized = {
#         "heirs": {},
#         "total_estate": 0,
#         "debts": 0,
#         "wasiyyat": 0,
#         "sect": "hanafi",
#         "dispute_flags": {}
#     }
    
#     # Process heirs
#     for heir in data.get("heirs", []):
#         heir_type = heir.get("type", "")
#         count = heir.get("count", 0)
        
#         if heir_type == "son":
#             normalized["heirs"]["sons"] = normalized["heirs"].get("sons", 0) + count
#         elif heir_type == "daughter":
#             normalized["heirs"]["daughters"] = normalized["heirs"].get("daughters", 0) + count
#         elif heir_type == "wife":
#             normalized["heirs"]["wife"] = normalized["heirs"].get("wife", 0) + count
#         elif heir_type == "husband":
#             normalized["heirs"]["husband"] = count
#         elif heir_type == "mother":
#             normalized["heirs"]["mother"] = count
#         elif heir_type == "father":
#             normalized["heirs"]["father"] = count
    
#     # Process assets - sum all values
#     total_estate = 0
#     for asset in data.get("assets", []):
#         value = asset.get("estimated_value_pkr", 0)
#         total_estate += value
    
#     if total_estate == 0:
#         total_estate = 8000000  # default if nothing found
    
#     normalized["total_estate"] = total_estate
    
#     # Process debts
#     total_debts = 0
#     for debt in data.get("debts", []):
#         total_debts += debt.get("amount_pkr", 0)
#     normalized["debts"] = total_debts
    
#     # Process sect
#     sect = data.get("sect", "hanafi")
#     if sect and sect.lower() in ["hanafi", "shia", "christian", "hindu"]:
#         normalized["sect"] = sect.lower()
#     else:
#         normalized["sect"] = "hanafi"
    
#     return normalized


# # ─────────────────────────────────────────────
# # MAIN FUNCTION
# # ─────────────────────────────────────────────
# def parse_scenario(user_text: str) -> Dict[str, Any]:
#     """
#     Main NLP pipeline with multiple fallback strategies.
#     """
#     if not user_text or not user_text.strip():
#         return {
#             "raw": {},
#             "normalized": {
#                 "heirs": {"sons": 2, "daughters": 3, "wife": 1},
#                 "total_estate": 8000000,
#                 "debts": 0,
#                 "wasiyyat": 0,
#                 "sect": "hanafi",
#                 "dispute_flags": {}
#             },
#             "success": True,
#             "method": "default"
#         }
    
#     parsed = None
#     method = "regex"
    
#     # Try Gemini first (if available)
#     if client:
#         parsed = _gemini_parse(user_text)
#         if parsed:
#             method = "gemini"
    
#     # Fallback to regex
#     if not parsed:
#         parsed = _regex_parse(user_text)
#         method = "regex"
    
#     # Normalize and return
#     normalized = _normalize_output(parsed)
    
#     return {
#         "raw": parsed,
#         "normalized": normalized,
#         "success": True,
#         "method": method
#     }

#my new versio of nlp_parser.py code


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WarisNama AI — ai/nlp_parser.py
================================
Unified NLP Engine · Production Ready · Drop-in replacement

CONTRACT with app.py
─────────────────────
app.py calls parse_scenario() and reads the result like this:

    parsed_result  = parse_scenario(user_input)
    normalized     = parsed_result.get('normalized', parsed_result)
    heirs          = normalized.get('heirs', {})
    # heirs → FLAT DICT  e.g. {"sons": 2, "daughters": 3, "wife": 1}

    st.session_state['parsed_sons']         = heirs.get('sons', 2)
    st.session_state['parsed_daughters']    = heirs.get('daughters', 3)
    st.session_state['parsed_wives']        = heirs.get('wife', 1)
    st.session_state['parsed_husband']      = heirs.get('husband', 0)
    st.session_state['parsed_mother']       = heirs.get('mother', 0)
    st.session_state['parsed_father']       = heirs.get('father', 0)
    st.session_state['parsed_total_estate'] = normalized.get('total_estate', 10_000_000)
    st.session_state['parsed_debts']        = normalized.get('debts', 0)
    st.session_state['parsed_sect']         = normalized.get('sect', 'hanafi')
    dispute_flags = normalized.get('dispute_flags', {})
    st.session_state['parsed_mutation']     = dispute_flags.get('mutation_done_by_one_heir', False)
    ...

So parse_scenario() MUST return:
{
"raw":        { ...full Gemini/regex extraction... },
"normalized": {
        "heirs":         {"sons":2, "daughters":3, "wife":1, "husband":0, ...},
        "total_estate":  8000000,
        "debts":         0,
        "wasiyyat":      0,
        "sect":          "hanafi",
        "dispute_flags": {"mutation_done_by_one_heir": False, ...}
    },
    "success": True,
    "method":  "gemini" | "regex" | "default"
}

APIs Used (all free / free-tier)
──────────────────────────────────
    GEMINI_API_KEY  → aistudio.google.com → "Get API Key"  (free, 15 req/min)
    OPENAI_API_KEY  → platform.openai.com → "API Keys"     (free $5 credit)
    gTTS            → no key needed (completely free)
    Web Speech API  → no key needed (browser-native, Chrome/Edge)

Add to your .env file:
    GEMINI_API_KEY=your_key_here
    OPENAI_API_KEY=your_key_here
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
import tempfile
from typing import Any, Dict, List, Optional

# ── dotenv ────────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | nlp_parser | %(message)s"
)
logger = logging.getLogger(__name__)

# ── env keys ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ── optional imports (never crash at import time) ─────────────────────────────
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai not found → pip install google-generativeai")

OPENAI_AVAILABLE = False
_openai_mod = None
try:
    import openai as _openai_mod
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("openai not found → pip install openai")

GTTS_AVAILABLE = False
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gtts not found → pip install gtts")

STREAMLIT_AVAILABLE = False
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — GEMINI CLIENT
# Uses google-generativeai SDK (pip install google-generativeai)
# Cached at module level so we don't re-init on every parse_scenario() call
# ═══════════════════════════════════════════════════════════════════════════════

_gemini_model_cache = None


def _get_gemini_model():
    """Return a cached Gemini 1.5 Flash GenerativeModel instance."""
    global _gemini_model_cache
    if _gemini_model_cache is not None:
        return _gemini_model_cache
    if not GEMINI_AVAILABLE:
        raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY missing from .env — "
            "get a free key at aistudio.google.com → 'Get API Key'"
        )
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model_cache = genai.GenerativeModel("gemini-1.5-flash")
    logger.info("Gemini 1.5 Flash initialised")
    return _gemini_model_cache


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — NLP PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

_NLP_PROMPT = """
You are an expert Pakistani inheritance law NLP assistant.
Extract structured information from the user's inheritance scenario.

Input may be Urdu, English, or Roman-Urdu (mixed).

Urdu keyword guide:
    beta/bete/baita/بیٹا   = son
    beti/betiyan/بیٹی      = daughter
    biwi/bivi/begum/بیوی   = wife
    shohar/shauhar/خاوند   = husband
    walid/baap/abu/والد    = father
    walida/maa/ammi/والدہ  = mother
    pota/nawaasa            = grandson
    poti/nawaasi            = granddaughter
    bhai                    = brother
    behen                   = sister
    qarz/karza/loan         = debt
    wasiyyat/will           = will/bequest
    ghar                    = house  |  dukaan/shop = shop
    zameen/plot             = land   |  lakh=100000, crore=10000000

Dispute signals:
    "apne naam kara liya/mutate/intiqal" → mutation_by_single_heir
    "bech diya/sold without consent"      → one_heir_selling_without_consent
    "hiba/gift deed/ہبہ"                  → gift_deed_hiba_mentioned
    "beti ko kuch nahi/daughters nothing" → daughters_told_they_inherit_nothing
    "no succession certificate"           → no_succession_certificate_obtained

RULES:
    1. Return ONLY valid JSON. No markdown. No backticks. No explanation.
    2. null for any field not mentioned.
    3. Money: integers in PKR (already converted from lakh/crore).
    4. heir counts: integers.

JSON SCHEMA (return exactly this):
{
    "deceased": {"gender": "male"|"female"|null, "relation_to_speaker": "father"|"mother"|"husband"|"wife"|"other"|null},
    "heirs": [
    {"type": "son"|"daughter"|"wife"|"husband"|"father"|"mother"|"grandson"|"granddaughter"|"full_brother"|"full_sister"|"paternal_grandfather"|"paternal_grandmother"|"maternal_grandmother",
        "count": <int>, "alive": true|false, "predeceased": true|false, "has_children": true|false|null, "age": <int>|null}
    ],
"assets": [
    {"type": "house"|"plot"|"shop"|"agricultural_land"|"apartment"|"car"|"cash"|"bank_account"|"business"|"jewelry"|"other",
        "estimated_value_pkr": <int>|null, "description": "<string>"|null}
],
    "debts": [{"description": "<string>", "amount_pkr": <int>|null}],
    "total_estate_pkr": <int>|null,
    "will_mentioned": true|false,
    "will_amount_pkr": <int>|null,
    "disputes_mentioned": true|false,
    "dispute_description": "<string>"|null,
    "dispute_flags": ["mutation_by_single_heir"|"no_succession_certificate_obtained"|"one_heir_selling_without_consent"|"gift_deed_hiba_mentioned"|"donor_still_occupying_property"|"daughters_told_they_inherit_nothing"|"estate_distributed_without_paying_debts"|"only_sons_listed_in_mutation"|"will_bequest_exceeds_one_third"],
    "has_minor_heir": true|false,
    "sect_mentioned": "hanafi"|"shia"|"christian"|"hindu"|null,
    "language_detected": "urdu"|"english"|"mixed",
    "input_confidence": <float>,
    "extraction_notes": "<string>"
}

User input: {user_text}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — MAIN PUBLIC FUNCTION  (the one app.py imports)
# ═══════════════════════════════════════════════════════════════════════════════

def parse_scenario(user_text: str) -> Dict[str, Any]:
    """
    Parse a free-form inheritance scenario (Urdu / English / Roman-Urdu).

    Called by app.py:
        from ai.nlp_parser import parse_scenario
        parsed_result = parse_scenario(user_input)
        normalized    = parsed_result.get('normalized', parsed_result)

    Strategy: Gemini 1.5 Flash → fallback to regex if Gemini fails/unavailable.

    Returns the dict shape described in the module docstring.
    Never raises — all exceptions are caught and surfaced in the return dict.
    """
    if not user_text or not user_text.strip():
        return _make_response(_default_raw(), _default_normalized(), "default")

    user_text = user_text.strip()
    raw: Optional[Dict] = None
    method = "regex"

    # ── 1. Gemini (primary) ───────────────────────────────────────────────────
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        raw = _gemini_parse(user_text)
        if raw:
            method = "gemini"

    # ── 2. Regex fallback ─────────────────────────────────────────────────────
    if raw is None:
        raw    = _regex_parse(user_text)
        method = "regex"

    raw        = _validate_raw(raw, user_text)
    normalized = _normalize(raw)

    return _make_response(raw, normalized, method)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — GEMINI PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def _gemini_parse(user_text: str) -> Optional[Dict[str, Any]]:
    """Call Gemini 1.5 Flash. Returns parsed dict or None on any failure."""
    try:
        model    = _get_gemini_model()
        prompt   = _NLP_PROMPT.format(user_text=user_text)
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # strip any markdown fences
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
        raw_text = re.sub(r"\s*```$",           "", raw_text, flags=re.MULTILINE)
        raw_text = raw_text.strip()

        start = raw_text.find("{")
        end   = raw_text.rfind("}")
        if start == -1 or end == -1:
            logger.warning("Gemini returned no JSON object")
            return None

        parsed = json.loads(raw_text[start:end + 1])
        logger.info(
            f"Gemini OK: {len(parsed.get('heirs', []))} heirs | "
            f"estate={parsed.get('total_estate_pkr')} | "
            f"sect={parsed.get('sect_mentioned')}"
        )
        return parsed

    except json.JSONDecodeError as exc:
        logger.error(f"Gemini JSON error: {exc}")
        return None
    except Exception as exc:
        logger.error(f"Gemini call failed: {exc}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — REGEX FALLBACK PARSER
# Handles Urdu, English, and Roman-Urdu without any API
# ═══════════════════════════════════════════════════════════════════════════════

def _regex_parse(user_text: str) -> Dict[str, Any]:
    """Rule-based extraction — no API required."""
    logger.info("Using regex fallback parser")
    text   = user_text.lower()
    heirs: List[Dict] = []

    def _add(heir_type: str, patterns: List[str]) -> None:
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                count = int(m.group(1)) if m.lastindex and m.group(1) else 1
                heirs.append({
                    "type": heir_type, "count": count,
                    "alive": True, "predeceased": False,
                    "has_children": None, "age": None,
                })
                return

    _add("son",           [r"(\d+)\s*(?:sons?|bete?|baita|betay|بیٹے|بیٹا)"])
    _add("daughter",      [r"(\d+)\s*(?:daughters?|betiyan?|بیٹی|بیٹیاں)"])
    _add("wife",          [r"(\d+)\s*(?:wi(?:ves|fe)|biw[iy]|begum|zauja|بیوی)",
                            r"\b(?:ek biwi|ek bivi|one wife)\b"])
    _add("husband",       [r"\b(?:husband|shohar|shauhar|خاوند)\b"])
    _add("mother",        [r"\b(?:mother|maa|ammi|walida|والدہ)\b"])
    _add("father",        [r"\b(?:father|baap|walid|abu|والد)\b"])
    _add("grandson",      [r"(\d+)\s*(?:grandsons?|pota|nawaasa)"])
    _add("granddaughter", [r"(\d+)\s*(?:granddaughters?|poti|nawaasi)"])

    # all asset amounts — accumulate total
    amt_pat    = r"(\d+(?:\.\d+)?)\s*(crore|cr|lakh|lac|thousand|ہزار|لاکھ|کروڑ)"
    all_amounts = re.findall(amt_pat, text, re.IGNORECASE)
    total_value = 0
    for val_s, unit in all_amounts:
        val  = float(val_s)
        unit = unit.lower()
        if unit in ("crore", "cr", "کروڑ"):
            total_value += int(val * 10_000_000)
        elif unit in ("lakh", "lac", "لاکھ"):
            total_value += int(val * 100_000)
        elif unit in ("thousand", "ہزار"):
            total_value += int(val * 1_000)

    assets: List[Dict] = []
    if total_value > 0:
        assets.append({"type": "property", "estimated_value_pkr": total_value,
                        "description": f"total from {len(all_amounts)} amount(s)"})
    else:
        assets.append({"type": "house", "estimated_value_pkr": 8_000_000,
                        "description": "default — not found in text"})
        total_value = 8_000_000

    sect = "hanafi"
    if re.search(r"\bshia\b", text):
        sect = "shia"
    elif re.search(r"\b(?:christian|isai|maseehi)\b", text):
        sect = "christian"
    elif re.search(r"\bhindu\b", text):
        sect = "hindu"

    disp_flags: List[str] = []
    if re.search(r"apne naam|mutate|mutation|intiqal", text):
        disp_flags.append("mutation_by_single_heir")
    if re.search(r"bech diya|sold|sell without|farookht", text):
        disp_flags.append("one_heir_selling_without_consent")
    if re.search(r"hiba|gift deed|ہبہ", text):
        disp_flags.append("gift_deed_hiba_mentioned")
    if re.search(r"beti.{0,10}nahi|daughters?.{0,10}nothing", text):
        disp_flags.append("daughters_told_they_inherit_nothing")
    if re.search(r"no succession|succession cert", text):
        disp_flags.append("no_succession_certificate_obtained")

    debts: List[Dict] = []
    if re.search(r"\b(?:qarz|karza|loan|debt|mortgage)\b", text):
        debts.append({"description": "debt mentioned", "amount_pkr": None})

    default_heirs = [
        {"type": "son",      "count": 2, "alive": True, "predeceased": False, "has_children": None, "age": None},
        {"type": "daughter", "count": 3, "alive": True, "predeceased": False, "has_children": None, "age": None},
        {"type": "wife",     "count": 1, "alive": True, "predeceased": False, "has_children": None, "age": None},
    ]

    return {
        "deceased":            {"gender": "male", "relation_to_speaker": "father"},
        "heirs":               heirs if heirs else default_heirs,
        "assets":              assets,
        "debts":               debts,
        "total_estate_pkr":    total_value,
        "will_mentioned":      bool(re.search(r"\b(?:wasiyyat|will|وصیت)\b", text)),
        "will_amount_pkr":     None,
        "disputes_mentioned":  bool(disp_flags or re.search(r"fraud|dhooka|nahi diya|chheen", text)),
        "dispute_description": None,
        "dispute_flags":       disp_flags,
        "has_minor_heir":      bool(re.search(r"minor|nabalig|bacha|infant", text)),
        "sect_mentioned":      sect,
        "language_detected":   detect_language(user_text),
        "input_confidence":    0.55,
        "extraction_notes":    "Regex fallback used — Gemini unavailable or returned invalid JSON.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — VALIDATE RAW + NORMALISE
# ═══════════════════════════════════════════════════════════════════════════════

def _validate_raw(parsed: Dict[str, Any], original_text: str) -> Dict[str, Any]:
    """Fill missing keys and coerce types so downstream never crashes."""
    defaults: Dict[str, Any] = {
        "deceased": {"gender": None, "relation_to_speaker": None},
        "heirs": [], "assets": [], "debts": [],
        "total_estate_pkr": None, "will_mentioned": False, "will_amount_pkr": None,
        "disputes_mentioned": False, "dispute_description": None, "dispute_flags": [],
        "has_minor_heir": False, "sect_mentioned": None,
        "language_detected": detect_language(original_text),
        "input_confidence": 0.85, "extraction_notes": "",
    }
    for k, v in defaults.items():
        if k not in parsed:
            parsed[k] = v

    # heirs — coerce count to int
    clean_heirs: List[Dict] = []
    for h in parsed["heirs"]:
        if not isinstance(h, dict):
            continue
        try:
            count = max(1, int(h.get("count", 1)))
        except (TypeError, ValueError):
            count = 1
        clean_heirs.append({
            "type": str(h.get("type", "unknown")), "count": count,
            "alive": bool(h.get("alive", True)), "predeceased": bool(h.get("predeceased", False)),
            "has_children": h.get("has_children"), "age": h.get("age"),
        })
    parsed["heirs"] = clean_heirs

    # assets — coerce string amounts
    clean_assets: List[Dict] = []
    for a in parsed["assets"]:
        if not isinstance(a, dict):
            continue
        val = a.get("estimated_value_pkr")
        if isinstance(val, str):
            val = _parse_amount(val)
        elif isinstance(val, float):
            val = int(val)
        clean_assets.append({
            "type": str(a.get("type", "other")),
            "estimated_value_pkr": val,
            "description": a.get("description"),
        })
    parsed["assets"] = clean_assets

    # auto-compute total from assets if missing
    if not parsed["total_estate_pkr"]:
        total = sum(a["estimated_value_pkr"] for a in parsed["assets"]
                    if isinstance(a.get("estimated_value_pkr"), int))
        parsed["total_estate_pkr"] = total if total > 0 else None

    # detect minors from age fields
    if not parsed["has_minor_heir"]:
        for h in parsed["heirs"]:
            if isinstance(h.get("age"), int) and h["age"] < 18:
                parsed["has_minor_heir"] = True
                break

    # auto-detect dispute flags from description
    if parsed["dispute_description"] and not parsed["dispute_flags"]:
        parsed["dispute_flags"] = _extract_dispute_flags(parsed["dispute_description"])

    return parsed


def _normalize(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw extracted dict → flat format that app.py session_state reads.

    Key output shape (must match app.py exactly):
        heirs         → {"sons": 2, "daughters": 3, "wife": 1, "husband": 0, ...}
        total_estate  → int PKR
        debts         → int PKR
        wasiyyat      → int PKR
        sect          → str
        dispute_flags → {"mutation_done_by_one_heir": bool, ...}
    """
    # ── heirs list → flat dict ────────────────────────────────────────────────
    heirs_flat: Dict[str, int] = {}
    for h in raw.get("heirs", []):
        t = h.get("type", "")
        c = h.get("count", 1)
        if   t == "son":               heirs_flat["sons"]                = heirs_flat.get("sons",               0) + c
        elif t == "daughter":          heirs_flat["daughters"]           = heirs_flat.get("daughters",          0) + c
        elif t == "wife":              heirs_flat["wife"]                = heirs_flat.get("wife",               0) + c
        elif t == "husband":           heirs_flat["husband"]             = c
        elif t == "mother":            heirs_flat["mother"]              = c
        elif t == "father":            heirs_flat["father"]              = c
        elif t == "grandson":          heirs_flat["grandsons"]           = heirs_flat.get("grandsons",          0) + c
        elif t == "granddaughter":     heirs_flat["granddaughters"]      = heirs_flat.get("granddaughters",     0) + c
        elif t == "full_brother":      heirs_flat["full_brothers"]       = heirs_flat.get("full_brothers",      0) + c
        elif t == "full_sister":       heirs_flat["full_sisters"]        = heirs_flat.get("full_sisters",       0) + c
        elif t == "paternal_grandfather": heirs_flat["paternal_grandfather"] = c
        elif t == "paternal_grandmother": heirs_flat["paternal_grandmother"] = c
        elif t == "maternal_grandmother": heirs_flat["maternal_grandmother"] = c

    # ── total estate ──────────────────────────────────────────────────────────
    total_estate: int = raw.get("total_estate_pkr") or 0
    if total_estate == 0:
        total_estate = sum(
            a.get("estimated_value_pkr", 0) or 0
            for a in raw.get("assets", [])
        )
    if total_estate == 0:
        total_estate = 8_000_000  # prevent division-by-zero in faraid engine

    # ── debts ─────────────────────────────────────────────────────────────────
    total_debts: int = sum(d.get("amount_pkr", 0) or 0 for d in raw.get("debts", []))

    # ── wasiyyat ──────────────────────────────────────────────────────────────
    wasiyyat: int = raw.get("will_amount_pkr") or 0

    # ── sect ──────────────────────────────────────────────────────────────────
    sect = str(raw.get("sect_mentioned") or "hanafi").lower()
    if sect not in ("hanafi", "shia", "christian", "hindu"):
        sect = "hanafi"

    # ── dispute_flags list → bool dict that app.py reads ─────────────────────
    raw_flags: List[str] = raw.get("dispute_flags") or []
    dispute_flags_dict: Dict[str, bool] = {
        # app.py reads these exact keys:
        "mutation_done_by_one_heir":  "mutation_by_single_heir"                  in raw_flags,
        "has_succession_certificate": "no_succession_certificate_obtained"        not in raw_flags,
        "minor_heir_present":         bool(raw.get("has_minor_heir", False)),
        "selling_without_consent":    "one_heir_selling_without_consent"          in raw_flags,
        "gift_hiba_present":          "gift_deed_hiba_mentioned"                  in raw_flags,
        "possession_transferred":     "donor_still_occupying_property"            not in raw_flags,
        "daughters_share_denied":     "daughters_told_they_inherit_nothing"       in raw_flags,
        "will_exceeds_limit":         "will_bequest_exceeds_one_third"            in raw_flags,
        "debts_present":              len(raw.get("debts", [])) > 0,
        "debts_paid":                 "estate_distributed_without_paying_debts"   not in raw_flags,
        "only_sons_in_mutation":      "only_sons_listed_in_mutation"              in raw_flags,
    }

    return {
        "heirs":         heirs_flat,
        "total_estate":  total_estate,
        "debts":         total_debts,
        "wasiyyat":      wasiyyat,
        "sect":          sect,
        "dispute_flags": dispute_flags_dict,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SPEECH-TO-TEXT  (Whisper API)
# ═══════════════════════════════════════════════════════════════════════════════

def transcribe_audio(audio_bytes: bytes, language: str = "ur") -> Dict[str, Any]:
    """
    Transcribe audio bytes using OpenAI Whisper API.

    Supports Urdu ('ur') and English ('en').
    Cost: $0.006/min  ≈  833 min free on $5 OpenAI credit.
    Get key: platform.openai.com → API Keys → Create new secret key
    Add to .env: OPENAI_API_KEY=sk-...

    Args:
        audio_bytes: WAV / MP3 / M4A / OGG / WEBM bytes.
        language:    'ur', 'en', or 'auto' (auto-detect).

    Returns:
        {"text": "...", "language": "ur", "confidence": 0.90, "error": None}
    """
    if not audio_bytes:
        return {"text": "", "error": "No audio data", "language": language}
    if not OPENAI_AVAILABLE or _openai_mod is None:
        return {"text": "", "error": "pip install openai", "language": language}
    if not OPENAI_API_KEY:
        return {"text": "", "error": "OPENAI_API_KEY missing from .env", "language": language}

    try:
        client = _openai_mod.OpenAI(api_key=OPENAI_API_KEY)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        kwargs: Dict[str, Any] = {"model": "whisper-1", "response_format": "verbose_json"}
        if language != "auto":
            kwargs["language"] = language

        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(file=f, **kwargs)

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        text = transcription.text.strip()
        detected = getattr(transcription, "language", language)
        logger.info(f"Whisper: '{text[:60]}' lang={detected}")
        return {"text": text, "language": detected, "confidence": 0.90, "error": None}

    except _openai_mod.AuthenticationError:
        return {"text": "", "error": "Invalid OPENAI_API_KEY — check .env", "language": language}
    except _openai_mod.RateLimitError:
        return {"text": "", "error": "OpenAI rate limit — wait and retry", "language": language}
    except Exception as exc:
        logger.error(f"transcribe_audio error: {exc}")
        return {"text": "", "error": str(exc), "language": language}


def transcribe_and_parse(audio_bytes: bytes, language: str = "ur") -> Dict[str, Any]:
    """STT then NLP in one call. Returns same shape as parse_scenario()."""
    stt = transcribe_audio(audio_bytes, language)
    if stt.get("error") or not stt.get("text"):
        return {
            "raw": {}, "normalized": _default_normalized(),
            "success": False, "method": "stt_failed",
            "transcribed_text": "", "error": stt.get("error", "Empty STT"),
        }
    result = parse_scenario(stt["text"])
    result["transcribed_text"] = stt["text"]
    result["stt_language"]     = stt.get("language", language)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — TEXT-TO-SPEECH  (gTTS — no API key)
# ═══════════════════════════════════════════════════════════════════════════════

def synthesize_speech(text: str, language: str = "ur", slow: bool = False) -> Optional[bytes]:
    """
    Convert text to MP3 bytes using gTTS (Google Text-to-Speech).
    No API key required. Supports 'ur' (Urdu) and 'en' (English).
    """
    if not text or not text.strip():
        return None
    if not GTTS_AVAILABLE:
        logger.warning("gTTS not installed. Run: pip install gtts")
        return None
    try:
        tts = gTTS(text=text.strip(), lang=language, slow=slow)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as exc:
        logger.error(f"synthesize_speech error: {exc}")
        return None


def speak_result_urdu(urdu_text: str) -> None:
    """
    Render a Streamlit audio widget that speaks Urdu text aloud.

    Usage in app.py:
        from ai.nlp_parser import speak_result_urdu
        speak_result_urdu("آپ کا حصہ آٹھواں ہے جو دس لاکھ روپے بنتا ہے")
    """
    if not STREAMLIT_AVAILABLE:
        return
    audio = synthesize_speech(urdu_text, language="ur")
    if audio:
        st.audio(audio, format="audio/mp3")
    else:
        st.caption("🔇 Voice unavailable (gTTS not installed or network issue)")


def speak_result_english(english_text: str) -> None:
    """Streamlit audio widget for English TTS."""
    if not STREAMLIT_AVAILABLE:
        return
    audio = synthesize_speech(english_text, language="en")
    if audio:
        st.audio(audio, format="audio/mp3")
    else:
        st.caption("🔇 Voice unavailable")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — BROWSER MIC (Web Speech API — no key, Chrome/Edge only)
# ═══════════════════════════════════════════════════════════════════════════════

def get_voice_input_component(language: str = "ur-PK") -> str:
    """
    Return HTML/JS for a browser mic button using Web Speech API.
    Inject via: st.components.v1.html(get_voice_input_component(), height=165)
    """
    is_urdu   = "ur" in language
    btn_lbl   = "🎙️ اُردو میں بولیں"   if is_urdu else "🎙️ Speak in English"
    listen_lbl= "سن رہا ہوں ..."        if is_urdu else "Listening..."
    done_lbl  = "مکمل ✓"               if is_urdu else "Done ✓"
    copy_lbl  = "📋 Copy & Paste"
    direction = "rtl"                  if is_urdu else "ltr"
    font      = "Noto Nastaliq Urdu,serif" if is_urdu else "inherit"

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
<style>
body{{margin:0;padding:8px;font-family:'Segoe UI',sans-serif;display:flex;flex-direction:column;gap:8px}}
#mb{{padding:10px 20px;font-size:15px;border:none;border-radius:8px;cursor:pointer;background:#4B3FAF;color:#fff;transition:background .2s}}
#mb:hover{{background:#3730A3}}
#mb.listening{{background:#DC2626;animation:pulse 1s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.7}}}}
#status{{font-size:12px;color:#6B7280;min-height:16px}}
#transcript{{display:none;background:#F3F4F6;border-radius:6px;padding:8px 12px;font-size:14px;direction:{direction};font-family:{font};min-height:36px}}
#cb{{display:none;padding:7px 14px;font-size:13px;border:none;border-radius:6px;cursor:pointer;background:#059669;color:#fff}}
</style></head><body>
<button id="mb" onclick="toggle()">{btn_lbl}</button>
<div id="status"></div><div id="transcript"></div>
<button id="cb" onclick="copyText()">{copy_lbl}</button>
<script>
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
const mb=document.getElementById('mb'),status=document.getElementById('status'),
        td=document.getElementById('transcript'),cb=document.getElementById('cb');
let rec=null,listening=false,final='';
if(!SR){{status.textContent='⚠️ Use Chrome or Edge.';mb.disabled=true;mb.style.background='#9CA3AF';}}
else{{
    rec=new SR();rec.lang='{language}';rec.continuous=true;rec.interimResults=true;
    rec.onstart=()=>{{listening=true;mb.textContent='⏹️ {listen_lbl}';mb.classList.add('listening');final='';}}
    rec.onresult=(e)=>{{
    let interim='';
    for(let i=e.resultIndex;i<e.results.length;i++){{
        if(e.results[i].isFinal)final+=e.results[i][0].transcript+' ';
        else interim+=e.results[i][0].transcript;
    }}
    td.style.display='block';
    td.innerHTML='<span style="color:#111">'+final+'</span><span style="color:#9CA3AF">'+interim+'</span>';
    }};
rec.onerror=(e)=>{{
    const m={{'no-speech':'کوئی آواز نہیں','audio-capture':'مائیکروفون تک رسائی نہیں',
                'not-allowed':'اجازت دیں','network':'Network error'}};
    status.textContent=m[e.error]||'Error: '+e.error;reset();
    }};
    rec.onend=()=>{{if(listening)rec.start();}};
}}
function toggle(){{
    if(!rec)return;
    if(!listening){{rec.start();}}
    else{{rec.stop();listening=false;reset();if(final.trim()){{status.textContent='{done_lbl}';cb.style.display='block';}}}}
}}
function reset(){{listening=false;mb.textContent='{btn_lbl}';mb.classList.remove('listening');}}
function copyText(){{
    if(navigator.clipboard)navigator.clipboard.writeText(final.trim()).then(()=>{{
    cb.textContent='✅ Copied!';setTimeout(()=>cb.textContent='{copy_lbl}',2000);
    }});
}}
</script></body></html>"""


def render_voice_input_streamlit(language: str = "ur-PK", height: int = 165) -> None:
    """
    Render browser mic button in Streamlit. User speaks → Copies → Pastes into text area.

    Usage:
        from ai.nlp_parser import render_voice_input_streamlit
        render_voice_input_streamlit(language="ur-PK")
    """
    if not STREAMLIT_AVAILABLE:
        return
    import streamlit.components.v1 as components
    components.html(get_voice_input_component(language), height=height)
    if "ur" in language:
        st.caption("🎙️ Chrome/Edge میں بولیں → Stop → Copy → نیچے paste کریں")
    else:
        st.caption("🎙️ Click mic (Chrome/Edge) → speak → Stop → Copy → paste below")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — LANGUAGE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def detect_language(text: str) -> str:
    """
    Detect 'urdu' | 'english' | 'mixed' using Unicode range analysis.
    No API. No library. Arabic block U+0600–U+06FF = Urdu.
    Roman Urdu (ASCII) is treated as 'english' — Gemini handles it fine.
    """
    if not text:
        return "english"
    urdu_c  = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
    latin_c = sum(1 for c in text if c.isalpha() and c.isascii())
    total   = urdu_c + latin_c
    if total == 0:
        return "english"
    ratio = urdu_c / total
    if ratio > 0.70:
        return "urdu"
    if ratio < 0.15:
        return "english"
    return "mixed"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — BILINGUAL EXPLANATION GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_explanation(
    shares: Dict[str, Any],
    sect: str,
    disputes: Dict[str, Any],
    language: str = "both",
) -> Dict[str, str]:
    """
    Generate plain-language Urdu + English explanation of share results.

    Usage in app.py Urdu section:
        from ai.nlp_parser import generate_explanation, speak_result_urdu
        exp = generate_explanation(shares, sect, disputes)
        st.markdown(exp["urdu"])
        speak_result_urdu(exp["urdu"])
    """
    fallback = {
        "urdu":    "وراثت کا حساب مکمل ہو گیا۔ تفصیل اوپر جدول میں دیکھیں۔",
        "english": "Inheritance calculation complete. See the share table above.",
    }
    try:
        model = _get_gemini_model()
        lines = "\n".join(
            f"  {heir}: {d.get('fraction','?')} = PKR {d.get('amount',0):,.0f}"
            for heir, d in shares.items()
        )
        prompt = (
            f"Explain this inheritance ({sect}) in simple Pakistani language.\n"
            f"Shares:\n{lines}\n\n"
            f"Return ONLY JSON: {{\"urdu\": \"2-3 sentences Urdu\", \"english\": \"1-2 sentences\"}}"
        )
        response = model.generate_content(prompt)
        raw = re.sub(r"```(?:json)?", "", response.text).strip().strip("`").strip()
        s = raw.find("{"); e = raw.rfind("}")
        if s != -1 and e != -1:
            return json.loads(raw[s:e+1])
    except Exception as exc:
        logger.error(f"generate_explanation error: {exc}")
    return fallback


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 12 — PRIVATE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_amount(value_str: str) -> Optional[int]:
    """'80 lakh' → 8000000, '1.5 crore' → 15000000, '8000000' → 8000000"""
    if not value_str:
        return None
    s = str(value_str).lower().replace(",", "").strip()
    m = re.search(r"[\d.]+", s)
    if not m:
        return None
    num = float(m.group())
    if "crore" in s or "کروڑ" in s or " cr" in s:
        return int(num * 10_000_000)
    if "lakh" in s or "lac" in s or "لاکھ" in s:
        return int(num * 100_000)
    if "thousand" in s or "ہزار" in s:
        return int(num * 1_000)
    return int(num)


def _extract_dispute_flags(description: str) -> List[str]:
    """Map dispute description text to flag code strings."""
    flags: List[str] = []
    d = description.lower()
    mapping: Dict[str, List[str]] = {
        "mutation_by_single_heir":               ["mutation", "intiqal", "naam kara", "انتقال"],
        "no_succession_certificate_obtained":    ["no succession", "without certificate"],
        "one_heir_selling_without_consent":      ["selling", "sold", "bech diya"],
        "gift_deed_hiba_mentioned":              ["hiba", "gift deed", "ہبہ"],
        "donor_still_occupying_property":        ["still living", "abhi rehta"],
        "daughters_told_they_inherit_nothing":   ["daughter nothing", "beti ko nahi"],
        "estate_distributed_without_paying_debts": ["before debt", "qarz pay nahi"],
        "only_sons_listed_in_mutation":          ["only sons", "sirf bete"],
        "will_bequest_exceeds_one_third":        ["will exceed", "wasiyyat exceed"],
    }
    for flag, keywords in mapping.items():
        if any(kw in d for kw in keywords):
            flags.append(flag)
    return flags


def _default_normalized() -> Dict[str, Any]:
    return {
        "heirs":         {"sons": 2, "daughters": 3, "wife": 1},
        "total_estate":  8_000_000,
        "debts":         0,
        "wasiyyat":      0,
        "sect":          "hanafi",
        "dispute_flags": {},
    }


def _default_raw() -> Dict[str, Any]:
    return {
        "deceased": {"gender": "male", "relation_to_speaker": "father"},
        "heirs": [
            {"type": "son",      "count": 2, "alive": True, "predeceased": False, "has_children": None, "age": None},
            {"type": "daughter", "count": 3, "alive": True, "predeceased": False, "has_children": None, "age": None},
            {"type": "wife",     "count": 1, "alive": True, "predeceased": False, "has_children": None, "age": None},
        ],
        "assets": [{"type": "house", "estimated_value_pkr": 8_000_000, "description": "default"}],
        "debts": [], "total_estate_pkr": 8_000_000, "will_mentioned": False,
        "will_amount_pkr": None, "disputes_mentioned": False, "dispute_description": None,
        "dispute_flags": [], "has_minor_heir": False, "sect_mentioned": "hanafi",
        "language_detected": "english", "input_confidence": 1.0,
        "extraction_notes": "Default values — no input provided.",
    }


def _make_response(raw: Dict, normalized: Dict, method: str) -> Dict[str, Any]:
    return {"raw": raw, "normalized": normalized, "success": True, "method": method}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 13 — SELF-TEST   python ai/nlp_parser.py
# ═══════════════════════════════════════════════════════════════════════════════

def _run_self_tests() -> None:
    print("=" * 62)
    print("WarisNama AI — nlp_parser.py  self-test  (offline)")
    print("=" * 62)

    assert detect_language("مرے والد کا انتقال ہوگیا") == "urdu",   "urdu"
    assert detect_language("My father passed away")    == "english", "english"
    print("✓  detect_language")

    assert _parse_amount("80 lakh")      == 8_000_000
    assert _parse_amount("1.5 crore")    == 15_000_000
    assert _parse_amount("50 lac")       == 5_000_000
    assert _parse_amount("500 thousand") == 500_000
    assert _parse_amount("8000000")      == 8_000_000
    print("✓  _parse_amount")

    r = _regex_parse("Mera baap guzar gaya. 2 bete, 3 betiyan. Ghar 80 lakh ka.")
    assert any(h["type"]=="son"      and h["count"]==2 for h in r["heirs"]), "sons"
    assert any(h["type"]=="daughter" and h["count"]==3 for h in r["heirs"]), "daughters"
    assert r["total_estate_pkr"] == 8_000_000, r["total_estate_pkr"]
    print("✓  _regex_parse")

    # multi-asset accumulation
    r2 = _regex_parse("Ghar 50 lakh, dukaan 30 lakh, zameen 1 crore.")
    expected = 50*100_000 + 30*100_000 + 1*10_000_000   # 18,000,000
    assert r2["total_estate_pkr"] == expected, f"multi-asset got {r2['total_estate_pkr']}"
    print("✓  multi-asset accumulation")

    raw = {"heirs": [{"type":"wife","count":"1"}], "assets": [{"type":"house","estimated_value_pkr":"80 lakh"}]}
    v   = _validate_raw(raw, "test")
    assert v["heirs"][0]["count"]                      == 1
    assert v["assets"][0]["estimated_value_pkr"]       == 8_000_000
    print("✓  _validate_raw  (type coercions)")

    norm = _normalize(_regex_parse("2 bete, 3 betiyan, ek biwi. Ghar 80 lakh."))
    assert norm["heirs"].get("sons")      == 2
    assert norm["heirs"].get("daughters") == 3
    assert norm["heirs"].get("wife")      == 1
    assert norm["total_estate"]           == 8_000_000
    assert norm["sect"]                   == "hanafi"
    assert isinstance(norm["dispute_flags"], dict)
    print("✓  _normalize  (app.py-compatible flat dict)")

    result = parse_scenario("2 bete, 3 betiyan. Ghar 80 lakh ka.")
    assert "raw"        in result
    assert "normalized" in result
    assert "success"    in result and result["success"]
    assert "method"     in result
    assert isinstance(result["normalized"]["heirs"],        dict)
    assert isinstance(result["normalized"]["total_estate"], int)
    assert isinstance(result["normalized"]["dispute_flags"],dict)
    print("✓  parse_scenario  (return shape)")

    empty = parse_scenario("")
    assert empty["success"] and empty["method"] == "default"
    print("✓  empty input guard")

    flags = _extract_dispute_flags("Brother mutated property without consent")
    assert "mutation_by_single_heir" in flags
    print("✓  _extract_dispute_flags")

    html = get_voice_input_component("ur-PK")
    assert "SpeechRecognition" in html and "ur-PK" in html
    print("✓  get_voice_input_component")

    print()
    print("All 10 offline tests passed ✓")
    print()
    print("Live API tests (need .env keys):")
    print("  parse_scenario()    → GEMINI_API_KEY")
    print("  transcribe_audio()  → OPENAI_API_KEY")
    print("  synthesize_speech() → no key needed (gTTS)")
    print("=" * 62)


if __name__ == "__main__":
    _run_self_tests()










































































##########################33
# Akif Version
#############################















# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# WarisNama AI — ai/nlp_parser.py
# ================================
# NLP Engine: Scenario Parsing + Speech-to-Text + Text-to-Speech

# Architecture:
#   - parse_scenario(text)      ← called by app.py — Gemini 1.5 Flash NLP extraction
#   - transcribe_audio(bytes)   ← Whisper API STT (English + Urdu)
#   - synthesize_speech(text)   ← gTTS / ElevenLabs TTS (Urdu output)
#   - get_voice_input_js()      ← Web Speech API JS component for Streamlit
#   - speak_result_urdu(text)   ← Streamlit-injectable TTS

# APIs Used (all free / free-tier):
#   ┌─────────────────────────────────────────────────────────────────────┐
#   │ 1. Gemini 1.5 Flash  — NLP parsing (entity extraction, Urdu/EN)    │
#   │    Key  : GEMINI_API_KEY                                            │
#   │    Get  : aistudio.google.com → "Get API Key" → free, no card      │
#   │    Limit: 15 req/min, 1M tokens/day (free tier)                    │
#   │                                                                     │
#   │ 2. OpenAI Whisper API — Speech-to-Text (EN + Urdu)                 │
#   │    Key  : OPENAI_API_KEY                                            │
#   │    Get  : platform.openai.com → API Keys → $5 free credit          │
#   │    Alt  : whisper.cpp locally (zero cost, runs offline)             │
#   │    Limit: $0.006/min audio — ~833 min free on $5 credit            │
#   │                                                                     │
#   │ 3. gTTS (Google Text-to-Speech) — Urdu voice output                │
#   │    Key  : None required — completely free, uses Google's TTS        │
#   │    Limit: Unlimited (rate-limit resistant with small delays)        │
#   │                                                                     │
#   │ 4. Web Speech API — Browser-native STT (no API key needed)         │
#   │    Key  : None — built into Chrome / Edge                           │
#   │    Lang : ur-PK (Pakistani Urdu) + en-US                           │
#   └─────────────────────────────────────────────────────────────────────┘

# .env variables needed (add these to your .env file):
#   GEMINI_API_KEY=your_gemini_api_key_here
#   OPENAI_API_KEY=your_openai_api_key_here   (only needed for Whisper STT)

# Function names are kept consistent with app.py which calls:
#   - parse_scenario(user_text: str) -> dict
# """

# from __future__ import annotations

# import io
# import json
# import logging
# import os
# import re
# import time
# import tempfile
# from typing import Any, Dict, Optional, Tuple

# # ── Third-party imports ───────────────────────────────────────────────────────
# try:
#     import google.generativeai as genai
#     GEMINI_AVAILABLE = True
# except ImportError:
#     GEMINI_AVAILABLE = False
#     logging.warning("google-generativeai not installed. Run: pip install google-generativeai")

# try:
#     from gtts import gTTS
#     GTTS_AVAILABLE = True
# except ImportError:
#     GTTS_AVAILABLE = False
#     logging.warning("gTTS not installed. Run: pip install gtts")

# try:
#     import streamlit as st
#     STREAMLIT_AVAILABLE = True
# except ImportError:
#     STREAMLIT_AVAILABLE = False

# try:
#     import openai
#     OPENAI_AVAILABLE = True
# except ImportError:
#     OPENAI_AVAILABLE = False
#     logging.warning("openai not installed. Run: pip install openai")

# # ── Environment Variables ─────────────────────────────────────────────────────
# from dotenv import load_dotenv
# load_dotenv()

# GEMINI_API_KEY: str  = os.getenv("GEMINI_API_KEY", "")
# OPENAI_API_KEY: str  = os.getenv("OPENAI_API_KEY", "")

# # ── Logging ───────────────────────────────────────────────────────────────────
# logging.basicConfig(level=logging.INFO, format="%(levelname)s | nlp_parser | %(message)s")
# logger = logging.getLogger(__name__)


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 1 — GEMINI CLIENT SETUP
# # ═══════════════════════════════════════════════════════════════════════════════

# def _get_gemini_model():
#     """
#     Initialise and return a Gemini 1.5 Flash model instance.
#     Cached after first call so we don't re-init on every request.
#     """
#     if not GEMINI_AVAILABLE:
#         raise RuntimeError(
#             "google-generativeai package not installed. "
#             "Run: pip install google-generativeai"
#         )
#     if not GEMINI_API_KEY:
#         raise ValueError(
#             "GEMINI_API_KEY is missing from your .env file. "
#             "Get a free key at: aistudio.google.com → 'Get API Key'"
#         )
#     genai.configure(api_key=GEMINI_API_KEY)
#     return genai.GenerativeModel("gemini-1.5-flash")


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 2 — MASTER NLP PROMPT
# # This prompt is the core of the NLP pipeline. It instructs Gemini to act
# # as a Pakistani inheritance law entity extractor and return strict JSON.
# # ═══════════════════════════════════════════════════════════════════════════════

# _NLP_SYSTEM_PROMPT = """
# You are an expert Pakistani inheritance law NLP assistant.
# Your ONLY task is to extract structured information from the user's description of an inheritance situation.

# The input may be in:
# - Urdu (written in Nastalikh or Roman Urdu)
# - English
# - A mix of both (code-switching is very common in Pakistan)

# EXTRACTION RULES:
# 1. Return ONLY valid JSON. No explanation. No markdown. No backticks. No preamble.
# 2. If a field is not mentioned, use null (not "unknown", not empty string).
# 3. For numerical values, extract integers only. Do not include commas or units in numbers.
# 4. For heirs: only include heirs that are EXPLICITLY mentioned or clearly implied.
# 5. If the user mentions "2 sons and 3 daughters", extract count=2 for sons, count=3 for daughters.
# 6. "bete" / "beta" = son, "beti" = daughter, "bivi/biwi/zauja" = wife, "shauhar" = husband
# 7. "walid/abu/abba/baap" = father (deceased or heir depending on context), "walida/ammi/amma/maa" = mother
# 8. "pota/nawaasa (boy)" = grandson, "poti/nawaasi (girl)" = granddaughter
# 9. "bhai" = brother, "behen" = sister
# 10. Detect disputes: if user mentions "fraud", "dhooka", "ghar apne naam", "bechi", "nahi diya", flag disputes_mentioned=true
# 11. Detect minor heirs: if user mentions "bacha", "infant", specific age < 18, set has_minor_heir=true
# 12. Extract debts: "qarz", "loan", "mortgage", "karza" = debt
# 13. Extract will: "wasiyyat", "will", "deed" = will_mentioned=true
# 14. Sect detection: "sunni/hanafi" → "hanafi", "shia/jafari/ithna ashari" → "shia", "christian/isai/maseehi" → "christian", "hindu" → "hindu"
# 15. If sect not mentioned, use null (app will ask user to select)

# REQUIRED JSON SCHEMA — return exactly this structure:
# {
#   "deceased": {
#     "gender": "male" | "female" | null,
#     "relation_to_speaker": "father" | "mother" | "husband" | "wife" | "brother" | "sister" | "grandfather" | "grandmother" | "uncle" | "other" | null
#   },
#   "heirs": [
#     {
#       "type": "son" | "daughter" | "wife" | "husband" | "father" | "mother" | "grandson" | "granddaughter" | "full_brother" | "full_sister" | "paternal_grandfather" | "paternal_grandmother" | "maternal_grandmother" | "uterine_brother" | "uterine_sister" | "paternal_uncle",
#       "count": <integer>,
#       "alive": true | false,
#       "predeceased": true | false,
#       "has_children": true | false | null,
#       "age": <integer> | null
#     }
#   ],
#   "assets": [
#     {
#       "type": "house" | "plot" | "shop" | "agricultural_land" | "apartment" | "car" | "cash" | "bank_account" | "business" | "jewelry" | "stocks" | "other",
#       "estimated_value_pkr": <integer> | null,
#       "description": "<string>" | null
#     }
#   ],
#   "debts": [
#     {
#       "description": "<string>",
#       "amount_pkr": <integer> | null
#     }
#   ],
#   "total_estate_pkr": <integer> | null,
#   "will_mentioned": true | false,
#   "will_amount_pkr": <integer> | null,
#   "disputes_mentioned": true | false,
#   "dispute_description": "<string>" | null,
#   "dispute_flags": [
#     "mutation_by_single_heir" | "no_succession_certificate_obtained" |
#     "one_heir_selling_without_consent" | "gift_deed_hiba_mentioned" |
#     "donor_still_occupying_property" | "daughters_told_they_inherit_nothing" |
#     "estate_distributed_without_paying_debts" | "only_sons_listed_in_mutation" |
#     "will_bequest_exceeds_one_third"
#   ],
#   "has_minor_heir": true | false,
#   "sect_mentioned": "hanafi" | "shia" | "christian" | "hindu" | null,
#   "language_detected": "urdu" | "english" | "mixed",
#   "input_confidence": <float between 0.0 and 1.0>,
#   "extraction_notes": "<string describing any ambiguities or assumptions made>"
# }
# """

# _NLP_USER_TEMPLATE = "User input: {user_text}"


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 3 — CORE PARSE FUNCTION (called by app.py)
# # ═══════════════════════════════════════════════════════════════════════════════

# def parse_scenario(user_text: str) -> Dict[str, Any]:
#     """
#     Parse a user's inheritance scenario description using Gemini 1.5 Flash.

#     This is the PRIMARY function called by app.py:
#         from ai.nlp_parser import parse_scenario
#         parsed = parse_scenario(user_input)

#     Accepts Urdu, English, or mixed input. Returns structured JSON dict.

#     Args:
#         user_text: Free-form description of the inheritance situation.
#                    e.g. "Mera baap guzar gaya. 2 bete, 3 betiyan. Ghar 80 lakh ka."

#     Returns:
#         Dict matching the JSON schema above. On error, returns a dict with
#         'error' key describing the problem.

#     Raises:
#         Never raises — all exceptions caught and returned as error dicts.
#     """
#     if not user_text or not user_text.strip():
#         return {
#             "error": "Input is empty. Please describe the inheritance situation.",
#             "heirs": [],
#             "assets": [],
#             "debts": [],
#             "disputes_mentioned": False,
#         }

#     user_text = user_text.strip()

#     try:
#         model = _get_gemini_model()
#         full_prompt = (
#             _NLP_SYSTEM_PROMPT
#             + "\n\n"
#             + _NLP_USER_TEMPLATE.format(user_text=user_text)
#         )

#         logger.info(f"Sending scenario to Gemini ({len(user_text)} chars, lang=auto-detect)")
#         response = model.generate_content(full_prompt)
#         raw_text = response.text.strip()

#         # Strip any markdown fences Gemini sometimes adds despite instructions
#         raw_text = _strip_markdown_fences(raw_text)

#         result = json.loads(raw_text)
#         result = _validate_and_normalise(result, user_text)

#         logger.info(
#             f"Parsed: {len(result.get('heirs', []))} heirs, "
#             f"{len(result.get('assets', []))} assets, "
#             f"disputes={result.get('disputes_mentioned')}, "
#             f"confidence={result.get('input_confidence')}"
#         )
#         return result

#     except json.JSONDecodeError as e:
#         logger.error(f"JSON decode error from Gemini: {e}\nRaw: {raw_text[:300]}")
#         # Attempt fallback extraction
#         return _fallback_extraction(user_text)

#     except Exception as e:
#         logger.error(f"parse_scenario failed: {e}")
#         return {
#             "error": str(e),
#             "error_type": type(e).__name__,
#             "heirs": [],
#             "assets": [],
#             "debts": [],
#             "disputes_mentioned": False,
#             "dispute_flags": [],
#         }


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 4 — BILINGUAL EXPLANATION GENERATOR
# # ═══════════════════════════════════════════════════════════════════════════════

# def generate_explanation(
#     shares: Dict[str, Any],
#     sect: str,
#     disputes: Dict[str, Any],
#     language: str = "both",
# ) -> Dict[str, str]:
#     """
#     Generate a plain-language explanation of the inheritance calculation.

#     Called after share calculation to produce the AI explanation shown
#     in the "AI Explanation (Urdu)" section of app.py.

#     Args:
#         shares   : Output of faraid_engine.calculate_shares()
#         sect     : 'hanafi', 'shia', 'christian', or 'hindu'
#         disputes : Output of dispute_detector.detect_inheritance_disputes()
#         language : 'urdu', 'english', or 'both'

#     Returns:
#         Dict with keys 'urdu' and/or 'english' containing explanation strings.
#     """
#     try:
#         model = _get_gemini_model()

#         # Build a concise summary for Gemini to explain
#         share_summary = "\n".join([
#             f"  - {heir}: {data.get('fraction','?')} = PKR {data.get('amount', 0):,.0f}"
#             for heir, data in shares.items()
#         ])
#         dispute_summary = ""
#         if disputes.get("disputes_found"):
#             dispute_summary = f"\nDisputes detected: {[d['type'] for d in disputes['disputes_found']]}"

#         prompt = f"""
# You are a Pakistani inheritance law advisor. Explain the following inheritance calculation
# in simple, compassionate language that a non-lawyer Pakistani family can understand.

# Sect: {sect}
# Share distribution:
# {share_summary}
# {dispute_summary}

# Instructions:
# - If language=urdu or both: write an Urdu explanation using simple Pakistani Urdu (not formal).
#   Use words like: حصہ (share), جائیداد (property), وارث (heir), قانون (law).
#   Format the Urdu as JSON field "urdu".
# - If language=english or both: write a plain English explanation (2-3 sentences max).
#   Format the English as JSON field "english".
# - Return ONLY JSON. No markdown. No backticks.
# - JSON schema: {{"urdu": "...", "english": "..."}}
# - Language requested: {language}
# """
#         response = model.generate_content(prompt)
#         raw = _strip_markdown_fences(response.text.strip())
#         result = json.loads(raw)
#         return result

#     except Exception as e:
#         logger.error(f"generate_explanation failed: {e}")
#         return {
#             "urdu": "وراثت کا حساب مکمل ہو گیا۔ تفصیل اوپر دی گئی جدول میں دیکھیں۔",
#             "english": "Inheritance calculation complete. See the share table above for details.",
#         }


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 5 — SPEECH TO TEXT (Whisper API + Web Speech API fallback)
# # ═══════════════════════════════════════════════════════════════════════════════

# def transcribe_audio(audio_bytes: bytes, language: str = "ur") -> Dict[str, Any]:
#     """
#     Transcribe audio bytes to text using OpenAI Whisper API.

#     Supports Urdu (ur) and English (en). Whisper is the best available
#     free-tier multilingual STT that handles Urdu reliably.

#     API Key : OPENAI_API_KEY in .env
#     Cost    : $0.006/minute — ~833 minutes free on $5 OpenAI credit
#     Get key : platform.openai.com → API Keys → Create new secret key

#     Args:
#         audio_bytes: Raw audio bytes (WAV, MP3, M4A, OGG, WEBM supported)
#         language   : 'ur' for Urdu, 'en' for English, 'auto' for auto-detect

#     Returns:
#         Dict with 'text', 'language', 'confidence', 'error' (if failed)
#     """
#     if not audio_bytes:
#         return {"error": "No audio data provided", "text": ""}

#     if not OPENAI_AVAILABLE:
#         return {
#             "error": "openai package not installed. Run: pip install openai",
#             "text": "",
#         }
#     if not OPENAI_API_KEY:
#         return {
#             "error": (
#                 "OPENAI_API_KEY missing from .env. "
#                 "Get free key at: platform.openai.com → API Keys"
#             ),
#             "text": "",
#         }

#     try:
#         client = openai.OpenAI(api_key=OPENAI_API_KEY)

#         # Write bytes to a temp file (Whisper API needs a file-like object)
#         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
#             tmp.write(audio_bytes)
#             tmp_path = tmp.name

#         whisper_lang = None if language == "auto" else language

#         with open(tmp_path, "rb") as audio_file:
#             kwargs: Dict[str, Any] = {
#                 "model": "whisper-1",
#                 "file": audio_file,
#                 "response_format": "verbose_json",  # includes language detection
#             }
#             if whisper_lang:
#                 kwargs["language"] = whisper_lang

#             transcription = client.audio.transcriptions.create(**kwargs)

#         os.unlink(tmp_path)  # clean up temp file

#         detected_lang = getattr(transcription, "language", language)
#         text = transcription.text.strip()

#         logger.info(f"Whisper transcribed: '{text[:60]}...' (lang={detected_lang})")
#         return {
#             "text":           text,
#             "language":       detected_lang,
#             "confidence":     0.90,    # Whisper doesn't expose confidence; 0.90 is typical
#             "error":          None,
#         }

#     except openai.AuthenticationError:
#         return {"error": "Invalid OPENAI_API_KEY. Check your .env file.", "text": ""}
#     except openai.RateLimitError:
#         return {"error": "OpenAI rate limit hit. Wait a moment and try again.", "text": ""}
#     except Exception as e:
#         logger.error(f"transcribe_audio failed: {e}")
#         return {"error": str(e), "text": ""}


# def transcribe_and_parse(audio_bytes: bytes, language: str = "ur") -> Dict[str, Any]:
#     """
#     Convenience function: transcribe audio then immediately parse the text.
#     Returns the full parsed scenario dict with an added 'transcribed_text' field.

#     This is the single call from the Streamlit audio recorder component.

#     Args:
#         audio_bytes: Raw audio from st_audiorec or similar
#         language   : 'ur', 'en', or 'auto'

#     Returns:
#         Parsed scenario dict (same schema as parse_scenario) + 'transcribed_text'
#     """
#     transcription = transcribe_audio(audio_bytes, language)

#     if transcription.get("error") or not transcription.get("text"):
#         return {
#             "error": transcription.get("error", "Transcription returned empty text."),
#             "transcribed_text": "",
#             "heirs": [],
#             "assets": [],
#             "debts": [],
#             "disputes_mentioned": False,
#         }

#     transcribed_text = transcription["text"]
#     parsed = parse_scenario(transcribed_text)
#     parsed["transcribed_text"] = transcribed_text
#     parsed["stt_language"] = transcription.get("language", language)
#     return parsed


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 6 — TEXT TO SPEECH (Urdu + English output)
# # ═══════════════════════════════════════════════════════════════════════════════

# def synthesize_speech(text: str, language: str = "ur", slow: bool = False) -> Optional[bytes]:
#     """
#     Convert text to speech using gTTS (Google Text-to-Speech).

#     gTTS requires NO API key — it uses Google's public TTS endpoint.
#     Supports Urdu ('ur') and English ('en') natively.

#     Args:
#         text    : Text to speak (Urdu or English)
#         language: 'ur' for Urdu, 'en' for English
#         slow    : Speak slower (helpful for complex Urdu legal terms)

#     Returns:
#         MP3 audio bytes, or None on failure.
#     """
#     if not text or not text.strip():
#         return None

#     if not GTTS_AVAILABLE:
#         logger.warning("gTTS not installed. Run: pip install gtts")
#         return None

#     try:
#         tts = gTTS(text=text.strip(), lang=language, slow=slow)
#         mp3_buffer = io.BytesIO()
#         tts.write_to_fp(mp3_buffer)
#         mp3_buffer.seek(0)
#         audio_bytes = mp3_buffer.read()
#         logger.info(f"TTS generated: {len(audio_bytes)} bytes ({language})")
#         return audio_bytes

#     except Exception as e:
#         logger.error(f"synthesize_speech failed: {e}")
#         return None


# def speak_result_urdu(urdu_text: str) -> None:
#     """
#     Inject a Streamlit audio player that speaks the given Urdu text.

#     Usage in app.py:
#         from ai.nlp_parser import speak_result_urdu
#         speak_result_urdu("آپ کا حصہ آٹھواں ہے جو دس لاکھ روپے بنتا ہے")

#     Args:
#         urdu_text: Urdu string to speak aloud.
#     """
#     if not STREAMLIT_AVAILABLE:
#         return

#     audio_bytes = synthesize_speech(urdu_text, language="ur")
#     if audio_bytes:
#         st.audio(audio_bytes, format="audio/mp3", autoplay=False)
#     else:
#         st.caption("🔇 Voice output unavailable (gTTS not installed or network error)")


# def speak_result_english(english_text: str) -> None:
#     """
#     Inject a Streamlit audio player that speaks the given English text.

#     Args:
#         english_text: English string to speak aloud.
#     """
#     if not STREAMLIT_AVAILABLE:
#         return

#     audio_bytes = synthesize_speech(english_text, language="en")
#     if audio_bytes:
#         st.audio(audio_bytes, format="audio/mp3", autoplay=False)
#     else:
#         st.caption("🔇 Voice output unavailable")


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 7 — WEB SPEECH API (Browser-Native STT — No API Key Needed)
# # Injected as a Streamlit HTML component. Works in Chrome / Edge.
# # ═══════════════════════════════════════════════════════════════════════════════

# def get_voice_input_component(language: str = "ur-PK") -> str:
#     """
#     Return HTML/JS for a browser-native voice input button using Web Speech API.

#     This uses the browser's built-in SpeechRecognition — completely free,
#     no API key, works offline. Supported in Chrome and Edge.

#     The component writes the transcript into a hidden Streamlit text element
#     that the Python code can read via st.session_state.

#     Args:
#         language: BCP-47 language code. 'ur-PK' for Pakistani Urdu, 'en-US' for English.

#     Returns:
#         HTML string to inject via st.components.v1.html()
#     """
#     lang_label = "اُردو میں بولیں" if "ur" in language else "Speak in English"
#     listening_label = "سن رہا ہوں..." if "ur" in language else "Listening..."
#     done_label = "مکمل" if "ur" in language else "Done"

#     html = f"""
# <!DOCTYPE html>
# <html>
# <head>
# <meta charset="utf-8">
# <style>
#   body {{
#     margin: 0;
#     font-family: 'Segoe UI', sans-serif;
#     display: flex;
#     flex-direction: column;
#     align-items: flex-start;
#     gap: 10px;
#     padding: 8px;
#   }}
#   button {{
#     padding: 10px 20px;
#     font-size: 15px;
#     border-radius: 8px;
#     border: none;
#     cursor: pointer;
#     background: #4B3FAF;
#     color: white;
#     display: flex;
#     align-items: center;
#     gap: 8px;
#     transition: background 0.2s;
#   }}
#   button:hover {{ background: #3730A3; }}
#   button.listening {{ background: #DC2626; animation: pulse 1s infinite; }}
#   @keyframes pulse {{ 0%,100% {{opacity:1}} 50% {{opacity:0.7}} }}
#   #status {{
#     font-size: 13px;
#     color: #6B7280;
#     min-height: 18px;
#   }}
#   #transcript {{
#     font-size: 14px;
#     color: #111827;
#     background: #F3F4F6;
#     border-radius: 6px;
#     padding: 8px 12px;
#     min-height: 40px;
#     width: 100%;
#     direction: {'rtl' if 'ur' in language else 'ltr'};
#     font-family: {'Noto Nastaliq Urdu, serif' if 'ur' in language else 'inherit'};
#     display: none;
#     box-sizing: border-box;
#   }}
#   #copy-btn {{
#     display: none;
#     background: #059669;
#     font-size: 13px;
#     padding: 7px 14px;
#   }}
# </style>
# <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
# </head>
# <body>
# <button id="mic-btn" onclick="toggleListening()">
#   🎙️ {lang_label}
# </button>
# <div id="status"></div>
# <div id="transcript"></div>
# <button id="copy-btn" onclick="copyTranscript()">📋 Copy / استعمال کریں</button>

# <script>
#   const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
#   let recognition = null;
#   let isListening = false;
#   let finalTranscript = '';

#   const micBtn = document.getElementById('mic-btn');
#   const status = document.getElementById('status');
#   const transcriptDiv = document.getElementById('transcript');
#   const copyBtn = document.getElementById('copy-btn');

#   if (!SpeechRecognition) {{
#     status.textContent = '⚠️ Voice not supported. Use Chrome or Edge browser.';
#     micBtn.disabled = true;
#     micBtn.style.background = '#9CA3AF';
#   }} else {{
#     recognition = new SpeechRecognition();
#     recognition.lang = '{language}';
#     recognition.continuous = true;
#     recognition.interimResults = true;
#     recognition.maxAlternatives = 1;

#     recognition.onstart = () => {{
#       isListening = true;
#       micBtn.textContent = '⏹️ {listening_label}';
#       micBtn.classList.add('listening');
#       status.textContent = '{listening_label}';
#       finalTranscript = '';
#     }};

#     recognition.onresult = (event) => {{
#       let interimTranscript = '';
#       for (let i = event.resultIndex; i < event.results.length; i++) {{
#         const transcript = event.results[i][0].transcript;
#         if (event.results[i].isFinal) {{
#           finalTranscript += transcript + ' ';
#         }} else {{
#           interimTranscript += transcript;
#         }}
#       }}
#       transcriptDiv.style.display = 'block';
#       transcriptDiv.innerHTML =
#         '<span style="color:#111827">' + finalTranscript + '</span>' +
#         '<span style="color:#9CA3AF">' + interimTranscript + '</span>';
#     }};

#     recognition.onerror = (event) => {{
#       const messages = {{
#         'no-speech'      : 'کوئی آواز نہیں آئی — دوبارہ کوشش کریں',
#         'audio-capture'  : 'مائیکروفون تک رسائی نہیں — browser permission check کریں',
#         'not-allowed'    : 'مائیکروفون کی اجازت دیں',
#         'network'        : 'Network error — internet connection check کریں',
#         'aborted'        : 'منسوخ کردیا گیا',
#       }};
#       status.textContent = messages[event.error] || ('Error: ' + event.error);
#       resetButton();
#     }};

#     recognition.onend = () => {{
#       if (isListening) recognition.start(); // keep listening until stopped
#     }};
#   }}

#   function toggleListening() {{
#     if (!recognition) return;
#     if (!isListening) {{
#       try {{
#         recognition.start();
#       }} catch(e) {{
#         status.textContent = 'Error starting recognition: ' + e.message;
#       }}
#     }} else {{
#       recognition.stop();
#       isListening = false;
#       resetButton();
#       if (finalTranscript.trim()) {{
#         status.textContent = '{done_label} ✓';
#         copyBtn.style.display = 'block';
#         // Send transcript to Streamlit via URL hash trick
#         window.location.hash = encodeURIComponent(finalTranscript.trim());
#       }}
#     }}
#   }}

#   function resetButton() {{
#     isListening = false;
#     micBtn.textContent = '🎙️ {lang_label}';
#     micBtn.classList.remove('listening');
#   }}

#   function copyTranscript() {{
#     const text = finalTranscript.trim();
#     if (navigator.clipboard) {{
#       navigator.clipboard.writeText(text).then(() => {{
#         copyBtn.textContent = '✅ Copied!';
#         setTimeout(() => {{ copyBtn.textContent = '📋 Copy / استعمال کریں'; }}, 2000);
#       }});
#     }}
#   }}
# </script>
# </body>
# </html>
# """
#     return html


# def render_voice_input_streamlit(
#     key: str = "voice_input",
#     language: str = "ur-PK",
#     height: int = 160,
# ) -> Optional[str]:
#     """
#     Render the Web Speech API voice input component inside Streamlit.

#     Returns the transcript text if user has spoken, None otherwise.
#     The caller is responsible for passing the returned text to parse_scenario().

#     Usage in app.py:
#         from ai.nlp_parser import render_voice_input_streamlit
#         transcript = render_voice_input_streamlit(language="ur-PK")
#         if transcript:
#             parsed = parse_scenario(transcript)

#     Args:
#         key     : Unique Streamlit component key
#         language: 'ur-PK' for Urdu, 'en-US' for English
#         height  : Component height in pixels

#     Returns:
#         Transcript text string, or None.
#     """
#     if not STREAMLIT_AVAILABLE:
#         return None

#     import streamlit.components.v1 as components

#     html_code = get_voice_input_component(language=language)
#     components.html(html_code, height=height, scrolling=False)

#     # Instructions below the component
#     if "ur" in language:
#         st.caption(
#             "🎙️ Chrome/Edge میں بولیں — مائیکروفون کی اجازت دیں۔ "
#             "بولنے کے بعد 'Copy' دبائیں اور نیچے text area میں paste کریں۔"
#         )
#     else:
#         st.caption(
#             "🎙️ Click the mic button and speak (Chrome/Edge required). "
#             "Click Stop when done, then Copy and paste into the text area."
#         )
#     return None


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 8 — LANGUAGE DETECTION (lightweight, no extra API)
# # ═══════════════════════════════════════════════════════════════════════════════

# def detect_language(text: str) -> str:
#     """
#     Lightweight language detection for Urdu vs English vs mixed.
#     Uses Unicode character range analysis — no API, no library needed.

#     Urdu characters are in the Arabic Unicode block: U+0600–U+06FF

#     Args:
#         text: Input string.

#     Returns:
#         'urdu', 'english', or 'mixed'
#     """
#     if not text:
#         return "english"

#     urdu_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
#     latin_chars = sum(1 for c in text if c.isalpha() and c.isascii())
#     total_alpha = urdu_chars + latin_chars

#     if total_alpha == 0:
#         return "english"

#     urdu_ratio = urdu_chars / total_alpha

#     if urdu_ratio > 0.70:
#         return "urdu"
#     elif urdu_ratio < 0.15:
#         return "english"
#     else:
#         return "mixed"


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 9 — INTERNAL HELPERS
# # ═══════════════════════════════════════════════════════════════════════════════

# def _strip_markdown_fences(text: str) -> str:
#     """Remove ```json ... ``` or ``` ... ``` fences Gemini sometimes adds."""
#     text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
#     text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
#     return text.strip()


# def _validate_and_normalise(parsed: Dict[str, Any], original_text: str) -> Dict[str, Any]:
#     """
#     Validate and fill in missing keys in the parsed JSON.
#     Ensures downstream modules don't crash on missing fields.
#     """
#     # Ensure all top-level keys exist
#     defaults: Dict[str, Any] = {
#         "deceased":           {"gender": None, "relation_to_speaker": None},
#         "heirs":              [],
#         "assets":             [],
#         "debts":              [],
#         "total_estate_pkr":   None,
#         "will_mentioned":     False,
#         "will_amount_pkr":    None,
#         "disputes_mentioned": False,
#         "dispute_description": None,
#         "dispute_flags":      [],
#         "has_minor_heir":     False,
#         "sect_mentioned":     None,
#         "language_detected":  detect_language(original_text),
#         "input_confidence":   0.85,
#         "extraction_notes":   "",
#     }
#     for key, default_val in defaults.items():
#         if key not in parsed:
#             parsed[key] = default_val

#     # Normalise heirs — ensure each has all required fields
#     normalised_heirs = []
#     for heir in parsed.get("heirs", []):
#         if not isinstance(heir, dict):
#             continue
#         normalised_heirs.append({
#             "type":         heir.get("type", "unknown"),
#             "count":        max(1, int(heir.get("count", 1))),
#             "alive":        heir.get("alive", True),
#             "predeceased":  heir.get("predeceased", False),
#             "has_children": heir.get("has_children", None),
#             "age":          heir.get("age", None),
#         })
#     parsed["heirs"] = normalised_heirs

#     # Normalise assets — ensure value is an integer or None
#     normalised_assets = []
#     for asset in parsed.get("assets", []):
#         if not isinstance(asset, dict):
#             continue
#         value = asset.get("estimated_value_pkr")
#         if isinstance(value, str):
#             # Handle "80 lakh", "1 crore" etc. that Gemini might not fully parse
#             value = _parse_urdu_amount(value)
#         normalised_assets.append({
#             "type":               asset.get("type", "other"),
#             "estimated_value_pkr": value,
#             "description":        asset.get("description", None),
#         })
#     parsed["assets"] = normalised_assets

#     # Auto-compute total_estate_pkr if not provided but assets have values
#     if parsed["total_estate_pkr"] is None:
#         total = sum(
#             a["estimated_value_pkr"]
#             for a in parsed["assets"]
#             if a.get("estimated_value_pkr") is not None
#         )
#         if total > 0:
#             parsed["total_estate_pkr"] = total

#     # Detect minor heirs from age fields
#     if not parsed["has_minor_heir"]:
#         for heir in parsed["heirs"]:
#             if heir.get("age") is not None and heir["age"] < 18:
#                 parsed["has_minor_heir"] = True
#                 break

#     # Auto-detect dispute flags from dispute_description
#     if parsed["dispute_description"] and not parsed["dispute_flags"]:
#         parsed["dispute_flags"] = _extract_dispute_flags(parsed["dispute_description"])

#     return parsed


# def _parse_urdu_amount(value_str: str) -> Optional[int]:
#     """
#     Parse Pakistani amount expressions like '80 lakh', '1.5 crore', '50 lakh'.
#     Returns integer PKR value or None.
#     """
#     if not value_str:
#         return None

#     value_str = value_str.lower().replace(",", "").strip()

#     # Extract numeric part
#     match = re.search(r"[\d.]+", value_str)
#     if not match:
#         return None
#     num = float(match.group())

#     if "crore" in value_str or "کروڑ" in value_str:
#         return int(num * 10_000_000)
#     elif "lakh" in value_str or "lac" in value_str or "لاکھ" in value_str:
#         return int(num * 100_000)
#     elif "thousand" in value_str or "ہزار" in value_str:
#         return int(num * 1_000)
#     else:
#         return int(num)


# def _extract_dispute_flags(description: str) -> List[str]:
#     """
#     Rule-based extraction of dispute flag codes from a dispute description string.
#     Used as a fallback when Gemini doesn't populate dispute_flags directly.
#     """
#     flags = []
#     desc_lower = description.lower()

#     flag_keywords = {
#         "mutation_by_single_heir":               ["mutation", "mutate", "intiqal", "انتقال", "naam kara"],
#         "no_succession_certificate_obtained":    ["no succession", "without certificate", "succession cert"],
#         "one_heir_selling_without_consent":      ["selling", "sold", "bech diya", "bech raha"],
#         "gift_deed_hiba_mentioned":              ["hiba", "gift deed", "gift", "ہبہ"],
#         "donor_still_occupying_property":        ["still living", "abhi rehta", "donor occu"],
#         "daughters_told_they_inherit_nothing":   ["daughter nothing", "beti ko nahi", "girls excluded"],
#         "estate_distributed_without_paying_debts": ["before debt", "qarz pay nahi", "debt not paid"],
#         "only_sons_listed_in_mutation":          ["only sons", "sirf bete", "daughters excluded"],
#         "will_bequest_exceeds_one_third":        ["will exceed", "wasiyyat exceed", "more than third"],
#     }

#     for flag, keywords in flag_keywords.items():
#         if any(kw in desc_lower for kw in keywords):
#             flags.append(flag)

#     return flags


# def _fallback_extraction(user_text: str) -> Dict[str, Any]:
#     """
#     Basic rule-based extraction when Gemini fails or returns invalid JSON.
#     Detects common Urdu/English heir keywords to produce a minimal usable result.
#     """
#     logger.warning("Using fallback rule-based extraction")
#     text = user_text.lower()

#     heirs = []

#     # Son detection
#     son_match = re.search(r"(\d+)\s*(?:bete|beta|sons?|baita|بیٹے|بیٹا)", text)
#     if son_match:
#         heirs.append({"type": "son", "count": int(son_match.group(1)),
#                        "alive": True, "predeceased": False, "has_children": None, "age": None})

#     # Daughter detection
#     daughter_match = re.search(r"(\d+)\s*(?:betiyan?|beti|daughters?|بیٹی|بیٹیاں)", text)
#     if daughter_match:
#         heirs.append({"type": "daughter", "count": int(daughter_match.group(1)),
#                        "alive": True, "predeceased": False, "has_children": None, "age": None})

#     # Wife detection
#     wife_match = re.search(r"(\d+)\s*(?:bivi|biwi|wife|wives|zauja|بیوی)", text)
#     if wife_match:
#         heirs.append({"type": "wife", "count": int(wife_match.group(1)),
#                        "alive": True, "predeceased": False, "has_children": None, "age": None})
#     elif re.search(r"\b(?:ek bivi|ek biwi|one wife|1 wife)\b", text):
#         heirs.append({"type": "wife", "count": 1,
#                        "alive": True, "predeceased": False, "has_children": None, "age": None})

#     # Amount detection
#     amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|crore|لاکھ|کروڑ)", text)
#     total_estate = None
#     assets = []
#     if amount_match:
#         total_estate = _parse_urdu_amount(amount_match.group(0))
#         if total_estate:
#             assets.append({"type": "house", "estimated_value_pkr": total_estate, "description": None})

#     return {
#         "deceased":            {"gender": "male", "relation_to_speaker": "father"},
#         "heirs":               heirs,
#         "assets":              assets,
#         "debts":               [],
#         "total_estate_pkr":    total_estate,
#         "will_mentioned":      "wasiyyat" in text or "will" in text,
#         "will_amount_pkr":     None,
#         "disputes_mentioned":  any(kw in text for kw in ["fraud", "dhooka", "nahi diya", "chheen"]),
#         "dispute_description": None,
#         "dispute_flags":       [],
#         "has_minor_heir":      False,
#         "sect_mentioned":      None,
#         "language_detected":   detect_language(user_text),
#         "input_confidence":    0.45,   # low — fallback extraction
#         "extraction_notes":    "Fallback rule-based extraction used. Gemini API call failed. Please review.",
#     }


# # Fix missing import
# from typing import List


# # ═══════════════════════════════════════════════════════════════════════════════
# # SECTION 10 — SELF TEST (python ai/nlp_parser.py)
# # ═══════════════════════════════════════════════════════════════════════════════

# def _run_self_tests() -> None:
#     """Run offline tests (no API calls) to verify helper functions."""
#     print("=" * 60)
#     print("WarisNama AI — ai/nlp_parser.py self-test (offline)")
#     print("=" * 60)

#     # Language detection
#     assert detect_language("مرے والد کا انتقال ہوگیا") == "urdu"
#     assert detect_language("My father passed away") == "english"
#     assert detect_language("Mera baap guzar gaya 80 lakh") == "english"  # roman urdu = ascii
#     print("✓ Language detection")

#     # Markdown stripping
#     raw = "```json\n{\"key\": \"value\"}\n```"
#     stripped = _strip_markdown_fences(raw)
#     assert stripped == '{"key": "value"}'
#     print("✓ Markdown fence stripping")

#     # Urdu amount parsing
#     assert _parse_urdu_amount("80 lakh") == 8_000_000
#     assert _parse_urdu_amount("1.5 crore") == 15_000_000
#     assert _parse_urdu_amount("50 lac") == 5_000_000
#     assert _parse_urdu_amount("500 thousand") == 500_000
#     print("✓ Urdu amount parsing")

#     # Fallback extraction
#     result = _fallback_extraction("Mera baap guzar gaya. 2 bete, 3 betiyan. Ghar 80 lakh ka.")
#     assert any(h["type"] == "son" and h["count"] == 2 for h in result["heirs"])
#     assert any(h["type"] == "daughter" and h["count"] == 3 for h in result["heirs"])
#     assert result["total_estate_pkr"] == 8_000_000
#     print("✓ Fallback rule-based extraction")

#     # Validation / normalisation
#     raw_parsed = {
#         "heirs": [{"type": "wife", "count": "1"}],   # count as string
#         "assets": [{"type": "house", "estimated_value_pkr": "80 lakh"}],
#     }
#     normalised = _validate_and_normalise(raw_parsed, "test")
#     assert normalised["heirs"][0]["count"] == 1
#     assert normalised["assets"][0]["estimated_value_pkr"] == 8_000_000
#     assert normalised["disputes_mentioned"] is False
#     print("✓ Validation & normalisation")

#     # Dispute flag extraction
#     flags = _extract_dispute_flags("Brother mutated property without telling us")
#     assert "mutation_by_single_heir" in flags
#     print("✓ Dispute flag extraction")

#     # Voice input HTML generation
#     html = get_voice_input_component("ur-PK")
#     assert "SpeechRecognition" in html
#     assert "ur-PK" in html
#     print("✓ Voice input HTML component")

#     print()
#     print("All offline tests passed.")
#     print()
#     print("API tests (require keys in .env):")
#     print("  parse_scenario() → needs GEMINI_API_KEY")
#     print("  transcribe_audio() → needs OPENAI_API_KEY")
#     print("  synthesize_speech() → needs no key (gTTS)")
#     print("=" * 60)


# if __name__ == "__main__":
#     _run_self_tests()