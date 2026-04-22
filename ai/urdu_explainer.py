#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WarisNama AI – Streamlit App (Fully Aligned Version)
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# CORE MODULES (FIXED IMPORTS)
from faraid_engine import calculate_shares
from dispute_detector import detect_inheritance_disputes
from tax_engine import calculate_all_heirs_tax
from doc_generator import (
    generate_inheritance_certificate_pdf,
    generate_legal_notice,
    generate_fir_draft
)
from process_navigator import get_succession_process
from nlp_parser import parse_scenario

st.set_page_config(page_title="WarisNama AI", page_icon="⚖️", layout="wide")

# ─────────────────────────────────────────────
# UI STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
.urdu-text {
    font-family: 'Noto Nastaliq Urdu', serif;
    font-size: 1.2rem;
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

st.title("⚖️ WarisNama AI")
st.caption("AI Inheritance System — Urdu + English")

# ─────────────────────────────────────────────
# INPUT MODE
# ─────────────────────────────────────────────
mode = st.sidebar.radio("Input Method", ["Form", "Natural Language"])

# ─────────────────────────────────────────────
# NLP MODE
# ─────────────────────────────────────────────
if mode == "Natural Language":
    user_input = st.sidebar.text_area("Describe scenario")

    if st.sidebar.button("Analyze"):
        parsed = parse_scenario(user_input)

        st.session_state["parsed"] = parsed
        st.success("Parsed successfully")

    if "parsed" in st.session_state:
        st.json(st.session_state["parsed"])

# ─────────────────────────────────────────────
# FORM MODE
# ─────────────────────────────────────────────
else:
    with st.sidebar.form("form"):

        sect = st.selectbox("Sect", ["hanafi", "shia", "christian", "hindu"])

        total_estate = st.number_input("Total Estate", value=10000000)
        debts = st.number_input("Debts", value=0)
        wasiyyat = st.number_input("Wasiyyat", value=0)

        sons = st.number_input("Sons", value=0)
        daughters = st.number_input("Daughters", value=0)
        wives = st.number_input("Wives", value=0)
        husband = st.number_input("Husband", value=0)
        mother = st.number_input("Mother", value=0)
        father = st.number_input("Father", value=0)

        # Dispute flags
        st.subheader("Disputes")
        mutation = st.checkbox("Single heir mutation")
        no_cert = st.checkbox("No succession certificate")
        forced_sale = st.checkbox("Forced sale")
        minor = st.checkbox("Minor heir")

        submit = st.form_submit_button("Calculate")

# ─────────────────────────────────────────────
# MAIN LOGIC
# ─────────────────────────────────────────────
if mode == "Form" and submit:

    # Build heirs
    heirs = {
        "sons": sons,
        "daughters": daughters,
        "wife": wives,
        "husband": husband,
        "mother": mother,
        "father": father
    }

    shares = calculate_shares(sect, heirs, total_estate, debts, wasiyyat)

    if "error" in shares:
        st.error(shares["error"])
        st.stop()

    # DISPUTE DETECTOR (NEW)
    dispute_flags = {
        "mutation_by_single_heir": mutation,
        "no_succession_certificate": no_cert,
        "one_heir_wants_sell": forced_sale,
        "others_refuse": forced_sale,
        "heir_age_under_18": minor
    }

    disputes = detect_inheritance_disputes(dispute_flags)

    # TAX ENGINE (FIXED)
    tax_results = calculate_all_heirs_tax(shares, {}, action="sell")

    # ─────────────────────────────────────────
    # DISPLAY
    # ─────────────────────────────────────────
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Shares")

        df = pd.DataFrame([
            {
                "Heir": h,
                "Amount": v["amount"],
                "Fraction": v["fraction"]
            }
            for h, v in shares.items()
        ])

        st.dataframe(df)

        fig = px.pie(df, values="Amount", names="Heir")
        st.plotly_chart(fig)

    with col2:
        st.subheader("⚠️ Disputes")

        if disputes["total_patterns_detected"] > 0:
            st.error(disputes["summary"])
        else:
            st.success("No disputes detected")

    # TAX
    st.subheader("💰 Tax")

    tax_df = pd.DataFrame([
        {
            "Heir": h,
            "Tax": t.get("total_tax", 0),
            "Net": t.get("net_after_tax", 0)
        }
        for h, t in tax_results.items()
    ])

    st.dataframe(tax_df)

    # PROCESS NAVIGATOR (FIXED)
    process = get_succession_process(
        has_minor_heir=minor,
        has_dispute=disputes["total_patterns_detected"] > 0,
        dispute_result=disputes
    )

    st.subheader("📜 Process")
    for step in process["steps"]:
        with st.expander(step["name"]):
            st.write(step)

    # DOCUMENTS
    st.subheader("📄 Documents")

    if st.button("Generate Certificate"):
        pdf = generate_inheritance_certificate_pdf(
            "Deceased",
            sect,
            total_estate,
            debts,
            wasiyyat,
            shares
        )
        st.download_button("Download", pdf, "certificate.pdf")

    if disputes["total_patterns_detected"] > 0:
        d = disputes["disputes"][0]

        notice = generate_legal_notice(
            "User", "Deceased", "Other Heir", "Address",
            d["pattern"], str(d.get("law_sections", "")), d.get("remedy", "")
        )

        st.text_area("Legal Notice", notice)

        fir = generate_fir_draft(
            "User", "Deceased", "Accused",
            d["pattern"], "PPC 498A", "Fraud", "Docs"
        )

        st.text_area("FIR", fir)

    # URDU (basic placeholder — next step Gemini)
    st.subheader("📖 Urdu Explanation")
    st.markdown('<div class="urdu-text">وراثت تقسیم کر دی گئی ہے۔</div>', unsafe_allow_html=True)