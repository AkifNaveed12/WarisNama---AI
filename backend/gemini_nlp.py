#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini NLP Module – extracts structured data from Urdu/English natural language.
Uses Google Gemini 1.5 Flash (free tier).
"""

import os
import json
import re
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please add to .env file")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

NLP_PROMPT = """
You are a Pakistani inheritance law assistant. Extract structured information from the user's description.
The input may be in Urdu, English, or a mix of both.
Return ONLY valid JSON. No explanation, no markdown backticks.

Extract these fields:
- deceased: {gender: "male"/"female", relation: "father"/"mother"/"husband"/"wife"/...}
- heirs: list of {type: "son"/"daughter"/"wife"/"husband"/"father"/"mother"/"grandson"/"granddaughter"/"brother"/"sister", count: integer, alive: true/false, predeceased: true/false}
- assets: list of {type: "house"/"plot"/"shop"/"agricultural_land"/"car"/"cash"/"business", estimated_value_pkr: integer, description: string}
- debts: list of {description: string, amount_pkr: integer}
- will_mentioned: boolean
- disputes_mentioned: boolean
- dispute_description: string or null
- sect_mentioned: "hanafi"/"shia"/"christian"/"hindu"/null

User input: {user_text}
"""


def clean_json_response(raw_response: str) -> str:
    """Clean markdown formatting from Gemini response."""
    raw_response = raw_response.strip()
    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]
    elif raw_response.startswith("```"):
        raw_response = raw_response[3:]
    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]
    return raw_response.strip()


def validate_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize extracted data."""
    if 'heirs' not in data or not isinstance(data['heirs'], list):
        data['heirs'] = []
    
    valid_heir_types = {'son', 'daughter', 'wife', 'husband', 'father', 'mother', 
                        'grandson', 'granddaughter', 'brother', 'sister'}
    for heir in data['heirs']:
        if heir.get('type') not in valid_heir_types:
            heir['type'] = 'unknown'
        if not isinstance(heir.get('count', 1), int) or heir.get('count', 1) < 1:
            heir['count'] = 1
        if 'alive' not in heir:
            heir['alive'] = True
        if 'predeceased' not in heir:
            heir['predeceased'] = False
    
    if 'assets' not in data or not isinstance(data['assets'], list):
        data['assets'] = []
    
    if 'debts' not in data or not isinstance(data['debts'], list):
        data['debts'] = []
    
    data['will_mentioned'] = data.get('will_mentioned', False)
    data['disputes_mentioned'] = data.get('disputes_mentioned', False)
    data['dispute_description'] = data.get('dispute_description')
    data['sect_mentioned'] = data.get('sect_mentioned')
    
    if 'deceased' not in data:
        data['deceased'] = {'gender': 'unknown', 'relation': 'unknown'}
    
    return data


def parse_scenario(user_text: str) -> Dict[str, Any]:
    """Parse natural language input into structured JSON."""
    if not user_text or not user_text.strip():
        raise ValueError("Empty input text provided")
    
    prompt = NLP_PROMPT.format(user_text=user_text)
    
    try:
        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Gemini returned empty response")
        
        cleaned = clean_json_response(response.text)
        data = json.loads(cleaned)
        validated_data = validate_extracted_data(data)
        validated_data['confidence'] = 0.85
        
        return validated_data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {e}")
    except Exception as e:
        raise ValueError(f"Gemini API error: {str(e)}")


def parse_scenario_with_fallback(user_text: str) -> Dict[str, Any]:
    """Parse with basic fallback if Gemini fails."""
    try:
        return parse_scenario(user_text)
    except Exception:
        return _basic_regex_extraction(user_text)


def _basic_regex_extraction(user_text: str) -> Dict[str, Any]:
    """Basic regex-based extraction as fallback."""
    result = {
        'deceased': {'gender': 'male', 'relation': 'father'},
        'heirs': [],
        'assets': [],
        'debts': [],
        'will_mentioned': False,
        'disputes_mentioned': False,
        'dispute_description': None,
        'sect_mentioned': None,
        'confidence': 0.5
    }
    
    text_lower = user_text.lower()
    
    # Son patterns
    son_match = re.search(r'(\d+)\s+bet[ae]', text_lower) or re.search(r'(\d+)\s+son', text_lower)
    if son_match:
        result['heirs'].append({'type': 'son', 'count': int(son_match.group(1)), 'alive': True, 'predeceased': False})
    elif re.search(r'bet[ae]', text_lower) or re.search(r'son', text_lower):
        result['heirs'].append({'type': 'son', 'count': 1, 'alive': True, 'predeceased': False})
    
    # Daughter patterns
    daughter_match = re.search(r'(\d+)\s+beti', text_lower)
    if daughter_match:
        result['heirs'].append({'type': 'daughter', 'count': int(daughter_match.group(1)), 'alive': True, 'predeceased': False})
    elif re.search(r'beti', text_lower):
        result['heirs'].append({'type': 'daughter', 'count': 1, 'alive': True, 'predeceased': False})
    
    # Wife pattern
    if re.search(r'biwi|wife', text_lower):
        result['heirs'].append({'type': 'wife', 'count': 1, 'alive': True, 'predeceased': False})
    
    # Asset value extraction
    value_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|crore)', text_lower)
    if value_match:
        value = float(value_match.group(1))
        if 'crore' in text_lower:
            value = value * 100
        result['assets'].append({
            'type': 'house',
            'estimated_value_pkr': int(value * 100000),
            'description': 'Property mentioned in input'
        })
    
    return result


if __name__ == "__main__":
    test_input = "Mera baap guzar gaya. Do beti hain, ek beta. Ghar 80 lakh ka."
    result = parse_scenario(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))