#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini NLP Module – extracts structured data from Urdu/English natural language.
Uses Google Gemini 1.5 Flash (free tier).
"""

import os
import json
import google.generativeai as genai

# Configure API key – set in environment or Streamlit secrets
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyAYAl3MmOwIgxZr1_72Qccn5r_pLnbQTTk"))
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

def parse_scenario(user_text: str) -> dict:
    """Parse natural language input into structured JSON."""
    prompt = NLP_PROMPT.format(user_text=user_text)
    response = model.generate_content(prompt)
    # Clean response – sometimes it returns markdown
    raw = response.text.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return json.loads(raw)