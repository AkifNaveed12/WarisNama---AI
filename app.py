#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WarisNama AI – Main Streamlit Application (Enhanced Visualizations)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
from core.knowledge_base import Province, FilerStatus

st.set_page_config(page_title="WarisNama AI", page_icon="⚖️", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-text {
        font-family: 'Noto Nastaliq Urdu', serif;
        font-size: 1.2rem;
        direction: rtl;
        text-align: right;
    }
    .big-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ WarisNama AI")
st.caption("Intelligent Pakistani Inheritance Dispute Resolution | Urdu + English")
st.info("📚 **Sources:** Hanafi (Mulla's Mohammedan Law), Shia (Zafar & Associates), Christian (Succession Act 1925), Hindu (Hindu Succession Act 1956), Tax (FBR Finance Act 2025)")

# Initialize session state for parsed values
if 'parsed' not in st.session_state:
    st.session_state['parsed'] = None

# Initialize all parsed form values with defaults
parsed_defaults = {
    'parsed_sons': 2,
    'parsed_daughters': 3,
    'parsed_wives': 1,
    'parsed_husband': 0,
    'parsed_mother': 0,
    'parsed_father': 0,
    'parsed_total_estate': 10_000_000,
    'parsed_debts': 0,
    'parsed_sect': 'hanafi',
    'parsed_mutation': False,
    'parsed_no_cert': False,
    'parsed_minor': False,
    'parsed_forced_sale': False,
    'parsed_hiba': False,
    'parsed_donor_possession': False,
    'parsed_will_exceeds': False,
    'parsed_debts_not_paid': False
}

for key, default in parsed_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Sidebar
st.sidebar.title("📝 WarisNama AI")
input_method = st.sidebar.radio("Input method", ["Form", "Natural Language (Urdu/English)"])

# ============================================================
# NATURAL LANGUAGE INPUT MODE (WITH AUTO-POPULATION)
# ============================================================
if input_method == "Natural Language (Urdu/English)":
    user_input = st.sidebar.text_area(
        "Describe the situation:", 
        height=150,
        placeholder="میرے والد کا انتقال ہوگیا۔ 2 بیٹے، 3 بیٹیاں، ایک بیوی۔ گھر 80 لاکھ کا ہے۔"
    )
    
    if st.sidebar.button("Parse Scenario"):
        with st.spinner("Analyzing..."):
            try:
                parsed_result = parse_scenario(user_input)
                normalized = parsed_result.get('normalized', parsed_result)
                
                # Store parsed data in session state
                heirs = normalized.get('heirs', {})
                st.session_state['parsed_sons'] = heirs.get('sons', 2)
                st.session_state['parsed_daughters'] = heirs.get('daughters', 3)
                st.session_state['parsed_wives'] = heirs.get('wife', 1)
                st.session_state['parsed_husband'] = heirs.get('husband', 0)
                st.session_state['parsed_mother'] = heirs.get('mother', 0)
                st.session_state['parsed_father'] = heirs.get('father', 0)
                st.session_state['parsed_total_estate'] = normalized.get('total_estate', 10_000_000)
                st.session_state['parsed_debts'] = normalized.get('debts', 0)
                st.session_state['parsed_sect'] = normalized.get('sect', 'hanafi')
                
                # Store dispute flags
                dispute_flags = normalized.get('dispute_flags', {})
                st.session_state['parsed_mutation'] = dispute_flags.get('mutation_done_by_one_heir', False)
                st.session_state['parsed_no_cert'] = not dispute_flags.get('has_succession_certificate', True)
                st.session_state['parsed_minor'] = dispute_flags.get('minor_heir_present', False)
                st.session_state['parsed_forced_sale'] = dispute_flags.get('selling_without_consent', False)
                st.session_state['parsed_hiba'] = dispute_flags.get('gift_hiba_present', False)
                st.session_state['parsed_donor_possession'] = not dispute_flags.get('possession_transferred', True)
                st.session_state['parsed_will_exceeds'] = dispute_flags.get('will_exceeds_limit', False)
                st.session_state['parsed_debts_not_paid'] = dispute_flags.get('debts_present', False) and not dispute_flags.get('debts_paid', True)
                
                st.success(f"✅ Scenario parsed successfully! Method: {parsed_result.get('method', 'unknown')}")
                
                # Display parsed summary
                with st.expander("📋 Parsed Data Summary"):
                    st.json({
                        "Sect": st.session_state['parsed_sect'],
                        "Sons": st.session_state['parsed_sons'],
                        "Daughters": st.session_state['parsed_daughters'],
                        "Wives": st.session_state['parsed_wives'],
                        "Husband": st.session_state['parsed_husband'],
                        "Mother": st.session_state['parsed_mother'],
                        "Father": st.session_state['parsed_father'],
                        "Total Estate": f"Rs {st.session_state['parsed_total_estate']:,.0f}",
                        "Debts": f"Rs {st.session_state['parsed_debts']:,.0f}",
                        "Dispute - Mutation": st.session_state['parsed_mutation'],
                        "Dispute - No Certificate": st.session_state['parsed_no_cert'],
                        "Dispute - Minor": st.session_state['parsed_minor'],
                        "Dispute - Forced Sale": st.session_state['parsed_forced_sale']
                    })
                    
            except Exception as e:
                st.error(f"Error parsing: {e}")
    
    # Form with PRE-POPULATED values from parsed data
    with st.sidebar.form("nlp_form"):
        st.subheader("🕌 Deceased & Sect")
        
        # Sect selector with parsed value
        default_sect = st.session_state.get('parsed_sect', 'hanafi')
        sect_index = ["hanafi", "shia", "christian", "hindu"].index(default_sect) if default_sect in ["hanafi", "shia", "christian", "hindu"] else 0
        sect = st.selectbox("Sect / Religion", ["hanafi", "shia", "christian", "hindu"], index=sect_index)
        
        st.subheader("💰 Estate & Liabilities")
        total_estate = st.number_input(
            "Total Estate (PKR)", 
            min_value=0, 
            value=st.session_state.get('parsed_total_estate', 10_000_000), 
            step=500_000
        )
        debts = st.number_input(
            "Outstanding Debts (PKR)", 
            min_value=0, 
            value=st.session_state.get('parsed_debts', 0)
        )
        funeral = st.number_input("Funeral Expenses (PKR)", min_value=0, value=0)
        wasiyyat = st.number_input("Wasiyyat (Will amount, PKR)", min_value=0, value=0)
        
        st.subheader("👨‍👩‍👧‍👦 Heirs (counts)")
        col1, col2 = st.columns(2)
        with col1:
            sons = st.number_input(
                "Sons", 
                min_value=0, 
                value=st.session_state.get('parsed_sons', 2),
                help="Son's share is double that of a daughter"
            )
            daughters = st.number_input(
                "Daughters", 
                min_value=0, 
                value=st.session_state.get('parsed_daughters', 3),
                help="Daughter gets half of son's share if both exist"
            )
            wives = st.number_input(
                "Wives", 
                min_value=0, 
                value=st.session_state.get('parsed_wives', 1),
                help="Multiple wives split the wife's share equally"
            )
        with col2:
            husband = st.number_input(
                "Husband (0/1)", 
                min_value=0, 
                max_value=1, 
                value=st.session_state.get('parsed_husband', 0)
            )
            mother = st.number_input(
                "Mother (0/1)", 
                min_value=0, 
                max_value=1, 
                value=st.session_state.get('parsed_mother', 0),
                help="Mother's share can be 1/6 or 1/3 depending on siblings"
            )
            father = st.number_input(
                "Father (0/1)", 
                min_value=0, 
                max_value=1, 
                value=st.session_state.get('parsed_father', 0),
                help="Father gets 1/6 plus residue"
            )
        
        # For Christian
        if sect == "christian":
            spouse_christian = st.number_input("Spouse (0/1)", min_value=0, max_value=1, value=0)
            children_christian = st.number_input("Children count", min_value=0, value=0)
        else:
            spouse_christian = 0
            children_christian = 0
        
        st.subheader("⚠️ Dispute Flags (optional)")
        mutation_single = st.checkbox(
            "Mutation done by single heir?", 
            value=st.session_state.get('parsed_mutation', False)
        )
        no_succession = st.checkbox(
            "No succession certificate?", 
            value=st.session_state.get('parsed_no_cert', False)
        )
        minor = st.checkbox(
            "Minor heir involved?", 
            value=st.session_state.get('parsed_minor', False)
        )
        forced_sale = st.checkbox(
            "One heir wants to sell, others refuse?", 
            value=st.session_state.get('parsed_forced_sale', False)
        )
        hiba = st.checkbox(
            "Gift deed (Hiba) mentioned?", 
            value=st.session_state.get('parsed_hiba', False)
        )
        donor_possession = st.checkbox(
            "Donor still in possession?", 
            value=st.session_state.get('parsed_donor_possession', False)
        )
        will_exceeds = st.checkbox(
            "Will exceeds 1/3 of estate?", 
            value=st.session_state.get('parsed_will_exceeds', False)
        )
        debts_not_paid = st.checkbox(
            "Estate distributed before paying debts?", 
            value=st.session_state.get('parsed_debts_not_paid', False)
        )
        
        submitted = st.form_submit_button("🔍 Calculate Shares & Taxes")

# ============================================================
# FORM INPUT MODE (STANDARD)
# ============================================================
else:
    with st.sidebar.form("inheritance_form"):
        st.subheader("🕌 Deceased & Sect")
        sect = st.selectbox("Sect / Religion", ["hanafi", "shia", "christian", "hindu"])
        
        st.subheader("💰 Estate & Liabilities")
        total_estate = st.number_input("Total Estate (PKR)", min_value=0, value=10_000_000, step=500_000)
        debts = st.number_input("Outstanding Debts (PKR)", min_value=0, value=0)
        funeral = st.number_input("Funeral Expenses (PKR)", min_value=0, value=0)
        wasiyyat = st.number_input("Wasiyyat (Will amount, PKR)", min_value=0, value=0)
        
        st.subheader("👨‍👩‍👧‍👦 Heirs (counts)")
        col1, col2 = st.columns(2)
        with col1:
            sons = st.number_input("Sons", min_value=0, value=2, help="Son's share is double that of a daughter")
            daughters = st.number_input("Daughters", min_value=0, value=3, help="Daughter gets half of son's share if both exist")
            wives = st.number_input("Wives", min_value=0, value=1, help="Multiple wives split the wife's share equally")
        with col2:
            husband = st.number_input("Husband (0/1)", min_value=0, max_value=1, value=0)
            mother = st.number_input("Mother (0/1)", min_value=0, max_value=1, value=0, help="Mother's share can be 1/6 or 1/3 depending on siblings")
            father = st.number_input("Father (0/1)", min_value=0, max_value=1, value=0, help="Father gets 1/6 plus residue")
        
        if sect == "christian":
            spouse_christian = st.number_input("Spouse (0/1)", min_value=0, max_value=1, value=0)
            children_christian = st.number_input("Children count", min_value=0, value=0)
        else:
            spouse_christian = 0
            children_christian = 0
        
        st.subheader("⚠️ Dispute Flags (optional)")
        mutation_single = st.checkbox("Mutation done by single heir?")
        no_succession = st.checkbox("No succession certificate?")
        minor = st.checkbox("Minor heir involved?")
        forced_sale = st.checkbox("One heir wants to sell, others refuse?")
        hiba = st.checkbox("Gift deed (Hiba) mentioned?")
        donor_possession = st.checkbox("Donor still in possession?")
        will_exceeds = st.checkbox("Will exceeds 1/3 of estate?")
        debts_not_paid = st.checkbox("Estate distributed before paying debts?")
        
        submitted = st.form_submit_button("🔍 Calculate Shares & Taxes")

# ============================================================
# MAIN CALCULATION LOGIC (SAME FOR BOTH MODES)
# ============================================================
if submitted:
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

    # Calculate shares
    calculation_result = calculate_shares(sect, heirs, total_estate, debts=debts, funeral=funeral, wasiyyat=wasiyyat)
    
    if "error" in calculation_result:
        st.error(calculation_result["error"])
        st.stop()
    
    # Extract shares
    if "shares" in calculation_result:
        shares = calculation_result["shares"]
    else:
        shares = calculation_result
    
    distributable_estate = calculation_result.get("distributable_estate", total_estate - debts - funeral)
    
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
    
    disputes = detect_inheritance_disputes(dispute_data)
    
    # Tax per heir
    full_property_value = total_estate
    filer_status_map = {}
    for heir in shares.keys():
        filer_status_map[heir] = FilerStatus.FILER if 'son' in heir else FilerStatus.NON_FILER
    
    tax_results = calculate_all_heirs_tax(
        heirs_shares=shares,
        filer_status_map=filer_status_map,
        full_property_value_pkr=full_property_value,
        action="sell",
        province=Province.DEFAULT
    )
    
    # ============================================================
    # SECTION 1: KEY METRICS (Top Row)
    # ============================================================
    st.subheader("📊 Estate Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Estate", f"Rs {total_estate:,.0f}")
    with col2:
        st.metric("📉 Total Deductions", f"Rs {debts + funeral + wasiyyat:,.0f}")
    with col3:
        st.metric("🏦 Distributable", f"Rs {distributable_estate:,.0f}")
    with col4:
        st.metric("👨‍👩‍👧‍👦 Total Heirs", len(shares))
    
    st.divider()
    
    # ============================================================
    # SECTION 2: SHARE DISTRIBUTION (Tables + Charts)
    # ============================================================
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.subheader("📋 Share Distribution Table")
        
        # Prepare data for table
        table_data = []
        for heir, data in shares.items():
            tax_info = tax_results.get(heir, {})
            net_after_tax = tax_info.get('net_after_all_taxes', data['amount'])
            percentage = (data['amount'] / distributable_estate * 100) if distributable_estate > 0 else 0
            
            table_data.append({
                "Heir": heir.replace('_', ' ').title(),
                "Fraction": data.get('fraction', 'N/A'),
                "Amount (PKR)": f"Rs {data['amount']:,.0f}",
                "Percentage": f"{percentage:.1f}%",
                "Net After Tax": f"Rs {net_after_tax:,.0f}"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with col_right:
        st.subheader("🥧 Distribution Chart")
        
        # Create pie chart with amounts and percentages
        pie_data = []
        for heir, data in shares.items():
            percentage = (data['amount'] / distributable_estate * 100) if distributable_estate > 0 else 0
            pie_data.append({
                "Heir": heir.replace('_', ' ').title(),
                "Amount": data['amount'],
                "Percentage": f"{percentage:.1f}%"
            })
        
        pie_df = pd.DataFrame(pie_data)
        
        fig_pie = px.pie(
            pie_df, 
            values="Amount", 
            names="Heir",
            title="Inheritance Share Distribution",
            hover_data=["Percentage"],
            labels={"Amount": "Amount (PKR)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hole=0.3,
            hovertemplate="<b>%{label}</b><br>Amount: Rs %{value:,.0f}<br>Percentage: %{percent}<extra></extra>"
        )
        fig_pie.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # ============================================================
    # SECTION 3: TAX ANALYSIS
    # ============================================================
    st.subheader("💰 Tax Analysis (If Selling Shares)")
    
    col_tax1, col_tax2 = st.columns(2)
    
    with col_tax1:
        # Tax table
        tax_table_data = []
        for heir, tax in tax_results.items():
            tax_table_data.append({
                "Heir": heir.replace('_', ' ').title(),
                "Share Value": f"Rs {tax.get('share_value_pkr', 0):,.0f}",
                "236C Tax": f"Rs {tax.get('advance_tax_236C', 0):,.0f}",
                "CGT": f"Rs {tax.get('cgt', 0):,.0f}",
                "Net After Tax": f"Rs {tax.get('net_after_all_taxes', 0):,.0f}"
            })
        
        tax_df = pd.DataFrame(tax_table_data)
        st.dataframe(tax_df, use_container_width=True, hide_index=True)
        st.caption("📌 Tax calculated as per FBR Finance Act 2025, Section 236C (seller). Pakistan has no inheritance tax.")
    
    with col_tax2:
        # Tax comparison bar chart (filer vs non-filer savings)
        tax_comparison_data = []
        for heir, tax in tax_results.items():
            savings = tax.get('savings_if_filer', 0)
            if savings > 0:
                tax_comparison_data.append({
                    "Heir": heir.replace('_', ' ').title(),
                    "Potential Savings": savings
                })
        
        if tax_comparison_data:
            savings_df = pd.DataFrame(tax_comparison_data)
            fig_savings = px.bar(
                savings_df,
                x="Heir",
                y="Potential Savings",
                title="💰 Potential Tax Savings if Filer",
                labels={"Potential Savings": "Savings (PKR)"},
                color="Potential Savings",
                color_continuous_scale="Greens"
            )
            fig_savings.update_layout(showlegend=False)
            st.plotly_chart(fig_savings, use_container_width=True)
        else:
            st.info("All heirs are already filers. No additional savings available.")
    
    st.divider()
    
    # ============================================================
    # SECTION 4: DISPUTE ANALYSIS
    # ============================================================
    col_disp1, col_disp2 = st.columns([1, 1])
    
    with col_disp1:
        st.subheader("⚠️ Dispute & Fraud Detection")
        if disputes.get('total_patterns_detected', 0) > 0:
            fraud_score = disputes.get('highest_risk', {}).get('fraud_score', 0)
            if fraud_score >= 70:
                st.error(f"🚨 FRAUD SCORE: {fraud_score}/100 - HIGH RISK")
            elif fraud_score >= 40:
                st.warning(f"⚠️ FRAUD SCORE: {fraud_score}/100 - MEDIUM RISK")
            else:
                st.info(f"ℹ️ FRAUD SCORE: {fraud_score}/100 - LOW RISK")
            
            for d in disputes.get('disputes', []):
                with st.expander(f"🔴 {d.get('pattern', '').replace('_', ' ').title()}"):
                    st.write(f"**Law:** {d.get('law_sections', {})}")
                    actions = d.get('recommended_actions', [])
                    if actions:
                        st.write(f"**Recommended Actions:**")
                        for action in actions[:3]:
                            st.write(f"  • {action}")
        else:
            st.success("✅ No significant dispute patterns detected.")
            st.info("The distribution appears to be peaceful. Proceed with standard NADRA process.")
    
    with col_disp2:
        st.subheader("📜 Legal Process Navigator")
        process_result = get_succession_process(
            has_minor_heir=minor,
            has_dispute=disputes.get('total_patterns_detected', 0) > 0,
            dispute_result=disputes,
            is_selling=False
        )
        
        for idx, step in enumerate(process_result.get('process_steps', []), 1):
            with st.expander(f"📌 Step {idx}: {step.get('name', 'Step')}"):
                st.write(f"**Authority:** {step.get('authority', 'N/A')}")
                st.write(f"**Fee:** {step.get('fee', 'N/A')}")
                st.write(f"**Documents Required:**")
                for doc in step.get('documents', []):
                    st.write(f"  • {doc}")
                st.write(f"**Estimated Time:** {step.get('time', 'N/A')}")
                if step.get('alert'):
                    st.warning(step['alert'])
    
    st.divider()
    
    # ============================================================
    # SECTION 5: HEIR-BY-HEIR BREAKDOWN
    # ============================================================
    st.subheader("👨‍👩‍👧‍👦 Detailed Heir Breakdown")
    
    # Create expandable cards for each heir
    heir_cols = st.columns(min(len(shares), 4))
    for idx, (heir, data) in enumerate(shares.items()):
        col_idx = idx % 4
        with heir_cols[col_idx]:
            percentage = (data['amount'] / distributable_estate * 100) if distributable_estate > 0 else 0
            tax_info = tax_results.get(heir, {})
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>{heir.replace('_', ' ').title()}</h4>
                <p class="big-number">{data.get('fraction', 'N/A')}</p>
                <p><b>Rs {data['amount']:,.0f}</b></p>
                <p style="color: #666;">{percentage:.1f}% of estate</p>
                <hr>
                <p style="font-size: 0.9rem;">📉 After Tax: <b>Rs {tax_info.get('net_after_all_taxes', data['amount']):,.0f}</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
    
    st.divider()
    
    # ============================================================
    # SECTION 6: DOCUMENT GENERATION
    # ============================================================
    st.subheader("📄 Legal Documents")
    
    col_doc1, col_doc2, col_doc3 = st.columns(3)
    
    with col_doc1:
        if st.button("📑 Generate Share Certificate (PDF)", use_container_width=True):
            try:
                pdf_bytes = generate_inheritance_certificate_pdf(
                    deceased_name="Late Person",
                    death_date=datetime.now().strftime("%Y-%m-%d"),
                    sect=sect,
                    total_estate=total_estate,
                    debts=debts,
                    funeral=funeral,
                    wasiyyat=wasiyyat,
                    shares=shares
                )
                st.download_button(
                    "⬇️ Download PDF", 
                    data=pdf_bytes, 
                    file_name="inheritance_certificate.pdf", 
                    mime="application/pdf",
                    use_container_width=True,
                    key="pdf_download"
                )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")
    
    with col_doc2:
        if disputes.get('total_patterns_detected', 0) > 0:
            top_dispute = disputes.get('disputes', [{}])[0]
            if st.button("📋 Generate Legal Notice", use_container_width=True):
                notice_text = generate_legal_notice(
                    sender_name="User",
                    sender_address="Your Address",
                    sender_cnic="XXXXX-XXXXXXX-X",
                    recipient_name="Opposing Heir",
                    recipient_address="Their Address",
                    deceased_name="Late Person",
                    death_date=datetime.now().strftime("%Y-%m-%d"),
                    sect=sect,
                    sender_share_fraction="1/8",
                    sender_share_amount=100000,
                    fraud_description=top_dispute.get('pattern', 'fraud'),
                    law_sections_list=str(top_dispute.get('law_sections', {})),
                    remedy=top_dispute.get('remedy', 'Legal action'),
                    language='en'
                )
                st.text_area("Legal Notice Preview", notice_text, height=150)
                st.download_button("⬇️ Download Notice", data=notice_text, file_name="legal_notice.txt", key="notice_download")
    
    with col_doc3:
        if disputes.get('total_patterns_detected', 0) > 0:
            top_dispute = disputes.get('disputes', [{}])[0]
            if top_dispute.get('pattern') == 'fraudulent_mutation':
                if st.button("🚨 Generate FIR Draft", use_container_width=True):
                    fir = generate_fir_draft(
                        complainant_name="User",
                        complainant_cnic="XXXXX-XXXXXXX-X",
                        complainant_address="Your Address",
                        complainant_father_name="Father Name",
                        deceased_name="Late Person",
                        death_date=datetime.now().strftime("%Y-%m-%d"),
                        heirs_list="List of heirs",
                        accused_name="Opposing Heir",
                        accused_address="Their Address",
                        crime_description="Fraudulent mutation of property",
                        evidence_list="Succession certificate missing",
                        police_station_name="Local Police Station",
                        police_station_address="Station Address",
                        ppc_sections="498A"
                    )
                    st.text_area("FIR Draft (Urdu)", fir, height=150)
    
    st.divider()
    
    # ============================================================
    # SECTION 7: URDU EXPLANATION
    # ============================================================
    with st.expander("📖 Urdu Explanation (AI Generated)"):
        # Build a simple Urdu explanation
        urdu_text = f"""
        <div class="urdu-text">
        <p><b>مرحوم کی جائیداد کی تقسیم</b></p>
        <p>کل جائیداد: {total_estate:,.0f} روپے</p>
        <p>تقسیم کے بعد ہر وارث کو درج ذیل حصے ملیں گے:</p>
        """
        for heir, data in shares.items():
            urdu_text += f"<p>• {heir.replace('_', ' ').title()}: {data.get('fraction', 'N/A')} = {data['amount']:,.0f} روپے</p>"
        
        urdu_text += """
        <p><b>اہم نوٹ:</b> پاکستان میں انہریٹنس ٹیکس نہیں ہے۔ ٹیکس صرف اس وقت لگتا ہے جب وارث اپنا حصہ بیچتا ہے۔</p>
        <p>مزید معلومات کے لیے قانونی مشورہ ضرور لیں۔</p>
        </div>
        """
        st.markdown(urdu_text, unsafe_allow_html=True)
    
    # ============================================================
    # SECTION 8: DOWNLOAD FULL REPORT
    # ============================================================
    st.subheader("📥 Export Options")
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        # Export shares as CSV
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📊 Download Shares as CSV",
            data=csv_data,
            file_name="warisnama_shares.csv",
            mime="text/csv",
            use_container_width=True,
            key="csv_download"
        )
    
    with col_export2:
        # Export tax data as CSV
        tax_csv = pd.DataFrame(tax_table_data).to_csv(index=False)
        st.download_button(
            "💰 Download Tax Report as CSV",
            data=tax_csv,
            file_name="warisnama_tax_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="tax_csv_download"
        )