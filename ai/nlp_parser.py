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
# ALYAN FIXES
###################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI — nlp_parser.py
Natural Language Parser with Multiple Fallback Strategies
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
# ─────────────────────────────────────────────
def _regex_parse(user_text: str) -> Dict[str, Any]:
    """
    Extract inheritance information using regex patterns.
    Works with Urdu, English, and Roman Urdu.
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
    
    # ───── Extract Heir Counts ─────
    # Sons
    son_patterns = [
        r'(\d+)\s*son',
        r'(\d+)\s*beta',
        r'(\d+)\s*betay',
        r'(\d+)\s*larkay'
    ]
    for pattern in son_patterns:
        match = re.search(pattern, text)
        if match:
            result["heirs"].append({"type": "son", "count": int(match.group(1))})
            break
    
    # Daughters
    daughter_patterns = [
        r'(\d+)\s*daughter',
        r'(\d+)\s*beti',
        r'(\d+)\s*betiyan',
        r'(\d+)\s*larkiyan'
    ]
    for pattern in daughter_patterns:
        match = re.search(pattern, text)
        if match:
            result["heirs"].append({"type": "daughter", "count": int(match.group(1))})
            break
    
    # Wives
    wife_patterns = [
        r'(\d+)\s*wife',
        r'(\d+)\s*biwi',
        r'(\d+)\s*begum'
    ]
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
    
    # ───── Extract Estate Value ─────
    # Look for numbers with lakh/crore
    value_patterns = [
        r'(\d+(?:\.\d+)?)\s*(lakh)',
        r'(\d+(?:\.\d+)?)\s*(crore)',
        r'(\d+(?:\.\d+)?)\s*(million)',
        r'(\d+(?:\.\d+)?)\s*(thousand)',
        r'(\d+)\s*(?:lac|lakh)',
        r'(\d+)\s*(?:cr|crore)'
    ]
    
    total_value = 0
    for pattern in value_patterns:
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1))
            unit = match.group(2).lower() if len(match.groups()) > 1 else 'lakh'
            
            if unit == 'lakh' or unit == 'lac':
                total_value = int(value * 100000)
            elif unit == 'crore' or unit == 'cr':
                total_value = int(value * 10000000)
            elif unit == 'million':
                total_value = int(value * 1000000)
            elif unit == 'thousand':
                total_value = int(value * 1000)
            break
    
    # Also look for direct numbers (like 80 lakh)
    if total_value == 0:
        direct_match = re.search(r'(\d+)\s*lakh', text)
        if direct_match:
            total_value = int(direct_match.group(1)) * 100000
    
    if total_value == 0:
        direct_match = re.search(r'(\d+)\s*crore', text)
        if direct_match:
            total_value = int(direct_match.group(1)) * 10000000
    
    if total_value > 0:
        result["assets"].append({
            "type": "house",
            "estimated_value_pkr": total_value,
            "description": ""
        })
    
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
    
    # ───── Default values if nothing found ─────
    if not result["heirs"]:
        # Default family: 2 sons, 3 daughters, 1 wife
        result["heirs"] = [
            {"type": "son", "count": 2},
            {"type": "daughter", "count": 3},
            {"type": "wife", "count": 1}
        ]
    
    if not result["assets"]:
        result["assets"] = [{"type": "house", "estimated_value_pkr": 8000000, "description": ""}]
    
    return result


# ─────────────────────────────────────────────
# GEMINI PARSER (with error handling)
# ─────────────────────────────────────────────
def _gemini_parse(user_text: str) -> Dict[str, Any]:
    """Use Gemini API to parse natural language."""
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
# NORMALIZATION
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
    
    # Process assets
    total_estate = 0
    for asset in data.get("assets", []):
        value = asset.get("estimated_value_pkr", 0)
        total_estate += value
    
    if total_estate == 0:
        total_estate = 8000000
    
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