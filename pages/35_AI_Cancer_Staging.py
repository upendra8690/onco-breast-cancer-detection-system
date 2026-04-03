# pages/35_AI_Cancer_Staging.py  ← NEW FILE
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()

st.markdown("""
<style>
.stage-card {
    border-radius:16px; padding:20px; text-align:center;
    border:2px solid; margin:4px; transition:transform 0.2s;
}
.stage-card:hover{transform:translateY(-2px);}
.stage-0  {background:rgba(34,197,94,0.1); border-color:#22c55e;}
.stage-1  {background:rgba(96,165,250,0.1); border-color:#60a5fa;}
.stage-2  {background:rgba(250,204,21,0.1); border-color:#facc15;}
.stage-3  {background:rgba(249,115,22,0.1); border-color:#f97316;}
.stage-4  {background:rgba(239,68,68,0.1);  border-color:#ef4444;}
.stage-label{font-size:28px;font-weight:900;}
.stage-name {font-size:14px;font-weight:700;margin-top:6px;}
.stage-survival{font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;}
.criterion-met   {color:#22c55e; font-size:13px;}
.criterion-unmet {color:#94a3b8; font-size:13px;}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.title("🔬 AI Cancer Staging — TNM Classification")
st.write("Clinical staging assessment based on AI findings and patient data.")

st.info("""
**TNM Classification System (AJCC 8th Edition)**
T = Tumor size · N = Lymph Node involvement · M = Metastasis
This tool assists in clinical staging — NOT a replacement for pathological diagnosis.
""")

patient_id = st.text_input("Patient ID")

conn = connect()
if patient_id:
    df_dx = pd.read_sql_query(
        "SELECT * FROM diagnosis WHERE patient_id=? ORDER BY created DESC LIMIT 1",
        conn, params=(patient_id,)
    )
else:
    df_dx = pd.DataFrame()
conn.close()

if not df_dx.empty:
    latest = df_dx.iloc[0]
    st.success(f"Latest AI result: **{latest['result']}** ({latest['confidence']:.1f}%) — {str(latest['created'])[:16]}")

st.markdown("---")
st.subheader("📋 Clinical Staging Criteria")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**T — Tumor (Primary)**")
    t_size    = st.number_input("Tumor Size (mm)", min_value=0.0, max_value=200.0, value=15.0, step=0.5)
    t_skin    = st.checkbox("Skin involvement")
    t_chest   = st.checkbox("Chest wall involvement")
    t_inflam  = st.checkbox("Inflammatory breast cancer")

with col2:
    st.markdown("**N — Lymph Nodes**")
    n_axillary = st.radio("Axillary Lymph Nodes",
                          ["N0 — None","N1 — 1-3 nodes","N2 — 4-9 nodes","N3 — ≥10 nodes"])
    n_internal  = st.checkbox("Internal mammary nodes involved")
    n_supraclav = st.checkbox("Supraclavicular nodes")

with col3:
    st.markdown("**M — Metastasis**")
    m_distant = st.radio("Distant Metastasis", ["M0 — None","M1 — Present"])
    m_sites   = st.multiselect("Sites (if M1):", ["Bone","Lung","Liver","Brain","Other"])

st.markdown("---")

# ── Biomarkers ─────────────────────────────────────────────────────────────────
st.subheader("🧬 Biomarker Profile")
c1,c2,c3,c4 = st.columns(4)
with c1: er_status  = st.selectbox("ER Status",  ["Positive","Negative","Unknown"])
with c2: pr_status  = st.selectbox("PR Status",  ["Positive","Negative","Unknown"])
with c3: her2_status= st.selectbox("HER2 Status",["Negative","Positive","Equivocal","Unknown"])
with c4: ki67       = st.number_input("Ki67 (%)", 0, 100, 20)

if st.button("🔬 Calculate Stage", type="primary", use_container_width=True):

    # Determine T stage
    if t_inflam: t_stage = "T4d"
    elif t_skin or t_chest: t_stage = "T4b" if (t_skin and t_chest) else "T4a"
    elif t_size <= 20: t_stage = "T1"
    elif t_size <= 50: t_stage = "T2"
    else: t_stage = "T3"

    # Determine N stage
    if "N3" in n_axillary or n_supraclav: n_stage = "N3"
    elif "N2" in n_axillary or n_internal: n_stage = "N2"
    elif "N1" in n_axillary: n_stage = "N1"
    else: n_stage = "N0"

    # Determine M stage
    m_stage = "M1" if "M1" in m_distant else "M0"

    # Overall stage
    if m_stage == "M1": overall = "IV";    stage_num = 4
    elif t_stage in ["T4a","T4b","T4d"]:   overall = "IIIB–IIIC"; stage_num = 3
    elif n_stage == "N3":                   overall = "IIIC"; stage_num = 3
    elif n_stage in ["N2"] or t_stage=="T3": overall = "IIIA"; stage_num = 3
    elif t_stage == "T2" and n_stage=="N1": overall = "IIB"; stage_num = 2
    elif t_stage == "T2" and n_stage=="N0": overall = "IIA"; stage_num = 2
    elif t_stage == "T1" and n_stage=="N1": overall = "IIA"; stage_num = 2
    else:                                   overall = "I"; stage_num = 1

    # Subtype
    if er_status=="Positive" and her2_status=="Negative":
        subtype = "Luminal A (HR+/HER2-)"
        subtype_prognosis = "Best prognosis. Hormone therapy recommended."
    elif er_status=="Positive" and her2_status=="Positive":
        subtype = "Luminal B (HR+/HER2+)"
        subtype_prognosis = "Moderate prognosis. Hormone + targeted therapy."
    elif er_status=="Negative" and her2_status=="Positive":
        subtype = "HER2-Enriched (HR-/HER2+)"
        subtype_prognosis = "Targeted therapy (Trastuzumab) recommended."
    elif er_status=="Negative" and pr_status=="Negative" and her2_status=="Negative":
        subtype = "Triple Negative (TNBC)"
        subtype_prognosis = "Most aggressive. Chemotherapy is main treatment."
    else:
        subtype = "Unknown Subtype"
        subtype_prognosis = "Further testing required."

    survival_map = {1: "95%", 2: "75–85%", 3: "55–70%", 4: "22–26%"}
    survival = survival_map.get(stage_num, "Unknown")
    stage_colors = {1:"#22c55e", 2:"#60a5fa", 3:"#f97316", 4:"#ef4444"}
    sc = stage_colors.get(stage_num, "#94a3b8")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba({','.join(str(int(sc.lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.15),rgba(0,0,0,0));
                border:2px solid {sc};border-radius:20px;padding:28px;text-align:center;margin:16px 0">
        <div style="font-size:13px;color:rgba(255,255,255,0.5);letter-spacing:2px;text-transform:uppercase">
            TNM Classification
        </div>
        <div style="font-size:48px;font-weight:900;color:{sc};margin:8px 0">Stage {overall}</div>
        <div style="font-size:18px;color:#f8fafc">{t_stage} · {n_stage} · {m_stage}</div>
        <div style="font-size:14px;color:rgba(255,255,255,0.6);margin-top:8px">
            5-Year Survival Rate: <b style="color:{sc}">{survival}</b>
        </div>
        <div style="margin-top:12px;background:rgba(255,255,255,0.06);border-radius:10px;padding:12px">
            <div style="font-size:13px;font-weight:700;color:#f8fafc">{subtype}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px">{subtype_prognosis}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Survival donut
    col_chart, col_rec = st.columns(2)
    with col_chart:
        surv_pct = int(survival.split("%")[0].split("–")[0])
        fig = go.Figure(go.Pie(
            values=[surv_pct, 100-surv_pct],
            labels=["5-Year Survival","Other"],
            hole=0.7,
            marker_colors=[sc,"#1e293b"],
            textinfo="none"
        ))
        fig.add_annotation(text=f"{surv_pct}%", x=0.5, y=0.5,
                           font_size=32, font_color=sc, showarrow=False, font_family="Arial Black")
        fig.update_layout(showlegend=False, paper_bgcolor="#0f172a",
                          height=250, margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_rec:
        st.subheader("Treatment Recommendation")
        recs = {
            1: ["Lumpectomy or mastectomy","Sentinel lymph node biopsy",
                "Radiation therapy (if lumpectomy)","Hormone therapy (if HR+)"],
            2: ["Surgery (lumpectomy/mastectomy)","Axillary lymph node dissection",
                "Chemotherapy (neoadjuvant or adjuvant)","Radiation therapy"],
            3: ["Neoadjuvant chemotherapy first","Surgery after response",
                "Radiation therapy","Targeted therapy (if HER2+)","Hormone therapy (if HR+)"],
            4: ["Systemic chemotherapy","Targeted therapy","Hormone therapy",
                "Palliative care planning","Bone-protecting agents if bone mets"]
        }
        for r in recs.get(stage_num, []):
            st.markdown(f'<div class="criterion-met">✓ {r}</div>', unsafe_allow_html=True)

    # Save
    conn = connect()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cancer_staging(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT, t_stage TEXT, n_stage TEXT, m_stage TEXT,
            overall_stage TEXT, subtype TEXT, survival_rate TEXT,
            created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
        )
    """)
    cur.execute("""
        INSERT INTO cancer_staging(patient_id,t_stage,n_stage,m_stage,overall_stage,subtype,survival_rate)
        VALUES(?,?,?,?,?,?,?)
    """, (patient_id, t_stage, n_stage, m_stage, overall, subtype, survival))
    conn.commit()
    conn.close()
    log_audit("CANCER_STAGING", "doctor", f"Patient {patient_id} staged as {overall}")
    st.success("✅ Staging saved to patient record!")
