# app.py  ← MAIN LANDING PAGE — REPLACE ENTIRE FILE
import streamlit as st
from database.database import connect
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Onco AI — Breast Cancer Detection System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help':    'mailto:onco@cmruniversity.edu.in',
        'Report a bug':'mailto:onco@cmruniversity.edu.in',
        'About':       "Onco AI — Breast Cancer Detection System\nCMR University, Bengaluru — 562149\n© 2026 Final Year Project"
    }
)

lang = render_sidebar()

from utils.language import get_text

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,[class*="css"]{font-family:'Inter',sans-serif !important;}
.stApp{background:#04080f !important;}
section[data-testid="stSidebar"]{background:#070c18 !important;}

/* HERO */
.hero-wrap{
    background:linear-gradient(135deg,#04080f 0%,#080f20 40%,#0c1830 70%,#04080f 100%);
    border:1px solid rgba(99,102,241,0.15);border-radius:20px;
    padding:52px 56px;margin-bottom:28px;position:relative;overflow:hidden;
}
.hero-wrap::before{
    content:'';position:absolute;top:-60px;right:-60px;
    width:400px;height:400px;border-radius:50%;
    background:radial-gradient(circle,rgba(99,102,241,0.08),transparent 70%);
    pointer-events:none;
}
.hero-badge{
    background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);
    border-radius:20px;padding:5px 14px;font-size:11px;font-weight:700;
    color:#a5b4fc;letter-spacing:1px;display:inline-block;margin-bottom:20px;
}
.hero-h1{font-size:52px;font-weight:900;line-height:1.1;letter-spacing:-1.5px;
          color:#f8fafc;margin-bottom:6px;}
.hero-h1 span{color:#ef4444;}
.hero-sub{font-size:16px;color:rgba(255,255,255,0.5);max-width:580px;
           line-height:1.75;margin:16px 0 28px 0;}
.hero-chip{
    background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);
    border-radius:20px;padding:6px 14px;font-size:11px;font-weight:600;
    color:rgba(255,255,255,0.55);display:inline-block;margin:3px;
}

/* STATS */
.stat-card{
    background:linear-gradient(145deg,#090f1e,#0e1829);
    border:1px solid rgba(255,255,255,0.06);border-radius:16px;
    padding:24px 20px;text-align:center;
}
.stat-num{
    font-size:42px;font-weight:900;
    background:linear-gradient(135deg,#60a5fa,#818cf8);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    line-height:1;
}
.stat-lbl{font-size:10px;font-weight:700;letter-spacing:1.5px;
           text-transform:uppercase;color:rgba(255,255,255,0.35);margin-top:6px;}

/* FEATURE CARDS */
.feat-card{
    background:linear-gradient(145deg,#090f1e,#0e1829);
    border:1px solid rgba(255,255,255,0.06);border-radius:16px;
    padding:22px 20px;height:100%;
    transition:all 0.25s;cursor:default;
}
.feat-card:hover{
    border-color:rgba(99,102,241,0.3);
    box-shadow:0 8px 32px rgba(0,0,0,0.4);
    transform:translateY(-3px);
}
.feat-icon{font-size:32px;margin-bottom:10px;}
.feat-title{font-size:14px;font-weight:800;color:#f0f6ff;margin-bottom:6px;}
.feat-desc{font-size:12px;color:rgba(255,255,255,0.42);line-height:1.65;}
.feat-tag{
    display:inline-block;padding:2px 8px;border-radius:5px;font-size:9px;
    font-weight:700;margin-top:8px;
    background:rgba(99,102,241,0.12);color:#a5b4fc;border:1px solid rgba(99,102,241,0.2);
}

/* PUBLICATION STRIP */
.pub-strip{
    background:linear-gradient(90deg,#070f20,#0c1830,#070f20);
    border:1px solid rgba(99,102,241,0.15);border-radius:14px;
    padding:16px 24px;margin:20px 0;
    display:flex;align-items:center;gap:10px;flex-wrap:wrap;
}
.pub-dot{width:6px;height:6px;border-radius:50%;background:#22c55e;flex-shrink:0;}
.pub-text{font-size:11px;color:rgba(255,255,255,0.4);font-weight:500;}

/* LOGIN PROMPT */
.login-prompt{
    background:linear-gradient(90deg,rgba(99,102,241,0.08),rgba(168,85,247,0.06));
    border:1px solid rgba(99,102,241,0.2);border-radius:14px;
    padding:16px 22px;text-align:center;margin-top:20px;
}
.stApp{background:#04080f !important;}
</style>
""", unsafe_allow_html=True)

# ── Live stats ────────────────────────────────────────────
conn = connect()
try:
    import pandas as pd
    total_patients = pd.read_sql_query("SELECT COUNT(*) as c FROM patients",  conn).iloc[0]['c']
    total_dx       = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis", conn).iloc[0]['c']
except:
    total_patients = 0; total_dx = 0
conn.close()

# ── HERO ──────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-badge">🧬 AI-POWERED MEDICAL PLATFORM · 2026</div>
  <div class="hero-h1">Onco <span>Breast Cancer</span><br>Detection System</div>
  <div class="hero-sub">
    A deep-learning powered clinical decision support platform using CNN &amp; VGG19
    for ultrasound image classification with Grad-CAM explainability,
    multi-language support, and comprehensive patient management.
  </div>
  <div>
    <span class="hero-chip">🤖 CNN + VGG19</span>
    <span class="hero-chip">🔥 GradCAM XAI</span>
    <span class="hero-chip">🌐 5 Languages</span>
    <span class="hero-chip">📊 93% Accuracy</span>
    <span class="hero-chip">📚 BUSI Dataset</span>
    <span class="hero-chip">📋 IEEE Ready</span>
    <span class="hero-chip">🏥 42+ Features</span>
    <span class="hero-chip">🚨 Emergency Locator</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
for col, val, lbl in [
    (c1, total_patients,  "REGISTERED PATIENTS"),
    (c2, total_dx,        "AI DIAGNOSES DONE"),
    (c3, "93%",           "MODEL ACCURACY"),
    (c4, "780",           "TRAINING IMAGES"),
]:
    col.markdown(f"""
    <div class="stat-card">
      <div class="stat-num">{val}</div>
      <div class="stat-lbl">{lbl}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature grid ──────────────────────────────────────────
FEATURES = [
    ("🤖","AI Breast Cancer Prediction","Upload ultrasound images for instant CNN classification into Benign, Malignant, or Normal with confidence scores.","Core AI"),
    ("🔥","Grad-CAM Explainability","Visual AI explanation showing exactly which regions of the ultrasound influenced the diagnosis — building doctor trust.","XAI"),
    ("🔄","Multi-Visit Comparison","Compare any two visits side by side with full clinical reports, BIRADS classification, and change analysis.","Clinical"),
    ("⚠️","Risk Assessment Engine","8-factor risk scoring with gauge chart. Flags high-risk patients for early screening and oncologist referral.","Prevention"),
    ("📊","Population Analytics","Epidemiology-level charts showing age-wise, gender-wise cancer distribution across your patient database.","Research"),
    ("🌐","5-Language Support","Full UI in English, Hindi, Telugu, Tamil, and Kannada — accessible to rural and regional healthcare providers.","Accessibility"),
    ("💬","AI Symptom Chatbot","Patients describe symptoms in natural language and get immediate guidance and triage advice.","Patient Care"),
    ("📄","Professional PDF Reports","Auto-generate CMR-branded PDF reports with QR codes, diagnosis history, confidence charts, and doctor notes.","Reporting"),
    ("📝","Digital Consent + Audit Trail","HIPAA-style digital consent forms and complete audit logging of every system action for medical compliance.","Compliance"),
    ("🏥","OPD Queue Management","Government-style patient token system. Urgent-first queue with analytics — just like AIIMS/Apollo.","Operations"),
    ("💊","Treatment Tracker","Track chemotherapy cycles, medications, follow-up schedule — full oncology workflow in one system.","Treatment"),
    ("🚨","Emergency Hospital Locator","Real GPS-powered locator for nearest cancer hospitals with one-tap directions and WhatsApp alerts.","Emergency"),
    ("🌐","Federated Learning Network","Multi-hospital AI collaboration across 8 hospitals in India — model improves without sharing patient data.","2028"),
    ("🧬","Genomics AI","BRCA1/BRCA2 mutation analysis, lifetime risk calculator, India-specific population genetics.","2029"),
    ("⌚","Patient Wearables & IoT","Real-time vitals from smartwatches, ECG patches — live monitoring during chemotherapy sessions.","2028"),
]

cols = st.columns(3)
for i, (icon, title, desc, tag) in enumerate(FEATURES):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="feat-card">
          <div class="feat-icon">{icon}</div>
          <div class="feat-title">{title}</div>
          <div class="feat-desc">{desc}</div>
          <span class="feat-tag">{tag}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

# ── Publication strip ─────────────────────────────────────
st.markdown("""
<div class="pub-strip">
  <div class="pub-dot"></div><div class="pub-text">IEEE Publication Ready</div>
  <div class="pub-dot"></div><div class="pub-text">UGC CARE Listed Journal Compatible</div>
  <div class="pub-dot"></div><div class="pub-text">Scopus Standard</div>
  <div class="pub-dot"></div><div class="pub-text">BUSI Dataset (CMR University)</div>
  <div class="pub-dot"></div><div class="pub-text">Keras + TensorFlow 2.13</div>
  <div class="pub-dot"></div><div class="pub-text">Government Hospital Ready (ICMR/NHA/ABDM)</div>
  <div class="pub-dot"></div><div class="pub-text">System Running Live ✓</div>
</div>
""", unsafe_allow_html=True)

# Login prompt
if not st.session_state.get("logged_in"):
    st.markdown(f"""
    <div class="login-prompt">
      👉 {get_text('please_login', lang)} — Use <b>admin / admin</b>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success(f"✅ Logged in as **{st.session_state.get('username','Doctor')}** — Use the sidebar to navigate.")

# Footer
st.markdown("""
<div style="text-align:center;margin-top:32px;padding:20px 0;
            border-top:1px solid rgba(255,255,255,0.05)">
  <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,0.3)">
    🏥 CMR University, Bengaluru — 562149
    &nbsp;·&nbsp; 📞 9342900666
    &nbsp;·&nbsp; 📧 onco@cmruniversity.edu.in
    &nbsp;·&nbsp; 🌐 www.cmruniversity.edu.in
  </div>
  <div style="font-size:11px;color:rgba(255,255,255,0.18);margin-top:6px">
    © 2026 Onco AI — Final Year Project · CMR University Bengaluru Lakeside Campus
    · Built by Final Year Students · All Rights Reserved
  </div>
</div>
""", unsafe_allow_html=True)
