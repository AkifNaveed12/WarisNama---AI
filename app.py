#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WarisNama AI – Main Streamlit Application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from fractions import Fraction
import json
import os
from datetime import datetime

from core.faraid_engine import calculate_shares
from core.dispute_detector import detect_inheritance_disputes
from core.tax_engine import calculate_all_heirs_tax
from ai.doc_generator import (
    generate_inheritance_certificate_pdf,
    generate_legal_notice,
    generate_fir_draft
)
from core.process_navigator import get_succession_process
from ai.nlp_parser import parse_scenario
st.set_page_config(page_title="WarisNama AI", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-text {
        font-family: 'Noto Nastaliq Urdu', serif;
        font-size: 1.2rem;
        direction: rtl;
        text-align: right;
    }
    .reference-box {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ WarisNama AI")
st.caption("Intelligent Pakistani Inheritance Dispute Resolution | Urdu + English")
st.info("📚 **Sources:** Hanafi (Mulla's Mohammedan Law), Shia (Zafar & Associates), Christian (Succession Act 1925), Hindu (Hindu Succession Act 1956), Tax (FBR Finance Act 2025)")

# Sidebar
st.sidebar.title("📝 WarisNama AI")
input_method = st.sidebar.radio("Input method", ["Form", "Natural Language (Urdu/English)"])

if input_method == "Natural Language (Urdu/English)":
    user_input = st.sidebar.text_area("Describe the situation:", height=150,
                                        placeholder="میرے والد کا انتقال ہوگیا۔ 2 بیٹے، 3 بیٹیاں، ایک بیوی۔ گھر 80 لاکھ کا ہے۔")
    if st.sidebar.button("Parse Scenario"):
        with st.spinner("Analyzing..."):
            try:
                parsed = parse_scenario(user_input)
                st.session_state['parsed'] = parsed
                st.success("Scenario parsed! Please review and click Calculate.")
            except Exception as e:
                st.error(f"Error parsing: {e}")
    if 'parsed' in st.session_state:
        st.json(st.session_state['parsed'])
else:
    with st.sidebar.form("inheritance_form"):
        st.subheader("🕌 Deceased & Sect")
        st.markdown("🔹 **Select the sect/religion of the deceased** – this determines which inheritance law applies.")
        sect = st.selectbox("Sect / Religion", ["hanafi", "shia", "christian", "hindu"])
        
        st.subheader("💰 Estate & Liabilities")
        st.markdown("🔹 **Total Estate:** Value of all assets (house, land, cash, etc.)")
        total_estate = st.number_input("Total Estate (PKR)", min_value=0, value=10_000_000, step=500_000)
        st.markdown("🔹 **Outstanding Debts:** Any loans, bills, or liabilities of the deceased")
        debts = st.number_input("Outstanding Debts (PKR)", min_value=0, value=0)
        st.markdown("🔹 **Wasiyyat (Will):** Amount gifted to non-heirs (max 1/3 of estate after debts)")
        wasiyyat = st.number_input("Wasiyyat (Will amount, PKR)", min_value=0, value=0)
        
        st.subheader("👨‍👩‍👧‍👦 Heirs (counts)")
        st.markdown("🔹 Enter the number of living heirs in each category.")
        col1, col2 = st.columns(2)
        with col1:
            sons = st.number_input("Sons", min_value=0, value=2, help="Son's share is double that of a daughter")
            daughters = st.number_input("Daughters", min_value=0, value=3, help="Daughter gets half of son's share if both exist")
            wives = st.number_input("Wives", min_value=0, value=1, help="Multiple wives split the wife's share equally")
        with col2:
            husband = st.number_input("Husband (0/1)", min_value=0, max_value=1, value=0)
            mother = st.number_input("Mother (0/1)", min_value=0, max_value=1, value=0, help="Mother's share can be 1/6 or 1/3 depending on siblings")
            father = st.number_input("Father (0/1)", min_value=0, max_value=1, value=0, help="Father gets 1/6 plus residue")
        
        # For Christian
        if sect == "christian":
            spouse_christian = st.number_input("Spouse (0/1)", min_value=0, max_value=1, value=0)
            children_christian = st.number_input("Children count", min_value=0, value=0)
        else:
            spouse_christian = 0
            children_christian = 0
        
        st.subheader("⚠️ Dispute Flags (optional)")
        st.markdown("🔹 Check any that apply to detect fraud patterns.")
        mutation_single = st.checkbox("Mutation done by single heir?")
        no_succession = st.checkbox("No succession certificate?")
        minor = st.checkbox("Minor heir involved?")
        forced_sale = st.checkbox("One heir wants to sell, others refuse?")
        hiba = st.checkbox("Gift deed (Hiba) mentioned?")
        donor_possession = st.checkbox("Donor still in possession?")
        will_exceeds = st.checkbox("Will exceeds 1/3 of estate?")
        debts_not_paid = st.checkbox("Estate distributed before paying debts?")
        
        submitted = st.form_submit_button("🔍 Calculate Shares & Taxes")

# Main area
if input_method == "Form" and submitted:
    # Build heirs dict based on sect
    if sect == "hanafi":
        heirs = {'sons': sons, 'daughters': daughters, 'wife': wives,
                'husband': husband, 'mother': mother, 'father': father}
    elif sect == "shia":
        heirs = {'sons': sons, 'daughters': daughters, 'wife': wives,
                'husband': husband, 'mother': mother, 'father': father}
    elif sect == "christian":
        heirs = {'spouse': spouse_christian, 'children': children_christian}
    else:  # hindu
        heirs = {'widow': wives, 'sons': sons, 'daughters': daughters}

    shares = calculate_shares(sect, heirs, total_estate, debts, wasiyyat)
    if "error" in shares:
        st.error(shares["error"])
        st.stop()

    # Dispute data
    dispute_data = {
        'mutation_by_single_heir': mutation_single,
        'no_succession_certificate': no_succession,
        'one_heir_wants_sell': forced_sale,
        'others_refuse': forced_sale,
        'gift_deed_mentioned': hiba,
        'donor_still_in_possession': donor_possession,
        'will_mentioned': will_exceeds,
        'will_percentage': 50 if will_exceeds else 0,
        'debts_mentioned': debts > 0,
        'estate_distributed_before_debt': debts_not_paid,
        'heir_age_under_18': minor,
        'legal_guardian_appointed': False
    }
    disputes = detect_disputes(dispute_data)

    # Tax per heir (assuming sell)
    tax_results = {}
    for heir, data in shares.items():
        amount = data['amount']
        filer_status = 'filer' if 'son' in heir else 'non_filer'  # demo
        tax = calculate_heir_tax(amount, filer_status, 'sell')
        tax_results[heir] = tax

    # Results columns
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📊 Share Distribution")
        rows = []
        for heir, data in shares.items():
            rows.append({
                "Heir": heir,
                "Fraction": data['fraction'],
                "Amount (PKR)": f"Rs {data['amount']:,.0f}",
                "Net after Tax (if sell)": f"Rs {tax_results[heir]['net_after_tax']:,.0f}",
                "Source": data.get('reference', 'Islamic/Juridical rule')
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        
        with st.expander("📖 View legal references for each share"):
            for heir, data in shares.items():
                st.markdown(f"**{heir}:** {data.get('reference', 'Standard rule')}")
        
        # Pie chart
        fig = px.pie(df, values="Amount (PKR)", names="Heir", title="Inheritance Shares")
        st.plotly_chart(fig)

    with col2:
        st.subheader("⚠️ Dispute Analysis")
        if disputes['disputes_found']:
            st.error(f"Fraud Score: {disputes['fraud_score']}/100 – {disputes['severity'].upper()}")
            for d in disputes['disputes_found']:
                st.write(f"**{d['type'].replace('_',' ').title()}**")
                st.write(f"Law: {d.get('law','')}")
                st.write(f"Actions: {', '.join(d.get('actions',[]))}")
        else:
            st.success("No significant dispute patterns detected.")
        
        st.subheader("📜 Process Navigator")
        process = get_succession_process(minor_heir=minor, has_dispute=len(disputes['disputes_found'])>0)
        for step_key, step in process.items():
            with st.expander(f"{step['name']}"):
                st.write(f"**Authority:** {step['authority']}")
                st.write(f"**Fee:** {step['fee']}")
                st.write(f"**Documents:** {', '.join(step['documents'])}")
                st.write(f"**Time:** {step['time']}")
                if 'note' in step:
                    st.info(step['note'])

    # Tax summary
    st.subheader("💰 Tax Liability (if selling share)")
    tax_df = pd.DataFrame([
        {"Heir": heir, "Advance Tax (236C)": f"Rs {tax['advance_tax_236C']:,.0f}",
         "Net after Tax": f"Rs {tax['net_after_tax']:,.0f}"}
        for heir, tax in tax_results.items()
    ])
    st.dataframe(tax_df, use_container_width=True)
    st.caption("📌 Tax calculated as per FBR Finance Act 2025, Section 236C (seller). Pakistan has no inheritance tax.")

    # Document generation
    st.subheader("📄 Legal Documents")
    col_doc1, col_doc2, col_doc3 = st.columns(3)
    with col_doc1:
        if st.button("Generate Share Certificate (PDF)"):
            pdf_bytes = generate_inheritance_certificate_pdf(
                deceased_name="Late Person", sect=sect, total_estate=total_estate,
                debts=debts, wasiyyat=wasiyyat, shares=shares
            )
            st.download_button("Download PDF", data=pdf_bytes, file_name="inheritance_certificate.pdf", mime="application/pdf")
    with col_doc2:
        if disputes['disputes_found']:
            notice_text = generate_legal_notice(
                sender_name="User", deceased_name="Late Person",
                recipient_name="Opposing Heir", recipient_address="Address",
                fraud_description=disputes['disputes_found'][0]['type'],
                law_section=disputes['disputes_found'][0].get('law', 'Law'),
                remedy=disputes['disputes_found'][0].get('remedy', 'Remedy'),
                language='en'
            )
            st.text_area("Legal Notice Preview", notice_text, height=150)
            st.download_button("Download Notice", data=notice_text, file_name="legal_notice.txt")
    with col_doc3:
        if disputes['disputes_found'] and disputes['disputes_found'][0]['type'] == 'fraudulent_mutation':
            fir = generate_fir_draft(
                complainant_name="User", deceased_name="Late Person",
                accused_name="Opposing Heir", fraud_description="Fraudulent mutation",
                law_section="PPC 498A", accused_action="transferred property to own name",
                evidence_list="Succession certificate missing"
            )
            st.text_area("FIR Draft (Urdu)", fir, height=150)

    # Urdu explanation
    st.subheader("📖 AI Explanation (Urdu)")
    st.markdown('<div class="urdu-text">' +
                "مرحوم کی جائیداد قانونی وارثوں میں تقسیم کردی گئی۔ بیوی کا آٹھواں حصہ، بیٹوں کو بیٹیوں سے دوگنا حصہ ملا۔ اگر کوئی تنازع ہو تو قانونی نوٹس بھیجا جا سکتا ہے۔" +
                '</div>', unsafe_allow_html=True)