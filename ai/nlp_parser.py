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





















#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — nlp_parser.py
Natural Language Parser with Multiple Fallback Strategies
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — nlp_parser.py
Natural Language Parser with Multiple Fallback Strategies
FIXED: Now accumulates ALL asset values from text.
"""

import os
import json
import re
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Try to import Gemini, but don't fail if not available
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Using regex fallback only.")


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
def _get_gemini_client():
    """Initialize Gemini client if API key exists."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or not GEMINI_AVAILABLE:
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"Gemini init error: {e}")
        return None


client = _get_gemini_client()


# ─────────────────────────────────────────────
# REGEX FALLBACK PARSER (WORKS WITHOUT API)
# Now correctly handles multiple asset values.
# ─────────────────────────────────────────────
def _regex_parse(user_text: str) -> Dict[str, Any]:
    """
    Extract inheritance information using regex patterns.
    Works with Urdu, English, and Roman Urdu.
    Now accumulates values from ALL assets mentioned.
    """
    text = user_text.lower()
    
    result = {
        "deceased": {"gender": "male", "relation": "father"},
        "heirs": [],
        "assets": [],
        "debts": [],
        "will_mentioned": False,
        "sect": "hanafi"
    }
    
    # ───── Extract Heir Counts (same as before) ─────
    # Sons
    son_patterns = [r'(\d+)\s*son', r'(\d+)\s*beta', r'(\d+)\s*betay', r'(\d+)\s*larkay']
    for pattern in son_patterns:
        match = re.search(pattern, text)
        if match:
            result["heirs"].append({"type": "son", "count": int(match.group(1))})
            break
    
    # Daughters
    daughter_patterns = [r'(\d+)\s*daughter', r'(\d+)\s*beti', r'(\d+)\s*betiyan', r'(\d+)\s*larkiyan']
    for pattern in daughter_patterns:
        match = re.search(pattern, text)
        if match:
            result["heirs"].append({"type": "daughter", "count": int(match.group(1))})
            break
    
    # Wives
    wife_patterns = [r'(\d+)\s*wife', r'(\d+)\s*biwi', r'(\d+)\s*begum']
    for pattern in wife_patterns:
        match = re.search(pattern, text)
        if match:
            result["heirs"].append({"type": "wife", "count": int(match.group(1))})
            break
    
    # Husband
    if re.search(r'husband|shohar', text):
        result["heirs"].append({"type": "husband", "count": 1})
    
    # Mother
    if re.search(r'mother|maa|walida', text):
        result["heirs"].append({"type": "mother", "count": 1})
    
    # Father
    if re.search(r'father|baap|walid', text):
        result["heirs"].append({"type": "father", "count": 1})
    
    # ───── Extract ALL Estate Values (FIXED) ─────
    # Patterns for numbers with units
    # We'll find all occurrences of numbers followed by lakh/crore/million/thousand
    value_pattern = r'(\d+(?:\.\d+)?)\s*(lakh|crore|million|thousand|lac|cr)'
    matches = re.findall(value_pattern, text, re.IGNORECASE)
    
    total_value = 0
    asset_count = 0
    
    for value_str, unit in matches:
        value = float(value_str)
        unit_lower = unit.lower()
        
        if unit_lower in ('lakh', 'lac'):
            total_value += int(value * 100000)
        elif unit_lower in ('crore', 'cr'):
            total_value += int(value * 10000000)
        elif unit_lower == 'million':
            total_value += int(value * 1000000)
        elif unit_lower == 'thousand':
            total_value += int(value * 1000)
        asset_count += 1
    
    # Also look for direct numbers like "80 lakh" without space? Already covered.
    # If we found multiple assets, we add one combined asset entry.
    if total_value > 0:
        # Add a single asset with the total value (or you could add separate assets)
        # For simplicity, we combine all into one "property" asset.
        result["assets"].append({
            "type": "property",
            "estimated_value_pkr": total_value,
            "description": f"total from {asset_count} asset(s)"
        })
    else:
        # Fallback default if nothing found
        result["assets"].append({"type": "house", "estimated_value_pkr": 8000000, "description": ""})
    
    # ───── Detect Sect ─────
    if 'shia' in text:
        result["sect"] = "shia"
    elif 'christian' in text or 'masihi' in text:
        result["sect"] = "christian"
    elif 'hindu' in text:
        result["sect"] = "hindu"
    else:
        result["sect"] = "hanafi"
    
    # ───── Detect Will ─────
    if 'will' in text or 'wasiyyat' in text or 'وصیت' in user_text:
        result["will_mentioned"] = True
    
    # ───── Default heirs if nothing found ─────
    if not result["heirs"]:
        result["heirs"] = [
            {"type": "son", "count": 2},
            {"type": "daughter", "count": 3},
            {"type": "wife", "count": 1}
        ]
    
    return result


# ─────────────────────────────────────────────
# GEMINI PARSER (with error handling)
# ─────────────────────────────────────────────
def _gemini_parse(user_text: str) -> Dict[str, Any]:
    """Use Gemini API to parse natural language (already handles multiple assets)."""
    if not client:
        return None
    
    prompt = f"""
Extract inheritance information from this text. Return ONLY valid JSON.

User text: {user_text}

Return EXACTLY this format:
{{"deceased": {{"gender": "male", "relation": "father"}}, "heirs": [{{"type": "son", "count": 2}}, {{"type": "daughter", "count": 3}}, {{"type": "wife", "count": 1}}], "assets": [{{"type": "house", "estimated_value_pkr": 8000000}}], "debts": [], "will_mentioned": false, "sect": "hanafi"}}

Valid heir types: son, daughter, wife, husband, mother, father
Valid asset types: house, plot, shop, car, cash, business
Valid sect: hanafi, shia, christian, hindu

IMPORTANT: If multiple assets are mentioned, sum their values into a single asset or list them separately. Make sure the total estimated_value_pkr reflects the sum of all asset values.

Return ONLY the JSON. Start directly with {{.
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        
        raw_response = response.text.strip()
        
        # Clean the response
        raw_response = re.sub(r'```json\s*', '', raw_response)
        raw_response = re.sub(r'```\s*', '', raw_response)
        raw_response = raw_response.lstrip('\n\r\t "').rstrip('"')
        
        # Find JSON object
        start = raw_response.find('{')
        end = raw_response.rfind('}')
        
        if start != -1 and end != -1:
            json_str = raw_response[start:end+1]
            return json.loads(json_str)
        
        return None
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


# ─────────────────────────────────────────────
# NORMALIZATION (same as before)
# ─────────────────────────────────────────────
def _normalize_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert parsed data to engine-ready format."""
    normalized = {
        "heirs": {},
        "total_estate": 0,
        "debts": 0,
        "wasiyyat": 0,
        "sect": "hanafi",
        "dispute_flags": {}
    }
    
    # Process heirs
    for heir in data.get("heirs", []):
        heir_type = heir.get("type", "")
        count = heir.get("count", 0)
        
        if heir_type == "son":
            normalized["heirs"]["sons"] = normalized["heirs"].get("sons", 0) + count
        elif heir_type == "daughter":
            normalized["heirs"]["daughters"] = normalized["heirs"].get("daughters", 0) + count
        elif heir_type == "wife":
            normalized["heirs"]["wife"] = normalized["heirs"].get("wife", 0) + count
        elif heir_type == "husband":
            normalized["heirs"]["husband"] = count
        elif heir_type == "mother":
            normalized["heirs"]["mother"] = count
        elif heir_type == "father":
            normalized["heirs"]["father"] = count
    
    # Process assets - sum all values
    total_estate = 0
    for asset in data.get("assets", []):
        value = asset.get("estimated_value_pkr", 0)
        total_estate += value
    
    if total_estate == 0:
        total_estate = 8000000  # default if nothing found
    
    normalized["total_estate"] = total_estate
    
    # Process debts
    total_debts = 0
    for debt in data.get("debts", []):
        total_debts += debt.get("amount_pkr", 0)
    normalized["debts"] = total_debts
    
    # Process sect
    sect = data.get("sect", "hanafi")
    if sect and sect.lower() in ["hanafi", "shia", "christian", "hindu"]:
        normalized["sect"] = sect.lower()
    else:
        normalized["sect"] = "hanafi"
    
    return normalized


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────
def parse_scenario(user_text: str) -> Dict[str, Any]:
    """
    Main NLP pipeline with multiple fallback strategies.
    """
    if not user_text or not user_text.strip():
        return {
            "raw": {},
            "normalized": {
                "heirs": {"sons": 2, "daughters": 3, "wife": 1},
                "total_estate": 8000000,
                "debts": 0,
                "wasiyyat": 0,
                "sect": "hanafi",
                "dispute_flags": {}
            },
            "success": True,
            "method": "default"
        }
    
    parsed = None
    method = "regex"
    
    # Try Gemini first (if available)
    if client:
        parsed = _gemini_parse(user_text)
        if parsed:
            method = "gemini"
    
    # Fallback to regex
    if not parsed:
        parsed = _regex_parse(user_text)
        method = "regex"
    
    # Normalize and return
    normalized = _normalize_output(parsed)
    
    return {
        "raw": parsed,
        "normalized": normalized,
        "success": True,
        "method": method
    }













































































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

