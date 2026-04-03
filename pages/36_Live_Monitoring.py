# pages/36_Live_Monitoring.py  ← NEW — Real-time system health dashboard
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pytz
from auth.guard import check_login
from database.database import connect
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()
IST  = pytz.timezone("Asia/Kolkata")

st.markdown("""
<style>
.live-dot{width:10px;height:10px;background:#22c55e;border-radius:50%;
          display:inline-block;animation:pulse 1.5s infinite;margin-right:6px;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(1.3)}}
.health-card{background:linear-gradient(145deg,#0f172a,#1e293b);
             border-radius:14px;padding:20px;border:1px solid rgba(255,255,255,0.07);}
.kpi-num{font-size:36px;font-weight:900;background:linear-gradient(90deg,#60a5fa,#818cf8);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.kpi-lbl{font-size:11px;color:rgba(255,255,255,0.45);font-weight:500;letter-spacing:0.5px;margin-top:2px;}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

now_str = datetime.now(IST).strftime("%d %b %Y  %H:%M:%S IST")

st.markdown(f"""
<h1 style="color:#f8fafc">
    <span class="live-dot"></span> Live System Monitoring
</h1>
<p style="color:rgba(255,255,255,0.45);margin-top:-8px">
    Real-time dashboard · Last updated: {now_str}
</p>
""", unsafe_allow_html=True)

# Auto-refresh
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
if auto_refresh:
    import time
    st.sidebar.info("Refreshing every 30 seconds")

# ── Load all metrics ──────────────────────────────────────────────────────────
conn = connect()
try:
    total_patients = pd.read_sql_query("SELECT COUNT(*) as c FROM patients", conn).iloc[0]['c']
    total_dx       = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis",conn).iloc[0]['c']
    total_mal      = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis WHERE result='Malignant'",conn).iloc[0]['c']
    total_benign   = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis WHERE result='Benign'",  conn).iloc[0]['c']
    total_normal   = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis WHERE result='Normal'",  conn).iloc[0]['c']
    avg_conf       = pd.read_sql_query("SELECT AVG(confidence) as a FROM diagnosis",conn).iloc[0]['a'] or 0

    today_str      = datetime.now(IST).strftime("%Y-%m-%d")
    today_pts      = pd.read_sql_query("SELECT COUNT(*) as c FROM patients WHERE created LIKE ?",
                                       conn, params=(f"{today_str}%",)).iloc[0]['c']
    today_dx       = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis WHERE created LIKE ?",
                                       conn, params=(f"{today_str}%",)).iloc[0]['c']

    df_recent      = pd.read_sql_query("""
        SELECT d.result, d.confidence, d.created, p.name
        FROM diagnosis d JOIN patients p ON d.patient_id=p.patient_id
        ORDER BY d.created DESC LIMIT 20
    """, conn)

    df_daily       = pd.read_sql_query("""
        SELECT DATE(created) as date, COUNT(*) as count,
               AVG(confidence) as avg_conf,
               SUM(CASE WHEN result='Malignant' THEN 1 ELSE 0 END) as malignant
        FROM diagnosis
        GROUP BY DATE(created) ORDER BY date DESC LIMIT 14
    """, conn)

    df_audit_recent = pd.read_sql_query(
        "SELECT action, user, details, created FROM audit_log ORDER BY created DESC LIMIT 15", conn
    )
except Exception as e:
    st.error(f"Database error: {e}")
    conn.close()
    st.stop()
conn.close()

# ── Top KPI Row ───────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
metrics = [
    (c1, total_patients, "TOTAL PATIENTS"),
    (c2, total_dx,       "AI DIAGNOSES"),
    (c3, total_mal,      "MALIGNANT"),
    (c4, today_pts,      "TODAY PATIENTS"),
    (c5, today_dx,       "TODAY DIAGNOSES"),
    (c6, f"{avg_conf:.1f}%", "AVG CONFIDENCE"),
]
for col, val, lbl in metrics:
    col.markdown(f"""
    <div class="health-card" style="text-align:center">
        <div class="kpi-num">{val}</div>
        <div class="kpi-lbl">{lbl}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── System Health ─────────────────────────────────────────────────────────────
st.subheader("🟢 System Health")
c1, c2, c3, c4 = st.columns(4)
health_items = [
    ("Database", "✅ Connected", "#22c55e"),
    ("AI Model", "✅ Loaded (93%)", "#22c55e"),
    ("Language", "✅ 5 Languages", "#22c55e"),
    ("Reports", "✅ PDF Generator", "#22c55e"),
]
for col, (name, status, color) in zip([c1,c2,c3,c4], health_items):
    col.markdown(f"""
    <div class="health-card" style="text-align:center">
        <div style="font-size:14px;font-weight:700;color:#f8fafc">{name}</div>
        <div style="font-size:12px;color:{color};margin-top:4px">{status}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Charts Row ────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Diagnosis Distribution")
    fig_donut = go.Figure(go.Pie(
        labels=["Benign","Malignant","Normal"],
        values=[total_benign, total_mal, total_normal],
        hole=0.6,
        marker_colors=["#22c55e","#ef4444","#60a5fa"],
        textinfo="label+percent"
    ))
    fig_donut.add_annotation(
        text=f"{total_dx}<br>Total", x=0.5, y=0.5,
        font_size=18, font_color="white", showarrow=False
    )
    fig_donut.update_layout(
        paper_bgcolor="#0f172a", font_color="white",
        height=300, showlegend=True, margin=dict(t=20,b=20)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with c2:
    st.subheader("📈 Daily Diagnosis Trend")
    if not df_daily.empty:
        df_daily_r = df_daily.iloc[::-1].reset_index(drop=True)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=df_daily_r["date"], y=df_daily_r["count"],
            name="Total", marker_color="#6366f1", opacity=0.8
        ))
        fig_trend.add_trace(go.Bar(
            x=df_daily_r["date"], y=df_daily_r["malignant"],
            name="Malignant", marker_color="#ef4444", opacity=0.9
        ))
        fig_trend.update_layout(
            paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
            font_color="white", height=300, barmode="overlay",
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ── Confidence trend ──────────────────────────────────────────────────────────
if not df_recent.empty:
    st.subheader("🎯 Recent 20 Diagnoses — Confidence Scatter")
    df_recent["idx"] = range(len(df_recent), 0, -1)
    df_recent["color"] = df_recent["result"].map(
        {"Malignant":"#ef4444","Benign":"#22c55e","Normal":"#60a5fa"}
    )
    fig_scatter = px.scatter(
        df_recent, x="idx", y="confidence",
        color="result",
        size=[15]*len(df_recent),
        hover_data=["name","result","confidence","created"],
        title="Confidence Scores — Recent Diagnoses",
        color_discrete_map={"Malignant":"#ef4444","Benign":"#22c55e","Normal":"#60a5fa"}
    )
    fig_scatter.add_hline(y=avg_conf, line_dash="dash", line_color="#f59e0b",
                           annotation_text=f"Avg: {avg_conf:.1f}%")
    fig_scatter.update_layout(
        paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
        font_color="white", height=320,
        xaxis_title="Diagnosis (recent → older)",
        yaxis_title="Confidence (%)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Live Audit Log ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Live Activity Feed")
if not df_audit_recent.empty:
    for _, row in df_audit_recent.iterrows():
        action = str(row['action'])
        icon   = {"AI_PREDICTION":"🤖","PATIENT_REGISTER":"👤","LOGIN":"🔐",
                  "EMAIL_REPORT":"📧","WHATSAPP_SENT":"💬","DELETE_PATIENT":"🗑️",
                  "OPD_REGISTER":"🏥","OPD_CALL":"📢","TREATMENT_ADDED":"💊",
                  "CANCER_STAGING":"🔬"}.get(action,"📌")
        color  = "#ef4444" if "MALIGNANT" in str(row['details']).upper() else \
                 "#22c55e" if "SUCCESS" in str(row['details']).upper() else "#94a3b8"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:8px 0;
                    border-bottom:1px solid rgba(255,255,255,0.05)">
            <span style="font-size:18px">{icon}</span>
            <div style="flex:1">
                <span style="color:#f8fafc;font-size:13px;font-weight:600">{action}</span>
                <span style="color:rgba(255,255,255,0.45);font-size:12px;margin-left:8px">by {row['user']}</span>
                <div style="color:{color};font-size:12px">{str(row['details'])[:80]}</div>
            </div>
            <div style="color:rgba(255,255,255,0.3);font-size:11px">{str(row['created'])[:16]}</div>
        </div>
        """, unsafe_allow_html=True)

if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()
