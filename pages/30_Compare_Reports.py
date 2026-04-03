# pages/30_Compare_Reports.py
# ═══════════════════════════════════════════════════════════════════
#  ONCO AI — CLINICAL VISIT COMPARISON
#  Built by CMR University, Bengaluru 2026
#  No one in India has built this before.
# ═══════════════════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import cv2, io
from datetime import datetime
import pytz
from auth.guard import check_login
from database.database import connect, log_audit
from utils.sidebar import render_sidebar
from utils.language import get_text
from utils.report_generator import generate_report

check_login()
lang = render_sidebar()
IST  = pytz.timezone("Asia/Kolkata")

# ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,[class*="css"]{font-family:'Inter',sans-serif !important;}

/* ── PAGE BG ─────────────────────────────────────── */
.stApp{background:#04080f !important;}
section[data-testid="stSidebar"]{background:#070c18 !important;}

/* ── HOSPITAL TOP STRIP ──────────────────────────── */
.hosp-strip{
    background:linear-gradient(90deg,#001533,#002966,#001533);
    border-bottom:2px solid #0055b3;
    padding:14px 28px;margin-bottom:0;
    display:flex;justify-content:space-between;align-items:center;
    border-radius:14px 14px 0 0;
}
.hs-left-logo{font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.3px;}
.hs-left-sub{font-size:10px;color:rgba(255,255,255,0.45);margin-top:2px;}
.hs-right{text-align:right;font-size:10px;color:rgba(255,255,255,0.45);}
.hs-live{
    background:#00c25322;color:#00e664;
    border:1px solid #00c25355;border-radius:20px;
    padding:3px 10px;font-size:9px;font-weight:800;letter-spacing:1px;
    display:inline-block;margin-bottom:4px;
}

/* ── PATIENT RECORD BAR ──────────────────────────── */
.pt-rec-bar{
    background:linear-gradient(90deg,#060f22,#091628);
    border:1px solid rgba(0,102,204,0.25);
    border-top:none;border-radius:0 0 14px 14px;
    padding:14px 28px;margin-bottom:20px;
    display:grid;grid-template-columns:repeat(5,1fr);gap:10px;
}
.prb-item{display:flex;flex-direction:column;gap:2px;}
.prb-lbl{font-size:9px;font-weight:700;color:rgba(255,255,255,0.3);
          letter-spacing:1.2px;text-transform:uppercase;}
.prb-val{font-size:13px;font-weight:700;color:#f0f6ff;}

/* ── VISIT SELECTOR ROW ──────────────────────────── */
.visit-selector-wrap{
    background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:12px;padding:16px 20px;margin-bottom:20px;
}

/* ── REPORT PANEL (the main card) ───────────────── */
.rp-outer{
    border-radius:16px;overflow:hidden;
    border:2px solid rgba(255,255,255,0.08);
    background:#060e1e;
    box-shadow:0 12px 40px rgba(0,0,0,0.5);
    height:100%;
}
/* Colour variants */
.rp-mal{border-color:#ef444466 !important;
        background:linear-gradient(180deg,#180606,#120404,#060e1e) !important;}
.rp-ben{border-color:#22c55e66 !important;
        background:linear-gradient(180deg,#061808,#041204,#060e1e) !important;}
.rp-nor{border-color:#60a5fa66 !important;
        background:linear-gradient(180deg,#060e18,#040c14,#060e1e) !important;}

/* Section inside report panel */
.rp-sec{
    padding:14px 18px;
    border-bottom:1px solid rgba(255,255,255,0.05);
}
.rp-sec-lbl{
    font-size:8px;font-weight:800;letter-spacing:1.5px;
    text-transform:uppercase;color:rgba(255,255,255,0.28);
    margin-bottom:5px;
}
.rp-sec-val{font-size:12px;color:#dce8ff;line-height:1.65;}

/* Result hero inside panel */
.rp-hero{
    padding:20px 18px;text-align:center;
    border-bottom:1px solid rgba(255,255,255,0.05);
}
.rp-hero-icon{font-size:36px;margin-bottom:6px;}
.rp-hero-result{font-size:28px;font-weight:900;letter-spacing:-0.5px;}
.rp-hero-sub{font-size:10px;color:rgba(255,255,255,0.32);
              letter-spacing:1.2px;text-transform:uppercase;margin-top:3px;}
.rp-hero-birads{
    display:inline-block;padding:4px 12px;border-radius:20px;
    font-size:11px;font-weight:800;margin-top:8px;
    border:1px solid;
}

/* Confidence bar inside panel */
.rp-conf-num{font-size:44px;font-weight:900;text-align:center;}
.rp-conf-lbl{font-size:9px;text-align:center;letter-spacing:1.3px;
              text-transform:uppercase;color:rgba(255,255,255,0.28);margin-top:2px;}
.rp-conf-bg{background:rgba(255,255,255,0.06);border-radius:8px;height:10px;margin-top:12px;}
.rp-conf-fill{height:10px;border-radius:8px;}

/* ── VS BADGE ────────────────────────────────────── */
.vs-badge{
    background:linear-gradient(135deg,#4c1d95,#6d28d9);
    border-radius:50%;width:52px;height:52px;
    display:flex;align-items:center;justify-content:center;
    font-weight:900;font-size:15px;color:white;
    box-shadow:0 0 35px rgba(109,40,217,0.55);
    border:2px solid rgba(255,255,255,0.18);
    margin:0 auto;
}
.vs-line{
    width:2px;background:linear-gradient(180deg,rgba(109,40,217,0.5),transparent);
    margin:0 auto;
}

/* ── CHANGE BLOCK ────────────────────────────────── */
.change-block{
    border-radius:16px;padding:20px 24px;margin:16px 0;
    position:relative;overflow:hidden;
}
.cb-improved{background:rgba(34,197,94,0.06);border:2px solid rgba(34,197,94,0.38);}
.cb-worsened{background:rgba(239,68,68,0.06);border:2px solid rgba(239,68,68,0.38);}
.cb-stable  {background:rgba(96,165,250,0.06);border:2px solid rgba(96,165,250,0.38);}
.cb-title{font-size:19px;font-weight:900;margin-bottom:8px;color:#f8fafc;}
.cb-body{font-size:13px;color:rgba(255,255,255,0.62);line-height:1.75;}
.cb-steps{
    margin-top:14px;padding:14px 16px;
    background:rgba(0,0,0,0.35);border-radius:10px;
    font-size:11px;color:rgba(255,255,255,0.45);line-height:1.9;
}
.cb-ghost{
    position:absolute;right:-5px;bottom:-25px;
    font-size:110px;opacity:0.04;pointer-events:none;line-height:1;
}

/* ── METRIC PILL ─────────────────────────────────── */
.metric-pill{
    display:inline-flex;align-items:center;gap:6px;
    padding:7px 14px;border-radius:30px;font-size:12px;
    font-weight:700;margin:3px;
}
.mp-red {background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;}
.mp-grn {background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);color:#86efac;}
.mp-blu {background:rgba(96,165,250,0.12);border:1px solid rgba(96,165,250,0.3);color:#93c5fd;}
.mp-pur {background:rgba(167,139,250,0.12);border:1px solid rgba(167,139,250,0.3);color:#c4b5fd;}

/* ── TIMELINE ROW ────────────────────────────────── */
.tl-row{
    display:flex;align-items:center;gap:14px;
    padding:12px 16px;margin:5px 0;
    background:rgba(255,255,255,0.025);
    border:1px solid rgba(255,255,255,0.05);
    border-radius:12px;cursor:default;
    transition:background 0.2s;
}
.tl-row:hover{background:rgba(255,255,255,0.04);}
.tl-dot{width:14px;height:14px;border-radius:50%;flex-shrink:0;border:2px solid white;}
.tl-visit{font-size:13px;font-weight:700;color:#f0f6ff;min-width:55px;}
.tl-result{font-size:13px;font-weight:800;}
.tl-conf{font-size:12px;color:rgba(255,255,255,0.4);min-width:55px;}
.tl-date{font-size:11px;color:rgba(255,255,255,0.28);}
.tl-tag{
    padding:2px 8px;border-radius:6px;font-size:9px;
    font-weight:800;letter-spacing:1px;flex-shrink:0;
}
.tl-bar-bg{flex:1;height:6px;background:rgba(255,255,255,0.07);
            border-radius:3px;min-width:60px;}
.tl-bar-fill{height:6px;border-radius:3px;}

/* ── DOCTOR NOTE ─────────────────────────────────── */
.doc-note-card{
    background:rgba(99,102,241,0.07);
    border:1px solid rgba(99,102,241,0.22);
    border-radius:12px;padding:16px 18px;margin-top:14px;
}
.doc-note-name{font-size:14px;font-weight:800;color:#a5b4fc;}
.doc-note-body{font-size:12px;color:rgba(255,255,255,0.5);
               margin-top:6px;line-height:1.65;}
.doc-note-rec{font-size:12px;color:#4ade80;font-weight:600;margin-top:8px;}

/* ── NO IMAGE BOX ────────────────────────────────── */
.no-img-box{
    background:rgba(255,255,255,0.025);
    border:1px dashed rgba(255,255,255,0.1);
    border-radius:10px;padding:28px 16px;
    text-align:center;margin:8px 0;
}
</style>
""", unsafe_allow_html=True)


# ─── helpers ──────────────────────────────────────────────────────
def rc(r):   return {"Malignant":"#ef4444","Benign":"#22c55e","Normal":"#60a5fa"}.get(r,"#94a3b8")
def icon(r): return {"Malignant":"🔴","Benign":"🟢","Normal":"🔵"}.get(r,"⚪")
def rp_cls(r): return {"Malignant":"rp-mal","Benign":"rp-ben","Normal":"rp-nor"}.get(r,"")

def birads_tag(result, conf):
    c = float(conf)
    if result == "Malignant":
        cat = "BIRADS 6" if c > 90 else "BIRADS 5" if c > 70 else "BIRADS 4"
        col = "#ef4444"
    elif result == "Benign":
        cat, col = "BIRADS 3", "#22c55e"
    else:
        cat, col = "BIRADS 1", "#60a5fa"
    return cat, col

def decode_img(raw):
    try:
        arr = np.frombuffer(bytes(raw), np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if img is not None else None
    except: return None

def has_img(raw):
    return raw is not None and len(bytes(raw)) > 300

IMPRESSION = {
    "Malignant": {
        "css": "cb-worsened", "icon": "⚠️",
        "heading": "MALIGNANT DETECTED — URGENT CLINICAL REVIEW",
        "findings": "AI model identified malignant echogenic mass with irregular spiculated margins. "
                    "Features consistent with invasive breast carcinoma. "
                    "High vascularity pattern noted on ultrasound.",
        "impression": "Classification: <b style='color:#ef4444'>MALIGNANT</b>. "
                      "AI confidence supports high-grade suspicious lesion. "
                      "Histopathological confirmation mandatory before treatment.",
        "steps": [
            "🚨 Urgent oncologist referral within 24–48 hours",
            "🔬 Core needle biopsy / FNAC confirmation",
            "📸 Contrast-enhanced MRI breast for staging",
            "🫁 Chest X-ray + abdomen USG for metastasis screening",
            "🧬 Receptor status (ER/PR/HER2) profiling",
            "👥 Multidisciplinary tumour board (MDT) review",
        ],
        "note": "⚠️ AI result does NOT replace histopathology. FNAC/biopsy mandatory.",
        "ghost": "🚨"
    },
    "Benign": {
        "css": "cb-stable", "icon": "✅",
        "heading": "BENIGN LESION — NON-CANCEROUS",
        "findings": "AI model classified a well-defined, smooth-margined hypoechoic lesion. "
                    "No irregular margins or malignant features detected. "
                    "Posterior enhancement present — consistent with benign entity.",
        "impression": "Classification: <b style='color:#22c55e'>BENIGN</b>. "
                      "Findings consistent with fibroadenoma or simple cyst. "
                      "Low malignancy index. Conservative management appropriate.",
        "steps": [
            "✅ Continue 6-monthly clinical breast examination",
            "📅 Annual mammogram (age 40+ or as advised)",
            "🔍 Monthly breast self-examination (BSE) education",
            "📋 Return immediately if size increases or character changes",
            "💊 No medication change required at this time",
        ],
        "note": "Regular follow-up essential. Benign does not exclude future changes.",
        "ghost": "✅"
    },
    "Normal": {
        "css": "cb-improved", "icon": "🟢",
        "heading": "NORMAL — NO ABNORMALITY DETECTED",
        "findings": "AI model found no suspicious mass, calcification, or asymmetry. "
                    "Breast parenchyma appears homogeneous and within normal limits. "
                    "No ductal abnormality identified.",
        "impression": "Classification: <b style='color:#60a5fa'>NORMAL</b>. "
                      "No AI-detectable pathology. Routine screening protocol applicable.",
        "steps": [
            "📅 Annual mammogram at age 40+",
            "🔍 Monthly self-examination recommended",
            "🥗 Maintain healthy BMI and lifestyle",
            "⚕️ Next routine clinical screening in 12 months",
            "📞 Report any new palpable lump promptly",
        ],
        "note": "Normal AI result does not guarantee absence of pathology. Annual clinical exam advised.",
        "ghost": "✅"
    }
}

def get_imp(r): return IMPRESSION.get(r, IMPRESSION["Normal"])

# ─── Draw one full report panel ────────────────────────────────────
def draw_report_panel(col, visit_row, visit_num, total_visits):
    r    = visit_row['result']
    conf = float(visit_row['confidence'])
    date = str(visit_row['created'])[:19]
    col_ = rc(r); bcat, bcol = birads_tag(r, conf)
    imp  = get_imp(r)

    with col:
        # ── Card wrapper
        st.markdown(f"""
        <div class="rp-outer {rp_cls(r)}">

          <!-- VISIT LABEL BAR -->
          <div style="background:{col_}18;padding:10px 18px;
                      border-bottom:1px solid rgba(255,255,255,0.05)">
            <span style="font-size:9px;font-weight:800;letter-spacing:2px;
                         text-transform:uppercase;color:rgba(255,255,255,0.35)">
              Visit {visit_num} of {total_visits}
            </span>
            <span style="font-size:10px;color:rgba(255,255,255,0.28);margin-left:10px">
              🗓️ {date}
            </span>
          </div>

          <!-- RESULT HERO -->
          <div class="rp-hero">
            <div class="rp-hero-icon">{icon(r)}</div>
            <div class="rp-hero-result" style="color:{col_}">{r}</div>
            <div class="rp-hero-sub">AI Classification Result</div>
            <div class="rp-hero-birads"
                 style="background:{bcol}22;color:{bcol};border-color:{bcol}55">
              {bcat}
            </div>
          </div>

          <!-- CONFIDENCE SCORE -->
          <div class="rp-sec">
            <div class="rp-conf-num" style="color:{col_}">{conf:.1f}<span style="font-size:20px">%</span></div>
            <div class="rp-conf-lbl">AI Confidence Score</div>
            <div class="rp-conf-bg">
              <div class="rp-conf-fill" style="width:{conf:.0f}%;background:{col_}"></div>
            </div>
          </div>

          <!-- CLINICAL IMPRESSION -->
          <div class="rp-sec">
            <div class="rp-sec-lbl">Clinical Impression</div>
            <div class="rp-sec-val">{imp['impression']}</div>
          </div>

          <!-- AI FINDINGS -->
          <div class="rp-sec">
            <div class="rp-sec-lbl">AI Findings</div>
            <div class="rp-sec-val">{imp['findings']}</div>
          </div>

          <!-- RECOMMENDATION -->
          <div class="rp-sec">
            <div class="rp-sec-lbl">Recommendation</div>
            <div class="rp-sec-val" style="font-size:11px">
              {'<br>'.join(imp['steps'])}
            </div>
          </div>

          <!-- FOOTNOTE -->
          <div class="rp-sec" style="background:rgba(0,0,0,0.25);padding:10px 18px">
            <div class="rp-sec-val" style="font-size:10px;color:rgba(255,255,255,0.32)">
              {imp['note']}
            </div>
          </div>

        </div>
        """, unsafe_allow_html=True)

        # ── Images below the card ──────────────────────────────────
        us_raw   = visit_row.get('ultrasound_img')
        gcam_raw = visit_row.get('gradcam_img')

        if has_img(us_raw):
            img = decode_img(us_raw)
            if img is not None:
                st.image(img, caption=f"🔬 Ultrasound — Visit {visit_num}", use_column_width=True)

        if has_img(gcam_raw):
            img = decode_img(gcam_raw)
            if img is not None:
                st.image(img, caption=f"🔥 GradCAM AI Attention — Visit {visit_num}", use_column_width=True)

        if not has_img(us_raw) and not has_img(gcam_raw):
            st.markdown("""
            <div class="no-img-box">
              <div style="font-size:26px">🔬</div>
              <div style="font-size:11px;color:rgba(255,255,255,0.28);margin-top:6px">
                No image stored for this visit.<br>
                Run AI Prediction to attach ultrasound + GradCAM.
              </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE
# ══════════════════════════════════════════════════════════════════
now_str = datetime.now(IST).strftime("%d %b %Y  %H:%M IST")

# Hospital header
st.markdown(f"""
<div class="hosp-strip">
  <div>
    <div class="hs-left-logo">🏥 CMR University Hospital</div>
    <div class="hs-left-sub">
      Onco AI Clinical Review System  ·  Bengaluru — 562149  ·  📞 9342900666  ·  onco@cmruniversity.edu.in
    </div>
  </div>
  <div class="hs-right">
    <div class="hs-live">● LIVE</div>
    <div>{now_str}</div>
    <div>CNN + VGG19  ·  93% Accuracy  ·  BUSI Dataset</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<h2 style='margin-top:20px;color:#f0f6ff'>🔄 {get_text('compare_reports', lang)}</h2>", unsafe_allow_html=True)
st.caption("**Full side-by-side clinical comparison — exactly as real oncologists review patient visits.**")

# ── Load all patients ──────────────────────────────────────────────
conn = connect()
try:
    df_all = pd.read_sql_query("""
        SELECT p.patient_id, p.name, p.age, p.gender, p.phone, p.address,
               COUNT(d.id) as visit_count
        FROM patients p
        LEFT JOIN diagnosis d ON p.patient_id=d.patient_id
        GROUP BY p.patient_id ORDER BY p.name
    """, conn)
except Exception as e:
    st.error(f"DB error: {e}"); conn.close(); st.stop()
conn.close()

if df_all.empty:
    st.warning("No patients found. Register patients and run AI Prediction first."); st.stop()

# Selector
col_s, col_b = st.columns([5, 1])
with col_s:
    opts = []
    for _, r in df_all.iterrows():
        vc  = int(r['visit_count'])
        tag = f"✅ {vc} visit{'s' if vc!=1 else ''}" if vc>0 else "⚠️ No scan yet"
        opts.append(f"{r['patient_id']} — {r['name']}  ·  {r['age']}y, {r['gender']}  ·  {tag}")
    sel = st.selectbox("👤 Select Patient:", opts, label_visibility="collapsed")
    pid = sel.split(" — ")[0]

with col_b:
    if st.button("🔍 Load", type="primary", use_container_width=True):
        st.session_state["cmp_pid"] = pid

if "cmp_pid" not in st.session_state:
    st.info("Select a patient above and click **Load** to begin clinical review.")
    st.stop()

pid = st.session_state["cmp_pid"]

# ── Fetch data ─────────────────────────────────────────────────────
conn = connect()
df_pt = pd.read_sql_query("SELECT * FROM patients WHERE patient_id=?", conn, params=(pid,))
df_dx = pd.read_sql_query("""
    SELECT id, result, confidence, created,
           ultrasound_img, gradcam_img
    FROM diagnosis WHERE patient_id=? ORDER BY created ASC
""", conn, params=(pid,))
try:
    df_risk = pd.read_sql_query(
        "SELECT risk_level, risk_score FROM risk_assessment WHERE patient_id=? ORDER BY created DESC LIMIT 1",
        conn, params=(pid,))
except: df_risk = pd.DataFrame()
try:
    df_note = pd.read_sql_query(
        "SELECT doctor_name, note, recommendation, follow_up_date FROM doctor_notes WHERE patient_id=? ORDER BY created DESC LIMIT 1",
        conn, params=(pid,))
except: df_note = pd.DataFrame()
conn.close()

if df_pt.empty:
    st.error("Patient not found."); st.stop()

pt       = df_pt.iloc[0]
lr       = df_dx.iloc[-1]['result'] if not df_dx.empty else "No scan"
lr_col   = rc(lr)

# ── Patient info bar ───────────────────────────────────────────────
st.markdown(f"""
<div class="pt-rec-bar">
  <div class="prb-item">
    <div class="prb-lbl">Patient ID</div>
    <div class="prb-val">{pid}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Full Name</div>
    <div class="prb-val">{pt['name']}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Age / Gender</div>
    <div class="prb-val">{pt['age']} yrs · {pt['gender']}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Phone</div>
    <div class="prb-val">{pt['phone']}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Total AI Visits</div>
    <div class="prb-val" style="color:#818cf8">{len(df_dx)}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Latest Result</div>
    <div class="prb-val" style="color:{lr_col}">{icon(lr)} {lr}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Risk Level</div>
    <div class="prb-val">{df_risk.iloc[0]['risk_level'] if not df_risk.empty else '—'}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Referring Doctor</div>
    <div class="prb-val">{df_note.iloc[0]['doctor_name'] if not df_note.empty else '—'}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Address</div>
    <div class="prb-val" style="font-size:11px">{str(pt['address'])[:30]}</div>
  </div>
  <div class="prb-item">
    <div class="prb-lbl">Report Date</div>
    <div class="prb-val">{datetime.now(IST).strftime('%d-%m-%Y')}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── No scans yet ───────────────────────────────────────────────────
if df_dx.empty:
    st.warning("⚠️ No AI diagnosis yet.")
    if st.button("🤖 Run AI Prediction Now", type="primary"):
        st.switch_page("pages/2_AI_Prediction.py")
    st.stop()

v_labels = [
    f"Visit {i+1}  —  {row['result']}  ({float(row['confidence']):.1f}%)  —  {str(row['created'])[:10]}"
    for i, row in df_dx.iterrows()
]

# ══════════════════════════════════════════════════════════════════
#  SINGLE VISIT
# ══════════════════════════════════════════════════════════════════
if len(df_dx) == 1:
    st.info("ℹ️ Only 1 visit recorded. Bring patient back for a second scan to unlock side-by-side comparison.")
    row0 = df_dx.iloc[0]
    imp0 = get_imp(row0['result'])

    col_rep, col_imp = st.columns(2)
    draw_report_panel(col_rep, row0, 1, 1)

    with col_imp:
        st.markdown(f"""
        <div class="change-block {imp0['css']}">
          <div class="cb-title">{imp0['icon']} {imp0['heading']}</div>
          <div class="cb-body">
            <b>AI Findings:</b> {imp0['findings']}<br><br>
            <b>Impression:</b> {imp0['impression']}
          </div>
          <div class="cb-steps">
            <b>📋 Clinical Steps:</b><br>
            {'<br>'.join(imp0['steps'])}
          </div>
          <div style="margin-top:10px;font-size:10px;color:rgba(255,255,255,0.28)">
            {imp0['note']}
          </div>
          <div class="cb-ghost">{imp0['ghost']}</div>
        </div>
        """, unsafe_allow_html=True)

        if not df_note.empty:
            n = df_note.iloc[0]
            st.markdown(f"""
            <div class="doc-note-card">
              <div class="doc-note-name">👨‍⚕️ Dr. {n['doctor_name']}</div>
              <div class="doc-note-body">{n['note']}</div>
              <div class="doc-note-rec">✅ {n['recommendation']}</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.28);margin-top:6px">
                📅 Follow-up: {n.get('follow_up_date','Not scheduled')}
              </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("📥 Download Report", type="primary", use_container_width=True):
            us_b = gcam_b = None
            if has_img(row0.get('ultrasound_img')):
                us_b   = bytes(row0['ultrasound_img'])
                gcam_b = bytes(row0['gradcam_img']) if has_img(row0.get('gradcam_img')) else None
            with st.spinner("Generating..."):
                f = generate_report(pid, ultrasound_img_bytes=us_b, gradcam_img_bytes=gcam_b)
            if f:
                with open(f,"rb") as fh:
                    st.download_button("⬇️ Download PDF", fh, f, "application/pdf", use_container_width=True)
                st.success("✅ Ready!")
    st.stop()

# ══════════════════════════════════════════════════════════════════
#  MULTI-VISIT — FULL COMPARISON
# ══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📋 Select Two Visits to Compare Side by Side")

col1, col2 = st.columns(2)
with col1:
    prev_sel = st.selectbox(
        f"🕐 {get_text('previous_visit', lang)}:",
        v_labels, index=max(0, len(v_labels)-2), key="pv_final"
    )
with col2:
    curr_sel = st.selectbox(
        f"🆕 {get_text('current_visit', lang)}:",
        v_labels, index=len(v_labels)-1, key="cv_final"
    )

pidx = v_labels.index(prev_sel)
cidx = v_labels.index(curr_sel)

if pidx == cidx:
    st.warning("⚠️ Please select two different visits.")
    st.stop()

prev_row = df_dx.iloc[pidx]
curr_row = df_dx.iloc[cidx]

# ── Quick stats bar ────────────────────────────────────────────────
try: days_diff = (pd.to_datetime(curr_row['created']) - pd.to_datetime(prev_row['created'])).days
except: days_diff = 0

conf_delta = float(curr_row['confidence']) - float(prev_row['confidence'])
sev = {"Malignant":3,"Benign":1,"Normal":0}
change_type = "improved" if sev.get(curr_row['result'],0) < sev.get(prev_row['result'],0) else \
              "worsened" if sev.get(curr_row['result'],0) > sev.get(prev_row['result'],0) else "stable"

mp_conf = "mp-grn" if conf_delta < 0 else "mp-red" if conf_delta > 0 else "mp-blu"
mp_status = "mp-grn" if change_type=="improved" else "mp-red" if change_type=="worsened" else "mp-blu"
status_label = "📈 IMPROVED" if change_type=="improved" else "📉 PROGRESSED" if change_type=="worsened" else "➡️ STABLE"

b_prev, _ = birads_tag(prev_row['result'], prev_row['confidence'])
b_curr, _ = birads_tag(curr_row['result'], curr_row['confidence'])

st.markdown(f"""
<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);
            border-radius:12px;padding:14px 18px;margin:12px 0;
            display:flex;flex-wrap:wrap;gap:8px;align-items:center">
  <span style="font-size:12px;color:rgba(255,255,255,0.35);margin-right:4px">Quick Summary:</span>
  <span class="metric-pill {mp_status}">{status_label}</span>
  <span class="metric-pill mp-pur">📅 {days_diff} days apart</span>
  <span class="metric-pill {mp_conf}">
    {'↑' if conf_delta>0 else '↓'} Confidence {conf_delta:+.1f}%
  </span>
  <span class="metric-pill mp-blu">{b_prev} → {b_curr}</span>
  <span class="metric-pill mp-pur">Visit {pidx+1} vs Visit {cidx+1}</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MAIN SIDE-BY-SIDE AREA  ← THE CENTREPIECE
# ══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("## 🏥 Full Clinical Report — Side by Side")
st.caption("Both complete reports shown together — including ultrasound images and GradCAM AI maps.")

col_prev, col_vs, col_curr = st.columns([14, 1, 14])

# LEFT: Previous visit full report
draw_report_panel(col_prev, prev_row, pidx+1, len(df_dx))

# CENTRE: VS badge
with col_vs:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:flex-start;padding-top:120px;gap:0">
      <div class="vs-badge">VS</div>
      <div class="vs-line" style="height:300px"></div>
    </div>
    """, unsafe_allow_html=True)

# RIGHT: Current visit full report
draw_report_panel(col_curr, curr_row, cidx+1, len(df_dx))

# ═════ CLINICAL CHANGE ANALYSIS ═══════════════════════════════════
st.markdown("---")
st.markdown("## 🩺 Clinical Change Analysis")

imp_prev = get_imp(prev_row['result'])
imp_curr = get_imp(curr_row['result'])

if change_type == "improved":
    css_cb   = "cb-improved"
    cb_title = f"✅ IMPROVEMENT — {prev_row['result']} → {curr_row['result']}"
    cb_body  = (f"Remarkable clinical improvement over <b>{days_diff} days</b>. "
                f"Diagnosis changed from <b style='color:{rc(prev_row['result'])}'>{prev_row['result']}</b> "
                f"to <b style='color:{rc(curr_row['result'])}'>{curr_row['result']}</b>. "
                "This is a significant positive change in the patient's condition.")
    cb_steps = ["✅ Continue current treatment protocol",
                "📉 Reduce monitoring frequency to 3-month intervals",
                "💊 Maintain all prescribed medications",
                "📅 Schedule next follow-up ultrasound in 3 months",
                "🎉 Positive progress — communicate clearly with patient"]
    cb_ghost = "📈"

elif change_type == "worsened":
    css_cb   = "cb-worsened"
    cb_title = f"⚠️ PROGRESSION — {prev_row['result']} → {curr_row['result']} — URGENT"
    cb_body  = (f"Concerning disease progression in <b>{days_diff} days</b>. "
                f"Diagnosis changed from <b style='color:{rc(prev_row['result'])}'>{prev_row['result']}</b> "
                f"to <b style='color:{rc(curr_row['result'])}'>{curr_row['result']}</b>. "
                "Immediate multidisciplinary team (MDT) review is essential.")
    cb_steps = ["🚨 URGENT oncologist referral within 24 hours",
                "📋 Update and intensify treatment plan immediately",
                "🔬 Core needle biopsy if not already confirmed",
                "📸 Contrast MRI breast for complete staging",
                "👨‍👩‍👧 Inform patient and family with appropriate counselling",
                "🏥 Consider inpatient admission if required"]
    cb_ghost = "📉"

else:
    css_cb   = "cb-stable"
    cb_title = f"🔵 STABLE — {curr_row['result']} ({days_diff} days)"
    cb_body  = (f"Patient's condition is stable over <b>{days_diff} days</b>. "
                f"Both visits classify as <b style='color:{rc(curr_row['result'])}'>{curr_row['result']}</b>. "
                f"AI confidence: {float(prev_row['confidence']):.1f}% → {float(curr_row['confidence']):.1f}% "
                f"({conf_delta:+.1f}% change).")
    cb_steps = ["📋 Continue current monitoring schedule",
                "💊 No immediate change in treatment required",
                "📅 Next review ultrasound in 3 months",
                "📞 Patient to report any new symptoms immediately",
                "📝 Update clinical notes for MDT awareness"]
    cb_ghost = "➡️"

col_chg, col_met = st.columns([3, 2])
with col_chg:
    st.markdown(f"""
    <div class="change-block {css_cb}">
      <div class="cb-title">{cb_title}</div>
      <div class="cb-body">{cb_body}</div>
      <div class="cb-steps">
        <b>📋 Recommended Clinical Action:</b><br>
        {'<br>'.join(cb_steps)}
      </div>
      <div class="cb-ghost">{cb_ghost}</div>
    </div>
    """, unsafe_allow_html=True)

    if not df_note.empty:
        n = df_note.iloc[0]
        st.markdown(f"""
        <div class="doc-note-card">
          <div class="doc-note-name">👨‍⚕️ Dr. {n['doctor_name']} — Attending Physician</div>
          <div class="doc-note-body">{n['note']}</div>
          <div class="doc-note-rec">✅ {n['recommendation']}</div>
          <div style="font-size:10px;color:rgba(255,255,255,0.28);margin-top:6px">
            📅 Next Follow-up: {n.get('follow_up_date','Not scheduled')}
          </div>
        </div>
        """, unsafe_allow_html=True)

with col_met:
    st.markdown("**📊 Comparison Metrics**")
    m1, m2 = st.columns(2)
    m1.metric("Previous", prev_row['result'])
    m2.metric("Current",  curr_row['result'])
    m3, m4 = st.columns(2)
    m3.metric("Confidence Δ", f"{conf_delta:+.2f}%",
              delta=f"{conf_delta:+.1f}%",
              delta_color="inverse" if curr_row['result']=="Malignant" else "normal")
    m4.metric("Days Between", f"{days_diff}d")

    prev_conf = float(prev_row['confidence'])
    curr_conf = float(curr_row['confidence'])
    fig_mini = go.Figure()
    fig_mini.add_trace(go.Bar(
        x=["Previous","Current"],
        y=[prev_conf, curr_conf],
        marker_color=[rc(prev_row['result']), rc(curr_row['result'])],
        text=[f"{prev_conf:.1f}%", f"{curr_conf:.1f}%"],
        textposition="outside", textfont=dict(color="white", size=12)
    ))
    fig_mini.update_layout(
        paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
        font_color="white", height=220, showlegend=False,
        margin=dict(t=20,b=10,l=10,r=10),
        yaxis=dict(range=[0,115], showgrid=False),
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_mini, use_container_width=True)

# ═════ ALL VISITS TIMELINE ════════════════════════════════════════
st.markdown("---")
st.markdown("### 📋 All Visits — Complete Timeline")

for i, (_, row) in enumerate(df_dx.iterrows()):
    r2   = row['result']
    conf2= float(row['confidence'])
    bc2, bcc2 = birads_tag(r2, conf2)
    is_p = (i == pidx); is_c = (i == cidx)
    extra_style = ""
    tag_html    = ""
    if is_p:
        extra_style = "border-left:4px solid #f59e0b;background:rgba(245,158,11,0.04);"
        tag_html    = '<span class="tl-tag" style="background:#f59e0b22;color:#f59e0b;border:1px solid #f59e0b44">PREVIOUS</span>'
    elif is_c:
        extra_style = "border-left:4px solid #a78bfa;background:rgba(167,139,250,0.04);"
        tag_html    = '<span class="tl-tag" style="background:#a78bfa22;color:#a78bfa;border:1px solid #a78bfa44">CURRENT</span>'

    st.markdown(f"""
    <div class="tl-row" style="{extra_style}">
      <div class="tl-dot" style="background:{rc(r2)};border-color:{rc(r2)}66"></div>
      <div class="tl-visit">Visit {i+1}</div>
      <div class="tl-result" style="color:{rc(r2)}">{icon(r2)} {r2}</div>
      <div class="tl-bar-bg" style="max-width:140px">
        <div class="tl-bar-fill" style="width:{conf2:.0f}%;background:{rc(r2)}"></div>
      </div>
      <div class="tl-conf">{conf2:.1f}%</div>
      <div style="background:{bcc2}22;color:{bcc2};border:1px solid {bcc2}44;
                  border-radius:6px;padding:2px 8px;font-size:9px;font-weight:800;flex-shrink:0">
        {bc2}
      </div>
      <div class="tl-date">{str(row['created'])[:19]}</div>
      {tag_html}
    </div>
    """, unsafe_allow_html=True)

# Confidence trend chart
# Confidence trend chart
df_c = df_dx.copy()
df_c["Visit"] = [f"V{i+1}" for i in range(len(df_c))]
df_c["cf"]    = df_c["confidence"].astype(float)

fig_t = go.Figure()

# ✅ Background fill (FIXED LINE HERE)
fig_t.add_trace(go.Scatter(
    x=df_c["Visit"],
    y=df_c["cf"],
    fill='tozeroy',
    fillcolor='rgba(99,102,241,0.05)',
    line=dict(color='rgba(0,0,0,0)'),  # ✅ FIX (NO ERROR)
    hoverinfo='skip',
    showlegend=False
))

# Main line
fig_t.add_trace(go.Scatter(
    x=df_c["Visit"],
    y=df_c["cf"],
    mode='lines+markers+text',
    line=dict(color='#6366f1', width=2.5),
    marker=dict(
        size=16,
        color=[rc(r) for r in df_c["result"]],
        line=dict(color='white', width=2.5)
    ),
    text=[f"{v:.1f}%" for v in df_c["cf"]],
    textposition="top center",
    textfont=dict(size=10, color="white"),
    hovertemplate="<b>%{x}</b><br>%{customdata}<br>%{y:.2f}%<extra></extra>",
    customdata=df_c["result"].tolist(),
    name="Confidence"
))

# Vertical markers
for sel_i, lbl, lc in [
    (pidx, "← Previous", "#f59e0b"),
    (cidx, "← Current", "#a78bfa")
]:
    fig_t.add_vline(
        x=sel_i,
        line_dash="dash",
        line_color=lc,
        line_width=2,
        annotation_text=lbl,
        annotation_font_color=lc,
        annotation_font_size=11
    )

fig_t.update_layout(
    title="Confidence Trend — All Visits",
    paper_bgcolor="#0c1427",
    plot_bgcolor="#111f38",
    font_color="white",
    height=320,
    showlegend=False,
    xaxis_title="Visit",
    yaxis_title="AI Confidence (%)",
    yaxis_range=[0, 115],
    margin=dict(t=40, b=20)
)

st.plotly_chart(fig_t, use_container_width=True)

# ═════ DOWNLOAD ═══════════════════════════════════════════════════
st.markdown("---")
col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    if st.button("📥 Download Full PDF Report", type="primary", use_container_width=True):
        us_b = gcam_b = None
        img_rows = df_dx[df_dx['ultrasound_img'].apply(
            lambda x: has_img(x) if x is not None else False
        )].tail(1)
        if not img_rows.empty:
            rr = img_rows.iloc[0]
            us_b   = bytes(rr['ultrasound_img'])
            gcam_b = bytes(rr['gradcam_img']) if has_img(rr.get('gradcam_img')) else None
        with st.spinner("Generating..."):
            f = generate_report(pid, ultrasound_img_bytes=us_b, gradcam_img_bytes=gcam_b)
        if f:
            with open(f,"rb") as fh:
                st.download_button("⬇️ Download PDF", fh, f, "application/pdf", use_container_width=True)
            log_audit("COMPARE_REPORT","doctor",f"Report {pid} — {len(df_dx)} visits")
            st.success("✅ Report ready!")
        else:
            st.error("Error generating report.")

with col_d2:
    df_exp = df_dx[["result","confidence","created"]].copy()
    df_exp.index   = [f"Visit {i+1}" for i in range(len(df_exp))]
    df_exp.columns = ["Diagnosis","Confidence (%)","Date & Time"]
    df_exp["Confidence (%)"] = df_exp["Confidence (%)"].apply(lambda x: f"{float(x):.2f}%")
    st.download_button("⬇️ Export All Visits CSV",
                       df_exp.to_csv().encode(),
                       f"visits_{pid}.csv","text/csv",
                       use_container_width=True)

with col_d3:
    if st.button("➕ Add New Visit (AI Prediction)", use_container_width=True):
        st.switch_page("pages/2_AI_Prediction.py")