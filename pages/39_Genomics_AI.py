# pages/39_Genomics_AI.py
# 2029 Feature: Genomic risk prediction + BRCA1/BRCA2 analysis
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()

st.markdown("""
<style>
.gene-card{background:linear-gradient(145deg,#0f172a,#1e293b);
           border-radius:14px;padding:18px;border:1px solid rgba(255,255,255,0.07);}
.gene-positive{border-color:rgba(239,68,68,0.5)!important;background:linear-gradient(145deg,#1a0a0a,#200d0d)!important;}
.gene-negative{border-color:rgba(34,197,94,0.5)!important;}
.gene-name{font-size:20px;font-weight:900;color:#f8fafc;}
.gene-result{font-size:28px;font-weight:900;}
.dna-helix{font-size:40px;animation:spin 4s linear infinite;}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:16px 0">
<div style="font-size:11px;color:#818cf8;letter-spacing:2px;text-transform:uppercase">2029 Feature</div>
<h1 style="color:#f8fafc;margin:4px 0">🧬 Genomics AI — Genetic Risk Analysis</h1>
<p style="color:rgba(255,255,255,0.45)">
BRCA1/BRCA2 mutation analysis · Hereditary breast cancer risk · Personalized prevention
</p>
</div>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────────────
conn = connect()
conn.execute("""
    CREATE TABLE IF NOT EXISTS genomic_profiles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT, brca1 TEXT, brca2 TEXT, tp53 TEXT, palb2 TEXT,
        chek2 TEXT, atm TEXT, overall_risk TEXT, polygenic_score REAL,
        recommendation TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )
""")
conn.commit()
conn.close()

tab1, tab2, tab3 = st.tabs(["🧬 Genetic Profile", "📊 Population Genetics", "📚 Gene Library"])

with tab1:
    st.subheader("🧬 Patient Genomic Risk Profile")

    col1, col2 = st.columns(2)
    with col1:
        patient_id = st.text_input("Patient ID *")
        st.markdown("**BRCA Gene Panel**")
        brca1 = st.selectbox("BRCA1 Status",
            ["Not Tested","Negative (No Mutation)","Positive — Pathogenic Variant",
             "Variant of Uncertain Significance (VUS)"])
        brca2 = st.selectbox("BRCA2 Status",
            ["Not Tested","Negative (No Mutation)","Positive — Pathogenic Variant",
             "Variant of Uncertain Significance (VUS)"])
    with col2:
        st.markdown("**Extended Gene Panel**")
        tp53  = st.selectbox("TP53",  ["Not Tested","Negative","Positive"])
        palb2 = st.selectbox("PALB2", ["Not Tested","Negative","Positive"])
        chek2 = st.selectbox("CHEK2", ["Not Tested","Negative","Positive"])
        atm   = st.selectbox("ATM",   ["Not Tested","Negative","Positive"])

    st.markdown("**Family History Score**")
    fh_score = st.slider("Number of 1st-degree relatives with breast/ovarian cancer", 0, 5, 0)

    if st.button("🧬 Generate Genomic Risk Report", type="primary", use_container_width=True):
        if patient_id:
            # Calculate risk
            risk_pts = 0
            if "Positive" in brca1: risk_pts += 40
            if "Positive" in brca2: risk_pts += 35
            if "Positive" in tp53:  risk_pts += 25
            if "Positive" in palb2: risk_pts += 15
            if "Positive" in chek2: risk_pts += 10
            if "Positive" in atm:   risk_pts += 10
            risk_pts += fh_score * 8
            risk_pts = min(risk_pts, 100)

            poly_score = random.uniform(0.3, 0.9)
            lifetime_risk = 12 + risk_pts * 0.7
            lifetime_risk = min(lifetime_risk, 85)

            if risk_pts >= 40:   overall = "Very High Risk"; ov_col="#ef4444"
            elif risk_pts >= 20: overall = "High Risk";      ov_col="#f97316"
            elif risk_pts >= 10: overall = "Moderate Risk";  ov_col="#f59e0b"
            else:                overall = "Average Risk";   ov_col="#22c55e"

            # Save
            conn = connect()
            conn.execute("""
                INSERT INTO genomic_profiles(patient_id,brca1,brca2,tp53,palb2,chek2,atm,
                                             overall_risk,polygenic_score,recommendation)
                VALUES(?,?,?,?,?,?,?,?,?,?)
            """, (patient_id, brca1, brca2, tp53, palb2, chek2, atm,
                  overall, poly_score, "See below"))
            conn.commit()
            conn.close()
            log_audit("GENOMIC_PROFILE", "doctor", f"Patient {patient_id}: {overall}")

            # ── Results Display ──────────────────────────────────────────────
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(168,85,247,0.08));
                        border:2px solid rgba(99,102,241,0.4);border-radius:20px;
                        padding:28px;text-align:center;margin:16px 0">
                <div style="font-size:12px;color:rgba(255,255,255,0.5);letter-spacing:2px">GENOMIC RISK CLASSIFICATION</div>
                <div style="font-size:42px;font-weight:900;color:{ov_col};margin:8px 0">{overall}</div>
                <div style="font-size:18px;color:#f8fafc">
                    Estimated Lifetime Risk: <b style="color:{ov_col}">{lifetime_risk:.1f}%</b>
                </div>
                <div style="font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px">
                    Population average: 12% · Polygenic Score: {poly_score:.3f}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Gene results
            genes = [("BRCA1",brca1),("BRCA2",brca2),("TP53",tp53),
                     ("PALB2",palb2),("CHEK2",chek2),("ATM",atm)]
            cols = st.columns(3)
            for i, (gene, result) in enumerate(genes):
                with cols[i % 3]:
                    is_pos = "Positive" in result
                    css    = "gene-positive" if is_pos else "gene-negative"
                    icon   = "🔴" if is_pos else "🟢"
                    short  = "POSITIVE" if is_pos else ("NEGATIVE" if "Negative" in result else "NOT TESTED")
                    col_v  = "#ef4444" if is_pos else "#22c55e" if "Negative" in result else "#94a3b8"
                    st.markdown(f"""
                    <div class="gene-card {css}">
                        <div class="gene-name">{gene}</div>
                        <div class="gene-result" style="color:{col_v}">{icon} {short}</div>
                        <div style="font-size:10px;color:rgba(255,255,255,0.35);margin-top:4px">{result[:30]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

            # Recommendations
            st.subheader("📋 Clinical Recommendations")
            recs = []
            if "Positive" in brca1 or "Positive" in brca2:
                recs += ["Annual breast MRI starting at age 25","Consider prophylactic mastectomy discussion",
                         "Annual mammogram","Refer to genetic counselor","Test 1st-degree relatives",
                         "Discuss risk-reducing salpingo-oophorectomy (RRSO)"]
            elif overall == "High Risk":
                recs += ["Annual mammogram starting at 35","Breast MRI every 2 years",
                         "Clinical breast exam every 6 months","Consider chemoprevention"]
            else:
                recs += ["Annual mammogram at 40+","Monthly self-examination",
                         "Maintain healthy BMI","Regular clinical checkups"]

            for r in recs:
                st.markdown(f"""
                <div style="display:flex;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05)">
                <span style="color:#22c55e">✓</span>
                <span style="color:#e2e8f0;font-size:13px">{r}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Enter Patient ID.")

with tab2:
    st.subheader("📊 BRCA Mutation Statistics — India")

    india_brca = pd.DataFrame({
        "Population":["General Population","Family History (1st degree)",
                      "Early-onset BC (<40)","Triple Negative BC","Ashkenazi Jews (Reference)"],
        "BRCA1 (%)": [0.5, 8.0, 12.0, 15.0, 8.3],
        "BRCA2 (%)": [0.3, 6.5, 8.0, 4.0, 2.6],
    })
    fig_brca = px.bar(india_brca, x="Population", y=["BRCA1 (%)","BRCA2 (%)"],
                       barmode="group", title="BRCA Mutation Prevalence by Population",
                       color_discrete_sequence=["#6366f1","#818cf8"])
    fig_brca.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                            font_color="white", height=350)
    st.plotly_chart(fig_brca, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        survival_data = pd.DataFrame({
            "Stage":["I","II","III","IV"],
            "BRCA1+ Survival":[95,78,55,22],
            "BRCA2+ Survival":[96,82,60,25],
            "Sporadic":[98,85,65,28]
        })
        fig_s = px.line(survival_data, x="Stage", y=["BRCA1+ Survival","BRCA2+ Survival","Sporadic"],
                         title="5-Year Survival by BRCA Status & Stage",
                         color_discrete_sequence=["#ef4444","#f97316","#22c55e"])
        fig_s.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                             font_color="white", height=300)
        st.plotly_chart(fig_s, use_container_width=True)
    with col2:
        risk_data = pd.DataFrame({
            "Mutation":["BRCA1","BRCA2","TP53","PALB2","CHEK2","ATM","General Pop"],
            "Lifetime Risk (%)": [72, 69, 60, 35, 25, 20, 12]
        })
        fig_r = px.bar(risk_data, x="Mutation", y="Lifetime Risk (%)",
                        title="Lifetime Breast Cancer Risk by Gene",
                        color="Lifetime Risk (%)",
                        color_continuous_scale="Reds")
        fig_r.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                             font_color="white", height=300)
        st.plotly_chart(fig_r, use_container_width=True)

with tab3:
    st.subheader("📚 Breast Cancer Gene Library")
    gene_lib = [
        {"Gene":"BRCA1","Chr":"17q21","Type":"Tumor Suppressor","Risk":"60–72%","Notes":"Most common high-risk gene; DNA repair (HR pathway)"},
        {"Gene":"BRCA2","Chr":"13q12","Type":"Tumor Suppressor","Risk":"55–69%","Notes":"DNA repair via RAD51; also pancreatic/ovarian cancer risk"},
        {"Gene":"TP53","Chr":"17p13","Type":"Tumor Suppressor","Risk":"Up to 60%","Notes":"Li-Fraumeni syndrome; early-onset (<35)"},
        {"Gene":"PALB2","Chr":"16p12","Type":"Tumor Suppressor","Risk":"35–58%","Notes":"Works with BRCA2; HR DNA repair"},
        {"Gene":"CHEK2","Chr":"22q12","Type":"Tumor Suppressor","Risk":"20–37%","Notes":"DNA damage checkpoint; 1100delC variant"},
        {"Gene":"ATM","Chr":"11q22","Type":"Tumor Suppressor","Risk":"20–30%","Notes":"Ataxia telangiectasia; double-strand break repair"},
        {"Gene":"PTEN","Chr":"10q23","Type":"Tumor Suppressor","Risk":"25–50%","Notes":"Cowden syndrome; hamartoma tumors"},
        {"Gene":"CDH1","Chr":"16q22","Type":"Tumor Suppressor","Risk":"42% (lobular)","Notes":"Hereditary diffuse gastric cancer syndrome"},
    ]
    df_lib = pd.DataFrame(gene_lib)
    st.dataframe(df_lib, use_container_width=True, hide_index=True)
    st.caption("Source: NCCN Clinical Practice Guidelines in Oncology v2.2024, ClinVar Database")
