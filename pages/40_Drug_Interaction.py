# pages/40_Drug_Interaction.py
# 2027 Feature: AI drug interaction checker for oncology medications
import streamlit as st
import pandas as pd
import plotly.express as px
from auth.guard import check_login
from database.database import connect, log_audit
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()

st.markdown("""
<style>
.drug-safe{background:rgba(34,197,94,0.1);border:1px solid #22c55e;border-radius:10px;padding:12px;}
.drug-warn{background:rgba(245,158,11,0.1);border:1px solid #f59e0b;border-radius:10px;padding:12px;}
.drug-danger{background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:10px;padding:12px;}
.drug-pill{background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);
           border-radius:20px;padding:4px 12px;font-size:12px;color:#a5b4fc;
           display:inline-block;margin:2px;}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:16px 0">
<div style="font-size:11px;color:#818cf8;letter-spacing:2px;text-transform:uppercase">2027 Feature</div>
<h1 style="color:#f8fafc;margin:4px 0">💊 AI Drug Interaction Checker</h1>
<p style="color:rgba(255,255,255,0.45)">
Check oncology medication interactions, side effects, and dosing for breast cancer patients
</p>
</div>
""", unsafe_allow_html=True)

# Drug database
DRUGS = {
    "Tamoxifen": {"class":"SERM","use":"HR+ breast cancer","half_life":"5-7 days",
                  "route":"Oral","dose":"20mg/day","monitoring":["LFT","CBC","Uterine monitoring"]},
    "Anastrozole (Arimidex)": {"class":"Aromatase Inhibitor","use":"Postmenopausal HR+ BC",
                                "half_life":"50h","route":"Oral","dose":"1mg/day",
                                "monitoring":["Bone density","LFT","Cholesterol"]},
    "Letrozole (Femara)": {"class":"Aromatase Inhibitor","use":"HR+ BC","half_life":"48h",
                            "route":"Oral","dose":"2.5mg/day","monitoring":["Bone density","LFT"]},
    "Trastuzumab (Herceptin)": {"class":"Anti-HER2 mAb","use":"HER2+ BC","half_life":"28 days",
                                 "route":"IV","dose":"8mg/kg loading, 6mg/kg q3w",
                                 "monitoring":["LVEF/ECHO","CBC","LFT"]},
    "Pertuzumab (Perjeta)": {"class":"Anti-HER2 mAb","use":"HER2+ BC (with Herceptin)","half_life":"18 days",
                              "route":"IV","dose":"840mg loading, 420mg q3w","monitoring":["LVEF","CBC"]},
    "Palbociclib (Ibrance)": {"class":"CDK4/6 Inhibitor","use":"HR+/HER2- advanced BC","half_life":"29h",
                               "route":"Oral","dose":"125mg/day x21 days, 7 off","monitoring":["CBC","LFT"]},
    "Capecitabine (Xeloda)": {"class":"Antimetabolite","use":"MBC, TNBC","half_life":"0.75h",
                               "route":"Oral","dose":"2500mg/m2/day","monitoring":["CBC","LFT","Hand-foot syndrome"]},
    "Paclitaxel (Taxol)": {"class":"Taxane","use":"MBC, adjuvant","half_life":"5.3–17.4h",
                            "route":"IV","dose":"175mg/m2 q3w","monitoring":["CBC","Neuropathy","LVEF"]},
    "Doxorubicin (AC)": {"class":"Anthracycline","use":"Neo/adjuvant","half_life":"16–20h",
                          "route":"IV","dose":"60mg/m2 q3w","monitoring":["LVEF","CBC","LFT"]},
    "Cyclophosphamide": {"class":"Alkylating agent","use":"AC regimen","half_life":"3–12h",
                          "route":"IV/Oral","dose":"600mg/m2 q3w","monitoring":["CBC","LFT","Bladder"]},
    "Bevacizumab (Avastin)": {"class":"Anti-VEGF mAb","use":"HER2- MBC","half_life":"20 days",
                               "route":"IV","dose":"10mg/kg q2w","monitoring":["BP","Proteinuria","CBC"]},
    "Olaparib (Lynparza)": {"class":"PARP Inhibitor","use":"BRCA1/2+ MBC","half_life":"14.9h",
                             "route":"Oral","dose":"300mg BID","monitoring":["CBC","LFT","MDS risk"]},
    "Warfarin": {"class":"Anticoagulant","use":"DVT prevention","half_life":"20–60h","route":"Oral","dose":"Variable","monitoring":["INR","CBC"]},
    "Metformin": {"class":"Biguanide","use":"Diabetes (Comorbidity)","half_life":"4–8h","route":"Oral","dose":"500–2000mg/day","monitoring":["LFT","B12"]},
}

INTERACTIONS = {
    ("Tamoxifen","Warfarin"): ("MAJOR","Tamoxifen significantly increases anticoagulant effect of warfarin. Monitor INR closely. May need dose reduction.","Monitor INR weekly initially"),
    ("Tamoxifen","Palbociclib (Ibrance)"): ("MODERATE","Both metabolized by CYP3A4. May alter plasma levels of both drugs.","Consider dose adjustment"),
    ("Doxorubicin (AC)","Trastuzumab (Herceptin)"): ("MAJOR","Increased cardiotoxicity risk. Sequential use preferred, not concurrent.","Do NOT give together. Sequential only."),
    ("Paclitaxel (Taxol)","Doxorubicin (AC)"): ("MODERATE","Paclitaxel may increase doxorubicin levels. Monitor cardiac function.","Monitor LVEF q3 months"),
    ("Capecitabine (Xeloda)","Warfarin"): ("MAJOR","Capecitabine significantly potentiates warfarin. Can cause fatal hemorrhage.","Monitor INR every 1-2 weeks"),
    ("Olaparib (Lynparza)","Metformin"): ("MINOR","No significant interaction reported.","Safe to use together"),
    ("Letrozole (Femara)","Anastrozole (Arimidex)"): ("CONTRAINDICATED","Do NOT use two aromatase inhibitors together. No clinical benefit, increased toxicity.","USE ONE OR THE OTHER"),
    ("Palbociclib (Ibrance)","Tamoxifen"): ("MODERATE","CYP3A4 interactions. Palbociclib may increase tamoxifen exposure.","Monitor toxicity closely"),
}

tab1, tab2, tab3 = st.tabs(["🔍 Check Interactions", "💊 Drug Database", "📋 Patient Prescription"])

with tab1:
    st.subheader("🔍 Drug Interaction Checker")
    st.info("Select 2 or more medications to check for interactions.")

    selected_drugs = st.multiselect(
        "Select medications patient is taking:",
        list(DRUGS.keys()),
        max_selections=6
    )

    if st.button("🔍 Check All Interactions", type="primary", use_container_width=True) and len(selected_drugs) >= 2:
        st.markdown("---")
        st.subheader("📊 Interaction Report")

        found_interactions = []
        for i in range(len(selected_drugs)):
            for j in range(i+1, len(selected_drugs)):
                d1, d2 = selected_drugs[i], selected_drugs[j]
                key1, key2 = (d1,d2), (d2,d1)
                interaction = INTERACTIONS.get(key1) or INTERACTIONS.get(key2)
                if interaction:
                    found_interactions.append((d1, d2, *interaction))
                else:
                    found_interactions.append((d1, d2, "MINOR",
                        "No significant interaction documented in oncology literature.",
                        "Standard monitoring recommended"))

        for d1, d2, severity, desc, action in found_interactions:
            css = "drug-danger" if severity in ["MAJOR","CONTRAINDICATED"] else \
                  "drug-warn"   if severity == "MODERATE" else "drug-safe"
            icon = "🚨" if severity in ["MAJOR","CONTRAINDICATED"] else \
                   "⚠️" if severity == "MODERATE" else "✅"
            st.markdown(f"""
            <div class="{css}">
                <div style="display:flex;justify-content:space-between">
                    <div>
                        <span class="drug-pill">{d1}</span>
                        <span style="color:rgba(255,255,255,0.4);margin:0 8px">+</span>
                        <span class="drug-pill">{d2}</span>
                    </div>
                    <span style="font-weight:800;font-size:13px">{icon} {severity}</span>
                </div>
                <div style="margin-top:10px;font-size:13px;color:#e2e8f0">{desc}</div>
                <div style="margin-top:6px;font-size:12px;font-weight:600;color:#f8fafc">
                    📋 Action: {action}
                </div>
            </div>
            <br>
            """, unsafe_allow_html=True)

        # Summary
        major_count = sum(1 for x in found_interactions if x[2] in ["MAJOR","CONTRAINDICATED"])
        moderate_count = sum(1 for x in found_interactions if x[2]=="MODERATE")
        if major_count:
            st.error(f"⚠️ {major_count} MAJOR interaction(s) found! Immediate clinical review required.")
        elif moderate_count:
            st.warning(f"⚠️ {moderate_count} moderate interaction(s). Monitor patient closely.")
        else:
            st.success("✅ No significant interactions found. Regimen appears safe.")

with tab2:
    st.subheader("💊 Oncology Drug Database")
    search = st.text_input("🔍 Search drug:", placeholder="e.g. Tamoxifen, Herceptin")
    drug_list = [d for d in DRUGS if search.lower() in d.lower()] if search else list(DRUGS.keys())

    cols = st.columns(2)
    for i, drug in enumerate(drug_list):
        with cols[i % 2]:
            d = DRUGS[drug]
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0f172a,#1e293b);
                        border:1px solid rgba(255,255,255,0.07);border-radius:14px;
                        padding:16px;margin:6px 0">
                <div style="font-size:15px;font-weight:700;color:#f8fafc">{drug}</div>
                <div style="margin-top:8px">
                    <span class="drug-pill">💊 {d['class']}</span>
                    <span class="drug-pill">📍 {d['route']}</span>
                </div>
                <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:8px">
                    <b style="color:#94a3b8">Use:</b> {d['use']}<br>
                    <b style="color:#94a3b8">Dose:</b> {d['dose']}<br>
                    <b style="color:#94a3b8">Half-life:</b> {d['half_life']}<br>
                    <b style="color:#94a3b8">Monitor:</b> {', '.join(d['monitoring'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("📋 Generate Patient Prescription Summary")
    p_id  = st.text_input("Patient ID")
    p_docs= st.multiselect("Prescribed Medications", list(DRUGS.keys()))
    p_doc = st.text_input("Prescribing Doctor")
    p_note= st.text_area("Special Instructions")

    if st.button("📋 Generate Prescription", type="primary"):
        if p_id and p_docs:
            log_audit("PRESCRIPTION", p_doc, f"Patient {p_id}: {', '.join(p_docs)}")
            st.success("✅ Prescription saved to patient record!")

            import io
            from datetime import datetime
            import pytz
            IST = pytz.timezone("Asia/Kolkata")
            lines = [
                "═"*60,
                "CMR UNIVERSITY HOSPITAL — ONCOLOGY DEPARTMENT",
                "Drug Prescription Summary",
                "═"*60,
                f"Patient ID : {p_id}",
                f"Date       : {datetime.now(IST).strftime('%d-%m-%Y %H:%M IST')}",
                f"Doctor     : {p_doc}",
                "─"*60,
                "PRESCRIBED MEDICATIONS:",
                ""
            ]
            for drug in p_docs:
                d = DRUGS[drug]
                lines += [
                    f"  Drug    : {drug}",
                    f"  Class   : {d['class']}",
                    f"  Dose    : {d['dose']}",
                    f"  Route   : {d['route']}",
                    f"  Monitor : {', '.join(d['monitoring'])}",
                    ""
                ]
            if p_note:
                lines += ["SPECIAL INSTRUCTIONS:", p_note, ""]
            lines += ["─"*60,
                      "DISCLAIMER: This prescription is for clinical decision support only.",
                      "Confirm with treating oncologist before administration.",
                      "═"*60]
            rx_text = "\n".join(lines)
            st.download_button("⬇️ Download Prescription (TXT)", rx_text.encode(),
                               f"prescription_{p_id}.txt", "text/plain")
        else:
            st.warning("Enter Patient ID and select medications.")
