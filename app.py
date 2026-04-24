#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
this is the app.py main file!
WarisNama AI – Main Streamlit Application
- Two modes: Inheritance Calculator (form/NLP) and AI Chatbot (Groq)
- All original features (shares, tax, disputes, documents, exports) preserved
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import re
import tempfile

from core.faraid_engine import calculate_shares
from core.dispute_detector import detect_inheritance_disputes
from core.tax_engine import calculate_all_heirs_tax
from core.process_navigator import get_succession_process
from ai.nlp_parser import parse_scenario
from core.knowledge_base import Province, FilerStatus

# PDF generators
from docs.pdf_builder import (
    generate_share_certificate_pdf,
    create_certificate_data_from_shares,
    generate_legal_notice_pdf,
    generate_fir_pdf
)
from docs.templates.legal_notice import get_legal_notice_data
from docs.templates.fir_draft import get_fir_data

# AI Chatbot
from ai.chatbot import InheritanceChatbot

st.set_page_config(page_title="WarisNama AI", page_icon="⚖️", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-text { font-family: 'Noto Nastaliq Urdu', serif; font-size: 1.2rem; direction: rtl; text-align: right; }
    .big-number { font-size: 2rem; font-weight: bold; color: #1f77b4; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ WarisNama AI")
st.caption("Intelligent Pakistani Inheritance Dispute Resolution | Urdu + English")
st.info("📚 **Sources:** Hanafi (Mulla's Mohammedan Law), Shia (Zafar & Associates), Christian (Succession Act 1925), Hindu (Hindu Succession Act 1956), Tax (FBR Finance Act 2025)")

# ======================================================================
# SESSION STATE INITIALISATION
# ======================================================================
if 'parsed' not in st.session_state:
    st.session_state['parsed'] = None

# Defaults for parsed values (used in NLP mode)
parsed_defaults = {
    'parsed_sons': 2, 'parsed_daughters': 3, 'parsed_wives': 1, 'parsed_husband': 0,
    'parsed_mother': 0, 'parsed_father': 0, 'parsed_total_estate': 10_000_000,
    'parsed_debts': 0, 'parsed_sect': 'hanafi', 'parsed_mutation': False,
    'parsed_no_cert': False, 'parsed_minor': False, 'parsed_forced_sale': False,
    'parsed_hiba': False, 'parsed_donor_possession': False, 'parsed_will_exceeds': False,
    'parsed_debts_not_paid': False
}
for key, default in parsed_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# For storing calculation results
if 'results' not in st.session_state:
    st.session_state.results = None
if 'results_ready' not in st.session_state:
    st.session_state.results_ready = False
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "📊 Inheritance Calculator"

# ======================================================================
# SIDEBAR – APP MODE SELECTION (with session state persistence)
# ======================================================================
st.sidebar.title("📝 WarisNama AI")
app_mode = st.sidebar.radio(
    "App Mode",
    ["📊 Inheritance Calculator", "💬 AI Chatbot"],
    index=0 if st.session_state.app_mode == "📊 Inheritance Calculator" else 1
)
# Update session state when user manually changes
if app_mode != st.session_state.app_mode:
    st.session_state.app_mode = app_mode
    st.rerun()

# ======================================================================
# MODE 1: INHERITANCE CALCULATOR (original functionality)
# ======================================================================
if st.session_state.app_mode == "📊 Inheritance Calculator":
    input_method = st.sidebar.radio("Input method", ["Form", "Natural Language (Urdu/English)","Voice Input"])
    # Track input source cleanly
    if input_method == "Form":
        st.session_state["input_source"] = "form"
    elif input_method == "Natural Language (Urdu/English)":
        st.session_state["input_source"] = "nlp"
    elif input_method == "Voice Input":
        st.session_state["input_source"] = "voice"

    # ---------- NATURAL LANGUAGE MODE ----------
    if input_method == "Natural Language (Urdu/English)":
        user_input = st.sidebar.text_area(
            "Describe the situation:", height=150,
            placeholder="میرے والد کا انتقال ہوگیا۔ 2 بیٹے، 3 بیٹیاں، ایک بیوی۔ گھر 80 لاکھ کا ہے۔"
        )
        if st.sidebar.button("Parse Scenario"):
            with st.spinner("Analyzing..."):
                try:
                    user_text = user_input.lower()

                    missing = []

                    # Check estate presence in USER TEXT (not parser)
                    # if not any(word in user_text for word in ["lakh", "lac", "million", "crore", "rs", "pkr"]):
                    #     missing.append("💰 Estate value")
                    
                    
                    # Detect numeric + value pattern (STRICT)
                    estate_pattern = re.search(r'\d+\s*(lakh|lac|million|crore|rs|pkr)', user_text)

                    if not estate_pattern:
                        missing.append("💰 Estate value")

                    # Check sect in USER TEXT
                    if not any(word in user_text for word in ["hanafi", "shia", "sunni", "christian", "hindu"]):
                        missing.append("🕌 Sect")

                    # Check heirs (basic safety)
                    if not any(word in user_text for word in ["son", "sons", "daughter", "daughters", "wife", "husband"]):
                        missing.append("👨‍👩‍👧‍👦 Heirs")

                    if missing:
                        st.error(f"❌ Missing: {', '.join(missing)}")
                        st.stop()
                    
                    parsed_result = parse_scenario(user_input)
                    st.session_state['nlp_full'] = parsed_result

                    normalized = parsed_result.get('normalized', {})
                    heirs = normalized.get('heirs', {})


                    # ✅ Populate session ONLY after validation
                    st.session_state['parsed_sons'] = heirs.get('sons', 0)
                    st.session_state['parsed_daughters'] = heirs.get('daughters', 0)
                    st.session_state['parsed_wives'] = heirs.get('wife', 0)
                    st.session_state['parsed_husband'] = heirs.get('husband', 0)
                    st.session_state['parsed_mother'] = heirs.get('mother', 0)
                    st.session_state['parsed_father'] = heirs.get('father', 0)
                    
                    # =====================================================
                    # 🧠 MULTI-ASSET FIX (ADD HERE) 
                    # =====================================================
                    values = re.findall(r'(\d+)\s*(lakh|lac|million|crore)', user_text)
                    multipliers = re.findall(r'(\d+)\s*(car|cars|plot|plots|house|houses)', user_text)

                    total = 0

                    for num, unit in values:
                        num = int(num)

                        if unit in ["lakh", "lac"]:
                            val = num * 100000
                        elif unit == "million":
                            val = num * 1000000
                        elif unit == "crore":
                            val = num * 10000000
                        else:
                            val = num

                        total += val

                        # Handle "each"
                        if "each" in user_text and multipliers and values:
                            count = int(multipliers[0][0])
                            last_value = total // len(values)
                            total = total - last_value + (last_value * count)

                        # Override parser ONLY if detected
                        if total > 0:
                            normalized['total_estate'] = total
                    

                        #st.session_state['parsed_total_estate'] = normalized.get('total_estate')
                        #-------------updated for property validation ----------------
                        parsed_estate = normalized.get('total_estate')
                    if not parsed_estate:
                        st.error("❌ Failed to extract estate value correctly.")
                        st.stop()

                    st.session_state['parsed_total_estate'] = parsed_estate
                    st.session_state['parsed_debts'] = normalized.get('debts', 0)
                    st.session_state['parsed_sect'] = normalized.get('sect')

                    dispute_flags = normalized.get('dispute_flags', {})
                    st.session_state['parsed_mutation'] = dispute_flags.get('mutation_done_by_one_heir', False)
                    st.session_state['parsed_no_cert'] = not dispute_flags.get('has_succession_certificate', True)
                    st.session_state['parsed_minor'] = dispute_flags.get('minor_heir_present', False)
                    st.session_state['parsed_forced_sale'] = dispute_flags.get('selling_without_consent', False)
                    st.session_state['parsed_hiba'] = dispute_flags.get('gift_hiba_present', False)
                    st.session_state['parsed_donor_possession'] = not dispute_flags.get('possession_transferred', True)
                    st.session_state['parsed_will_exceeds'] = dispute_flags.get('will_exceeds_limit', False)
                    st.session_state['parsed_debts_not_paid'] = (
                        dispute_flags.get('debts_present', False) and not dispute_flags.get('debts_paid', True)
                    )

                    st.success("✅ Parsed successfully!")

                    with st.expander("📋 Parsed Data Summary"):
                        st.json({k: v for k, v in st.session_state.items() if k.startswith('parsed_')})
                except Exception as e:
                    st.error(f"Error parsing: {e}")

        # Form for NLP mode (pre‑populated)
        with st.sidebar.form("nlp_form"):
            st.subheader("🕌 Deceased & Sect")
            default_sect = st.session_state.get('parsed_sect', 'hanafi')
            sect_index = ["hanafi","shia","christian","hindu"].index(default_sect) if default_sect in ["hanafi","shia","christian","hindu"] else 0
            sect = st.selectbox("Sect", ["hanafi","shia","christian","hindu"], index=sect_index)
            st.subheader("💰 Estate & Liabilities")
            total_estate = st.number_input("Total Estate (PKR)", value=st.session_state.parsed_total_estate, step=500_000)
            debts = st.number_input("Outstanding Debts (PKR)", value=st.session_state.parsed_debts)
            funeral = st.number_input("Funeral Expenses (PKR)", value=0)
            wasiyyat = st.number_input("Wasiyyat (Will amount, PKR)", value=0)
            st.subheader("👨‍👩‍👧‍👦 Heirs (counts)")
            col1, col2 = st.columns(2)
            with col1:
                sons = st.number_input("Sons", value=st.session_state.parsed_sons)
                daughters = st.number_input("Daughters", value=st.session_state.parsed_daughters)
                wives = st.number_input("Wives", value=st.session_state.parsed_wives)
            with col2:
                husband = st.number_input("Husband (0/1)", value=st.session_state.parsed_husband)
                mother = st.number_input("Mother (0/1)", value=st.session_state.parsed_mother)
                father = st.number_input("Father (0/1)", value=st.session_state.parsed_father)
            if sect == "christian":
                spouse_christian = st.number_input("Spouse (0/1)", 0,1,0)
                children_christian = st.number_input("Children count", 0,10,0)
            else:
                spouse_christian = children_christian = 0
            st.subheader("⚠️ Dispute Flags (optional)")
            mutation_single = st.checkbox("Mutation by single heir?", value=st.session_state.parsed_mutation)
            no_succession = st.checkbox("No succession certificate?", value=st.session_state.parsed_no_cert)
            minor = st.checkbox("Minor heir involved?", value=st.session_state.parsed_minor)
            forced_sale = st.checkbox("One heir wants sell, others refuse?", value=st.session_state.parsed_forced_sale)
            hiba = st.checkbox("Gift deed (Hiba) mentioned?", value=st.session_state.parsed_hiba)
            donor_possession = st.checkbox("Donor still in possession?", value=st.session_state.parsed_donor_possession)
            will_exceeds = st.checkbox("Will exceeds 1/3 of estate?", value=st.session_state.parsed_will_exceeds)
            debts_not_paid = st.checkbox("Estate distributed before paying debts?", value=st.session_state.parsed_debts_not_paid)
            submitted = st.form_submit_button("🔍 Calculate Shares & Taxes")
    
    # ---------- VOICE MODE ----------
    elif input_method == "Voice Input":
        st.sidebar.subheader("🎤 Voice Input")

        audio_file = st.sidebar.file_uploader(
            "Upload voice (wav/mp3)",
            type=["wav", "mp3"]
        )
        if audio_file and audio_file.type == "audio/mpeg":
            st.sidebar.warning("⚠️ MP3 may not be fully supported. Prefer WAV format.")

        if audio_file:
            st.sidebar.success("Audio uploaded!")

            with st.spinner("Transcribing..."):
                try:
                    from ai.nlp_parser import transcribe_audio  # your whisper func
                    text = transcribe_audio(audio_file)
                    # ✅ FIX 1: Convert UploadedFile → bytes
                    audio_bytes = audio_file.read()
                    transcription = transcribe_audio(audio_bytes)
                    
                    
                    if isinstance(transcription, dict):
                        if transcription.get("error"):
                            st.error(f"❌ Transcription failed: {transcription['error']}")
                            st.stop()
                        text = transcription.get("text", "")
                    else:
                        text = transcription
                    # 🚫 Empty speech guard
                    if not text.strip():
                        st.error("❌ Could not extract speech from audio.")
                        st.stop()
                    
                    st.sidebar.text_area("Transcribed Text", text, height=120)

                    if st.sidebar.button("Parse Voice Scenario"):
                        submitted = True
                        parsed_result = parse_scenario(text)

                        # ✅ IMPORTANT
                        st.session_state['nlp_full'] = parsed_result
                        normalized = parsed_result.get('normalized', {})
                        heirs = normalized.get('heirs', {})
                        
                        # ✅ STRICT VALIDATION
                        if not normalized.get("total_estate") or not normalized.get("sect"):
                            st.error("❌ Voice input incomplete. Please mention estate and sect.")
                            st.stop()

                        st.session_state['parsed_sons'] = heirs.get('sons', 0)
                        st.session_state['parsed_daughters'] = heirs.get('daughters', 0)
                        st.session_state['parsed_wives'] = heirs.get('wife', 0)
                        st.session_state['parsed_husband'] = heirs.get('husband', 0)
                        st.session_state['parsed_mother'] = heirs.get('mother', 0)
                        st.session_state['parsed_father'] = heirs.get('father', 0)

                        st.session_state['parsed_total_estate'] = normalized.get('total_estate')
                        st.session_state['parsed_debts'] = normalized.get('debts', 0)
                        st.session_state['parsed_sect'] = normalized.get('sect')

                        st.success("✅ Voice parsed successfully!")

                except Exception as e:
                    st.error(f"Voice processing failed: {e}")
    # ---------- FORM MODE (MANUAL) ----------
    else:
        with st.sidebar.form("manual_form"):
            st.subheader("🕌 Deceased & Sect")
            sect = st.selectbox("Sect", ["hanafi","shia","christian","hindu"])
            st.subheader("💰 Estate & Liabilities")
            total_estate = st.number_input("Total Estate (PKR)", value=10_000_000, step=500_000)
            debts = st.number_input("Outstanding Debts (PKR)", value=0)
            funeral = st.number_input("Funeral Expenses (PKR)", value=0)
            wasiyyat = st.number_input("Wasiyyat (Will amount, PKR)", value=0)
            st.subheader("👨‍👩‍👧‍👦 Heirs (counts)")
            col1, col2 = st.columns(2)
            with col1:
                sons = st.number_input("Sons", 0,10,2)
                daughters = st.number_input("Daughters", 0,10,3)
                wives = st.number_input("Wives", 0,4,1)
            with col2:
                husband = st.number_input("Husband (0/1)", 0,1,0)
                mother = st.number_input("Mother (0/1)", 0,1,0)
                father = st.number_input("Father (0/1)", 0,1,0)
            if sect == "christian":
                spouse_christian = st.number_input("Spouse (0/1)", 0,1,0)
                children_christian = st.number_input("Children count", 0,10,0)
            else:
                spouse_christian = children_christian = 0
            st.subheader("⚠️ Dispute Flags (optional)")
            mutation_single = st.checkbox("Mutation by single heir?")
            no_succession = st.checkbox("No succession certificate?")
            minor = st.checkbox("Minor heir involved?")
            forced_sale = st.checkbox("One heir wants sell, others refuse?")
            hiba = st.checkbox("Gift deed (Hiba) mentioned?")
            donor_possession = st.checkbox("Donor still in possession?")
            will_exceeds = st.checkbox("Will exceeds 1/3 of estate?")
            debts_not_paid = st.checkbox("Estate distributed before paying debts?")
            submitted = st.form_submit_button("🔍 Calculate Shares & Taxes")

    #----------------------------------------new version-----------------------------------
    submitted = False
    if submitted:
        # 🔹 Determine input source
        source = st.session_state.get("input_source", "form")

    # =========================================================
    # ✅ SOURCE: NLP / VOICE (STRICT MODE)
    # =========================================================
        if source in ["nlp", "voice"]:

            sect = st.session_state.get("parsed_sect")
            total_estate = st.session_state.get("parsed_total_estate")
            debts = st.session_state.get("parsed_debts", 0)
            funeral = 0
            wasiyyat = 0

            sons = st.session_state.get("parsed_sons", 0)
            daughters = st.session_state.get("parsed_daughters", 0)
            wives = st.session_state.get("parsed_wives", 0)
            husband = st.session_state.get("parsed_husband", 0)
            mother = st.session_state.get("parsed_mother", 0)
            father = st.session_state.get("parsed_father", 0)

            mutation_single = st.session_state.get("parsed_mutation", False)
            no_succession = st.session_state.get("parsed_no_cert", False)
            minor = st.session_state.get("parsed_minor", False)
            forced_sale = st.session_state.get("parsed_forced_sale", False)
            hiba = st.session_state.get("parsed_hiba", False)
            donor_possession = st.session_state.get("parsed_donor_possession", False)
            will_exceeds = st.session_state.get("parsed_will_exceeds", False)
            debts_not_paid = st.session_state.get("parsed_debts_not_paid", False)

        # 🚫 STRICT VALIDATION
            if not sect or not total_estate:
                st.error("❌ Missing required NLP/Voice data. Please re-parse scenario.")
                st.stop()

    # =========================================================
    # ✅ SOURCE: FORM (UNCHANGED BEHAVIOR)
    # =========================================================
        else:
        # (use values already coming from form inputs)
            pass

    # =========================================================
    # 🧠 BUILD HEIRS STRUCTURE (COMMON)
    # =========================================================
        if sect in ["hanafi", "shia"]:
            heirs = {
                'sons': sons,
                'daughters': daughters,
                'wife': wives,
                'husband': husband,
                'mother': mother,
                'father': father
            }

        elif sect == "christian":
            heirs = {
                'spouse': spouse_christian,
                'children': children_christian
            }

        else:  # hindu
            heirs = {
                'widow': wives,
                'sons': sons,
                'daughters': daughters
            }

    # =========================================================
    # 🧮 CALCULATE SHARES
    # =========================================================
        result = calculate_shares(
            sect,
            heirs,
            total_estate,
            debts=debts,
            funeral=funeral,
            wasiyyat=wasiyyat
        )

        if "error" in result:
            st.error(result["error"])
            st.stop()

        shares = result.get("shares", result)
        distributable = result.get("distributable_estate", total_estate - debts - funeral)

    # =========================================================
    # 🚨 DISPUTE DETECTION
    # =========================================================
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

        disputes = detect_inheritance_disputes(dispute_data)

    # =========================================================
    # 💰 TAX CALCULATION
    # =========================================================
        filer_map = {
            h: FilerStatus.FILER if 'son' in h else FilerStatus.NON_FILER
            for h in shares
        }

        tax_results = calculate_all_heirs_tax(
            heirs_shares=shares,
            filer_status_map=filer_map,
            full_property_value_pkr=total_estate,
            action="sell",
            province=Province.DEFAULT
        )

    # =========================================================
    # 💾 STORE RESULTS
    # =========================================================
        st.session_state.results = {
            "shares": shares,
            "disputes": disputes,
            "tax_results": tax_results,
            "total_estate": total_estate,
            "distributable": distributable,
            "debts": debts,
            "funeral": funeral,
            "wasiyyat": wasiyyat,
            "sect": sect,
            "minor": minor,
            "full_value": total_estate
        }

        st.session_state.results_ready = True

    # 🔁 Refresh UI
        st.rerun()

    # ---------- DISPLAY RESULTS (if present) ----------
    if st.session_state.results_ready and st.session_state.results:
        res = st.session_state.results
        shares = res["shares"]
        disputes = res["disputes"]
        tax_results = res["tax_results"]
        total_estate = res["total_estate"]
        distributable = res["distributable"]
        debts = res["debts"]
        funeral = res["funeral"]
        wasiyyat = res["wasiyyat"]
        sect = res["sect"]
        minor = res["minor"]

        # Estate summary
        st.subheader("📊 Estate Summary")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("💰 Total Estate", f"Rs {total_estate:,.0f}")
        c2.metric("📉 Total Deductions", f"Rs {debts + funeral + wasiyyat:,.0f}")
        c3.metric("🏦 Distributable", f"Rs {distributable:,.0f}")
        c4.metric("👨‍👩‍👧‍👦 Total Heirs", len(shares))
        st.divider()

        # Tabs
        tab1,tab2,tab3,tab4 = st.tabs(["📊 Shares", "💰 Tax", "🚨 Disputes", "📄 Documents"])

        with tab1:
            # Table
            table_data = []
            for heir, data in shares.items():
                tax_info = tax_results.get(heir, {})
                net_after = tax_info.get('net_after_all_taxes', data['amount'])
                pct = (data['amount'] / distributable * 100) if distributable > 0 else 0
                table_data.append({
                    "Heir": heir.replace('_',' ').title(),
                    "Fraction": data.get('fraction','N/A'),
                    "Amount (PKR)": f"Rs {data['amount']:,.0f}",
                    "Percentage": f"{pct:.1f}%",
                    "Net After Tax": f"Rs {net_after:,.0f}"
                })
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Pie chart
            pie_df = pd.DataFrame([{"Heir": h.replace('_',' ').title(), "Amount": d["amount"]} for h,d in shares.items()])
            fig = px.pie(pie_df, values="Amount", names="Heir", hole=0.4)
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

            # Heir cards
            st.subheader("👨‍👩‍👧‍👦 Detailed Heir Breakdown")
            cols = st.columns(min(4, len(shares)))
            for idx, (heir, data) in enumerate(shares.items()):
                with cols[idx % 4]:
                    tax = tax_results.get(heir, {})
                    pct = (data['amount'] / distributable * 100) if distributable > 0 else 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{heir.replace('_',' ').title()}</h4>
                        <p class="big-number">{data.get('fraction','N/A')}</p>
                        <p><b>Rs {data['amount']:,.0f}</b></p>
                        <p>{pct:.1f}% of estate</p>
                        <hr><p>📉 After Tax: <b>Rs {tax.get('net_after_all_taxes', data['amount']):,.0f}</b></p>
                    </div>
                    """, unsafe_allow_html=True)

        with tab2:
            tax_table = []
            for heir, tax in tax_results.items():
                tax_table.append({
                    "Heir": heir.replace('_',' ').title(),
                    "Share Value": f"Rs {tax.get('share_value_pkr',0):,.0f}",
                    "236C Tax": f"Rs {tax.get('advance_tax_236C',0):,.0f}",
                    "CGT": f"Rs {tax.get('cgt',0):,.0f}",
                    "Net After Tax": f"Rs {tax.get('net_after_all_taxes',0):,.0f}"
                })
            st.dataframe(pd.DataFrame(tax_table), use_container_width=True, hide_index=True)
            st.caption("📌 Tax per FBR Finance Act 2025, Section 236C (seller). Pakistan has no inheritance tax.")
            # Savings bar chart
            savings = [{"Heir": h.replace('_',' ').title(), "Savings": t.get('savings_if_filer',0)} for h,t in tax_results.items() if t.get('savings_if_filer',0) > 0]
            if savings:
                fig_sav = px.bar(pd.DataFrame(savings), x="Heir", y="Savings", title="Potential Savings if Filer", color="Savings")
                st.plotly_chart(fig_sav, use_container_width=True)

        with tab3:
            if disputes.get('total_patterns_detected',0) > 0:
                for d in disputes.get('disputes',[]):
                    st.error(f"**{d['pattern'].replace('_',' ').title()}** – Score {d['fraud_score']}")
                    st.write(f"Law: {d.get('law_sections',{})}")
                    for act in d.get('recommended_actions',[])[:3]:
                        st.write(f"• {act}")
            else:
                st.success("No disputes detected.")
            # Process navigator
            st.subheader("📜 Legal Process Navigator")
            process = get_succession_process(
                has_minor_heir=minor,
                has_dispute=(disputes.get('total_patterns_detected',0)>0),
                dispute_result=disputes,
                is_selling=False
            )
            for step in process.get('process_steps', []):
                with st.expander(step['name']):
                    st.write(f"**Authority:** {step.get('authority','')} | **Fee:** {step.get('fee','')} | **Time:** {step.get('time','')}")
                    st.info(step.get('note',''))

        with tab4:
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                first = list(shares.keys())[0] if shares else None
                if first:
                    cert = create_certificate_data_from_shares(
                        "Late Person", "[Father]", datetime.now().strftime("%Y-%m-%d"),
                        sect, distributable, shares, first, "XXXXX-XXXXXXX-X",
                        "[Father]", first.replace('_',' ').title(), "Inherited Property"
                    )
                    buf = io.BytesIO()
                    generate_share_certificate_pdf(cert, buffer=buf)
                    st.download_button("📑 Share Certificate", buf.getvalue(), "share_certificate.pdf", "application/pdf")
            with col_d2:
                if disputes.get('total_patterns_detected',0) > 0:
                    nlp_data = st.session_state.get("nlp_full", {})
                    raw = nlp_data.get("raw", {})
                    
                    notice = get_legal_notice_data()
                    top = disputes.get('disputes',[{}])[0]
                    # notice.update({
                    #     "noticee_name": "Opposing Heir", "client_name": "User",
                    #     "grievance_paras": [f"Opposing heir committed {top.get('pattern','fraud')}."],
                    #     "relief_demanded": [top.get('remedy','Legal action')]
                    # })
                    # new updated version with more details from NLP
                    notice.update({
                        "client_name": "User",

                        # ✅ Prefer NLP name, fallback to dispute/default
                        "noticee_name": raw.get("accused_name") or "Opposing Heir",

                        # ✅ Combine NLP + dispute insight
                        "grievance_paras": [
                        raw.get("description") or f"Opposing heir committed {top.get('pattern','fraud')}."
                        ],

                        # ✅ Keep dispute engine strength
                        "relief_demanded": [
                            top.get('remedy', 'Legal action')
                        ]
                    })
                    buf = io.BytesIO()
                    generate_legal_notice_pdf(notice, buffer=buf)
                    st.download_button("⚖️ Legal Notice", buf.getvalue(), "legal_notice.pdf", "application/pdf")
            with col_d3:
                if disputes.get('total_patterns_detected',0) > 0:
                    nlp_data = st.session_state.get("nlp_full", {})
                    raw = nlp_data.get("raw", {})
                    
                    
                    # new updated version with more details from NLP
                    fir = get_fir_data()

                    top = disputes.get('disputes', [{}])[0]

                    fir.update({
                        # ✅ Prefer NLP name
                        "accused_name": raw.get("accused_name") or "Opposing Heir",

                        # ✅ Combine NLP + dispute logic
                        "fir_narrative": raw.get("description") or \
                            f"Illegal act detected: {top.get('pattern','fraud')}.",

                        # ✅ Keep legal strength from dispute engine (fallback)
                        "offence_sections": top.get("law_sections", "420, 468 PPC")
                    })
                    buf = io.BytesIO()
                    generate_fir_pdf(fir, buffer=buf)
                    st.download_button("🚨 FIR Draft", buf.getvalue(), "fir_draft.pdf", "application/pdf")

        # Urdu explanation & exports
        with st.expander("📖 Urdu Explanation"):
            urdu_text = f"<div class='urdu-text'><p><b>مرحوم کی جائیداد کی تقسیم</b></p><p>کل جائیداد: {total_estate:,.0f} روپے</p>"
            for heir, data in shares.items():
                urdu_text += f"<p>• {heir.replace('_',' ').title()}: {data.get('fraction','N/A')} = {data['amount']:,.0f} روپے</p>"
            urdu_text += "<p><b>اہم نوٹ:</b> پاکستان میں انہریٹنس ٹیکس نہیں ہے۔</p></div>"
            st.markdown(urdu_text, unsafe_allow_html=True)

        st.subheader("📥 Export Options")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.download_button("📊 Shares as CSV", df.to_csv(index=False), "shares.csv", "text/csv")
        with col_e2:
            st.download_button("💰 Tax Report as CSV", pd.DataFrame(tax_table).to_csv(index=False), "tax_report.csv", "text/csv")
# ======================================================================
# MODE 2: AI CHATBOT
# ======================================================================
elif st.session_state.app_mode == "💬 AI Chatbot":
    st.header("💬 AI Legal Assistant – WarisNama Chatbot")
    st.markdown("Ask me anything about inheritance, fraud detection, or legal steps. I will help you build a complete scenario and then calculate shares.")

    # Lazy initialisation
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = InheritanceChatbot()
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Disclaimer (once)
    if not st.session_state.get("disclaimer_shown", False):
        st.info("⚠️ **Disclaimer:** WarisNama AI is not a law firm nor a substitute for a certified religious scholar (mufti/molvi). Always verify with a qualified professional.")
        st.session_state.disclaimer_shown = True

    if st.session_state.chatbot.client is None:
        st.error("❌ Groq API key not found. Please set GROQ_API_KEY in .streamlit/secrets.toml or environment variable.")
        st.stop()

    # Chat history display
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your question or describe your situation..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.chat(prompt)
                st.markdown(response)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})

        scenario = st.session_state.chatbot.get_scenario()
        if scenario:
            st.success("✅ I have extracted a complete inheritance scenario!")
            # REMOVED: st.json(scenario)  <--- JSON is no longer displayed
            if st.button("Calculate Shares from Chat", key="chat_calc"):
                # Run calculation
                heirs_input = scenario.get("heirs", {})
                result = calculate_shares(
                    scenario.get("sect", "hanafi"),
                    heirs_input,
                    scenario.get("total_estate", 0),
                    debts=scenario.get("debts", 0),
                    funeral=scenario.get("funeral", 0),
                    wasiyyat=scenario.get("wasiyyat", 0)
                )
                if result and "error" not in result:
                    shares_res = result.get("shares", result)
                    filer_map = {h: FilerStatus.FILER if 'son' in h else FilerStatus.NON_FILER for h in shares_res}
                    tax_res = calculate_all_heirs_tax(
                        heirs_shares=shares_res,
                        filer_status_map=filer_map,
                        full_property_value_pkr=scenario.get("total_estate", 0),
                        action="sell",
                        province=Province.DEFAULT
                    )
                    st.session_state.results = {
                        "shares": shares_res,
                        "disputes": {},
                        "tax_results": tax_res,
                        "total_estate": scenario.get("total_estate", 0),
                        "distributable": result.get("distributable_estate", scenario.get("total_estate",0) - scenario.get("debts",0) - scenario.get("funeral",0)),
                        "debts": scenario.get("debts", 0),
                        "funeral": scenario.get("funeral", 0),
                        "wasiyyat": scenario.get("wasiyyat", 0),
                        "sect": scenario.get("sect", "hanafi"),
                        "minor": scenario.get("dispute_flags", {}).get("heir_age_under_18", False),
                        "full_value": scenario.get("total_estate", 0)
                    }
                    st.session_state.results_ready = True
                    st.session_state.app_mode = "📊 Inheritance Calculator"
                    st.rerun()
                else:
                    st.error(f"Calculation error: {result.get('error', 'Unknown')}")