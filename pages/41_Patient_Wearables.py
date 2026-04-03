# pages/41_Patient_Wearables.py  ← REPLACE - Fixed ordering and patient selection
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
from datetime import datetime, timedelta
import pytz
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()
IST  = pytz.timezone("Asia/Kolkata")

st.markdown("""
<style>
.vital-card{background:linear-gradient(145deg,#0f172a,#1e293b);
            border-radius:12px;padding:16px;text-align:center;
            border:1px solid rgba(255,255,255,0.07);}
.vital-num{font-size:32px;font-weight:900;line-height:1;}
.vital-unit{font-size:12px;color:rgba(255,255,255,0.4);margin-top:2px;}
.vital-lbl{font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:1px;margin-top:4px;}
.vital-alert{animation:alertPulse 1s infinite;}
@keyframes alertPulse{0%,100%{opacity:1}50%{opacity:0.5}}
.device-card{background:linear-gradient(145deg,#0f172a,#1e293b);border-radius:14px;
             padding:20px;text-align:center;border:1px solid rgba(255,255,255,0.07);}
.device-conn{border-color:rgba(34,197,94,0.4)!important;}
.live-dot{width:8px;height:8px;background:#22c55e;border-radius:50%;
          animation:pulse 1.5s infinite;display:inline-block;margin-right:6px;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(1.3)}}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:10px 0 20px 0">
<div style="font-size:11px;color:#818cf8;letter-spacing:2px;text-transform:uppercase">2028 Feature</div>
<h1 style="color:#f8fafc;margin:4px 0">⌚ Patient Wearables & IoT Monitoring</h1>
<p style="color:rgba(255,255,255,0.45)">
Real-time vital signs from smartwatches, ECG patches, and hospital IoT devices
</p>
</div>
""", unsafe_allow_html=True)

# ── Patient Selection (with list from database) ───────────────────────────────
conn = connect()
try:
    df_pts = pd.read_sql_query(
        "SELECT patient_id, name FROM patients ORDER BY name", conn
    )
except:
    df_pts = pd.DataFrame()
conn.close()

col_pid, col_sel = st.columns([1,2])
with col_pid:
    patient_id = st.text_input("Patient ID:", placeholder="Enter patient ID")
with col_sel:
    if not df_pts.empty:
        opts = ["-- Select Patient --"] + df_pts.apply(
            lambda r: f"{r['patient_id']} — {r['name']}", axis=1).tolist()
        selected_pt = st.selectbox("Or select:", opts)
        if selected_pt != "-- Select Patient --" and not patient_id:
            patient_id = selected_pt.split(" — ")[0]

if not patient_id:
    st.info("👆 Enter a Patient ID or select from the dropdown to start monitoring.")
    st.stop()

# ── Live Status Header ────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);
            border-radius:12px;padding:12px 16px;margin-bottom:16px;
            display:flex;align-items:center;gap:12px">
<span class="live-dot"></span>
<span style="color:#4ade80;font-weight:700">LIVE MONITORING — Patient {patient_id}</span>
<span style="color:rgba(255,255,255,0.4);font-size:12px;margin-left:auto">
{datetime.now(IST).strftime('%d %b %Y, %H:%M:%S IST')}
</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["❤️ Live Vitals", "📈 24hr Trends", "⚙️ Devices"])

with tab1:
    if st.button("🔄 Refresh Readings"):
        st.rerun()

    # Simulated live vitals (in real system: from IoT API)
    hr    = random.randint(62, 98)
    spo2  = round(random.uniform(95.5, 99.9), 1)
    bp_s  = random.randint(110, 145)
    bp_d  = random.randint(70, 92)
    temp  = round(random.uniform(36.2, 37.8), 1)
    rr    = random.randint(14, 22)
    steps = random.randint(1200, 8500)
    stress= random.randint(20, 75)

    hr_alert   = hr > 100 or hr < 50
    spo2_alert = spo2 < 95
    bp_alert   = bp_s > 140 or bp_d > 90
    temp_alert = temp > 37.5

    if any([hr_alert, spo2_alert, bp_alert, temp_alert]):
        items = []
        if hr_alert: items.append(f"Heart Rate: {hr} bpm")
        if spo2_alert: items.append(f"SpO2: {spo2}%")
        if bp_alert: items.append(f"BP: {bp_s}/{bp_d}")
        if temp_alert: items.append(f"Temp: {temp}°C")
        st.error(f"⚠️ VITAL ALERT: {' | '.join(items)} — Review immediately!")

    # 6 vitals in 2 rows of 3
    row1 = st.columns(3)
    row2 = st.columns(3)

    vitals = [
        (row1[0], str(hr),          "bpm",    "❤️ Heart Rate",   "#ef4444" if hr_alert else "#22c55e",    hr_alert),
        (row1[1], f"{spo2}",        "%",      "🫁 SpO2",         "#ef4444" if spo2_alert else "#60a5fa",  spo2_alert),
        (row1[2], f"{bp_s}/{bp_d}", "mmHg",   "💉 Blood Pressure","#ef4444" if bp_alert else "#818cf8",   bp_alert),
        (row2[0], f"{temp}",        "°C",     "🌡️ Temperature",  "#ef4444" if temp_alert else "#f59e0b",  temp_alert),
        (row2[1], str(rr),          "br/min", "🫀 Resp. Rate",   "#60a5fa",                               False),
        (row2[2], f"{steps:,}",     "steps",  "🏃 Steps Today",  "#22c55e",                               False),
    ]

    for col, val, unit, label, color, is_alert in vitals:
        alert_cls = "vital-alert" if is_alert else ""
        col.markdown(f"""
        <div class="vital-card">
            <div class="vital-num {alert_cls}" style="color:{color}">{val}</div>
            <div class="vital-unit">{unit}</div>
            <div class="vital-lbl">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chemotherapy monitoring section
    st.subheader("💊 Chemotherapy Session Monitoring")
    c1, c2, c3 = st.columns(3)
    chemo_vals = [
        (c1, f"{random.randint(80,120)} mL/hr", "Infusion Rate",     "#6366f1"),
        (c2, f"{random.randint(30,80)}%",        "Infusion Progress", "#818cf8"),
        (c3, f"{random.randint(1,4)}h {random.randint(5,55)}m", "Time Remaining", "#a78bfa"),
    ]
    for col, val, label, color in chemo_vals:
        col.markdown(f"""
        <div class="vital-card" style="border-color:rgba(99,102,241,0.3)">
            <div class="vital-num" style="color:{color}">{val}</div>
            <div class="vital-lbl">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Side effects log
    st.subheader("📋 Side Effect Log")
    se_options = ["Nausea","Vomiting","Fatigue","Hair Loss","Mouth Sores",
                  "Numbness/Tingling","Fever","Bruising","Shortness of Breath","None"]
    se = st.multiselect("Report current side effects:", se_options)

    if st.button("💾 Save Vitals & Side Effects", type="primary"):
        conn = connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vitals_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT, heart_rate INTEGER, spo2 REAL,
                bp_systolic INTEGER, bp_diastolic INTEGER,
                temperature REAL, side_effects TEXT,
                created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
            )
        """)
        conn.execute("""
            INSERT INTO vitals_log(patient_id,heart_rate,spo2,bp_systolic,
                                   bp_diastolic,temperature,side_effects)
            VALUES(?,?,?,?,?,?,?)
        """, (patient_id, hr, spo2, bp_s, bp_d, temp, ", ".join(se) or "None"))
        conn.commit()
        conn.close()
        log_audit("VITALS_SAVED","doctor",f"Patient {patient_id} vitals logged")
        st.success("✅ Vitals and side effects saved!")

    # Previous vitals
    conn = connect()
    try:
        df_prev = pd.read_sql_query(
            "SELECT heart_rate,spo2,bp_systolic,bp_diastolic,temperature,side_effects,created "
            "FROM vitals_log WHERE patient_id=? ORDER BY created DESC LIMIT 5",
            conn, params=(patient_id,)
        )
        if not df_prev.empty:
            st.markdown("---")
            st.subheader("📋 Previous Vitals Records")
            st.dataframe(df_prev, use_container_width=True)
    except: pass
    conn.close()

with tab2:
    st.subheader("📈 24-Hour Vital Signs Trend")

    hours = list(range(24, 0, -1))
    times = [(datetime.now(IST) - timedelta(hours=h)).strftime("%H:%M") for h in hours]

    hr_trend   = [random.randint(60, 95) for _ in hours]
    spo2_trend = [round(random.uniform(96, 100), 1) for _ in hours]
    bp_trend   = [random.randint(110, 140) for _ in hours]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=hr_trend,   name="Heart Rate (bpm)",   line=dict(color="#ef4444", width=2)))
    fig.add_trace(go.Scatter(x=times, y=spo2_trend, name="SpO2 (%)",            line=dict(color="#60a5fa", width=2)))
    fig.add_trace(go.Scatter(x=times, y=bp_trend,   name="BP Systolic (mmHg)", line=dict(color="#818cf8", width=2)))

    fig.add_hrect(y0=60, y1=100, fillcolor="#22c55e", opacity=0.03, line_width=0)
    fig.add_hrect(y0=100, y1=130, fillcolor="#f59e0b", opacity=0.03, line_width=0)
    fig.update_layout(
        title="24-Hour Vital Signs Monitor",
        paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
        font_color="white", height=380,
        xaxis_title="Time", yaxis_title="Value",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig, use_container_width=True)

    stress_vals = [random.randint(15, 80) for _ in hours]
    fig2 = px.area(x=times, y=stress_vals, title="Stress Level (24h)",
                    color_discrete_sequence=["#f59e0b"])
    fig2.add_hrect(y0=70, y1=100, fillcolor="#ef4444", opacity=0.1)
    fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                        font_color="white", height=250,
                        xaxis_title="Time", yaxis_title="Stress Score")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("⚙️ Connected Devices")

    DEVICES = [
        {"name":"Apple Watch / Wear OS","icon":"⌚","type":"Smartwatch",
         "metrics":["Heart Rate","SpO2","Steps","ECG"],"status":"Connected"},
        {"name":"ECG Patch (Zio)","icon":"🩺","type":"Continuous ECG",
         "metrics":["12-lead ECG","Arrhythmia Alert"],"status":"Connected"},
        {"name":"Smart BP Monitor","icon":"💉","type":"Blood Pressure",
         "metrics":["Systolic BP","Diastolic BP","Pulse"],"status":"Connected"},
        {"name":"Smart Thermometer","icon":"🌡️","type":"Temperature",
         "metrics":["Body Temperature","Fever Alert"],"status":"Disconnected"},
        {"name":"Pulse Oximeter","icon":"🩸","type":"SpO2 Monitor",
         "metrics":["SpO2","Pulse Rate"],"status":"Connected"},
        {"name":"Activity Band","icon":"🏃","type":"Activity Tracker",
         "metrics":["Steps","Calories","Sleep","Stress"],"status":"Connected"},
    ]

    cols = st.columns(3)
    for i, d in enumerate(DEVICES):
        with cols[i % 3]:
            conn = d["status"] == "Connected"
            border = "rgba(34,197,94,0.4)" if conn else "rgba(239,68,68,0.2)"
            sc = "#22c55e" if conn else "#ef4444"
            met_html = "".join([
                f'<span style="background:rgba(255,255,255,0.05);border-radius:4px;'
                f'padding:2px 6px;font-size:10px;color:rgba(255,255,255,0.4);'
                f'margin:1px;display:inline-block">{m}</span>'
                for m in d["metrics"]
            ])
            st.markdown(f"""
            <div class="device-card {'device-conn' if conn else ''}"
                 style="border-color:{border}">
                <div style="font-size:30px">{d['icon']}</div>
                <div style="font-size:13px;font-weight:700;color:#f8fafc;margin-top:6px">{d['name']}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.4)">{d['type']}</div>
                <div style="color:{sc};font-size:12px;font-weight:600;margin:8px 0">● {d['status']}</div>
                <div style="margin-top:6px">{met_html}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    st.info("""
    **Compatible Devices:** Apple Watch Series 8+, Samsung Galaxy Watch,
    Omron BP Monitor, Masimo SpO2, iRhythm Zio Patch, Philips Patient Monitor
    """)
