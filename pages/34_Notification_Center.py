# pages/34_Notification_Center.py  ← NEW FILE
import streamlit as st
import pandas as pd
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
.notif-card {
    background:linear-gradient(145deg,#0f172a,#1e293b);
    border-radius:14px; padding:16px 20px; margin:6px 0;
    border-left:4px solid #6366f1; display:flex;
    align-items:flex-start; gap:14px;
}
.notif-urgent  { border-left-color:#ef4444 !important; background:linear-gradient(145deg,#1a0a0a,#200e0e) !important; }
.notif-warning { border-left-color:#f59e0b !important; }
.notif-success { border-left-color:#22c55e !important; }
.notif-info    { border-left-color:#60a5fa !important; }
.notif-icon    { font-size:24px; flex-shrink:0; margin-top:2px; }
.notif-title   { font-size:14px; font-weight:700; color:#f8fafc; }
.notif-body    { font-size:12px; color:rgba(255,255,255,0.5); margin-top:4px; }
.notif-time    { font-size:11px; color:rgba(255,255,255,0.3); margin-top:6px; }
.badge-count {
    background:#ef4444; color:white; border-radius:50%;
    width:20px; height:20px; display:inline-flex;
    align-items:center; justify-content:center;
    font-size:11px; font-weight:700; margin-left:6px;
}
.stApp { background:#060b18; }
section[data-testid="stSidebar"] { background:#0a0f1e !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔔 Notification Center")

# ── Generate smart notifications from database ─────────────────────────────────
conn = connect()
notifications = []

# 1. Malignant cases in last 7 days
try:
    df_mal = pd.read_sql_query("""
        SELECT d.patient_id, p.name, d.confidence, d.created
        FROM diagnosis d JOIN patients p ON d.patient_id=p.patient_id
        WHERE d.result='Malignant'
        ORDER BY d.created DESC LIMIT 10
    """, conn)
    for _, row in df_mal.iterrows():
        notifications.append({
            "type": "urgent",
            "icon": "🚨",
            "title": f"MALIGNANT Detected — Patient {row['patient_id']} ({row['name']})",
            "body":  f"AI confidence: {row['confidence']:.1f}% · Immediate oncologist referral required.",
            "time":  str(row['created'])[:16],
            "action":"Review"
        })
except: pass

# 2. Follow-up overdue
try:
    today = datetime.now(IST).strftime("%Y-%m-%d")
    df_fu_overdue = pd.read_sql_query("""
        SELECT patient_id, patient_name, visit_type, scheduled_date
        FROM followup_schedule
        WHERE status='Scheduled' AND scheduled_date < ?
        ORDER BY scheduled_date
    """, conn, params=(today,))
    for _, row in df_fu_overdue.iterrows():
        notifications.append({
            "type": "warning",
            "icon": "⏰",
            "title": f"Missed Follow-up — {row['patient_name']} ({row['patient_id']})",
            "body":  f"Scheduled: {row['scheduled_date']} · Type: {row['visit_type']}",
            "time":  row['scheduled_date'],
            "action":"Reschedule"
        })
except: pass

# 3. Today's follow-ups
try:
    df_fu_today = pd.read_sql_query("""
        SELECT patient_id, patient_name, visit_type, scheduled_time, doctor
        FROM followup_schedule
        WHERE status='Scheduled' AND scheduled_date = ?
        ORDER BY scheduled_time
    """, conn, params=(today,))
    for _, row in df_fu_today.iterrows():
        notifications.append({
            "type": "info",
            "icon": "📅",
            "title": f"Today's Appointment — {row['patient_name']}",
            "body":  f"{row['visit_type']} at {row['scheduled_time']} · Dr. {row['doctor'] or 'TBD'}",
            "time":  "Today",
            "action":"View"
        })
except: pass

# 4. New patients (last 24h)
try:
    df_new = pd.read_sql_query("""
        SELECT patient_id, name, created FROM patients
        WHERE created >= datetime('now', '-1 day', '+5 hours 30 minutes')
        ORDER BY created DESC
    """, conn)
    for _, row in df_new.iterrows():
        notifications.append({
            "type": "success",
            "icon": "👤",
            "title": f"New Patient Registered — {row['name']} (ID: {row['patient_id']})",
            "body":  "Patient has been registered and is ready for AI Prediction.",
            "time":  str(row['created'])[:16],
            "action":"View"
        })
except: pass

# 5. Active OPD queue
try:
    df_opd = pd.read_sql_query("""
        SELECT COUNT(*) as cnt FROM opd_queue
        WHERE status='Waiting' AND registered_at LIKE ?
    """, conn, params=(f"{today}%",))
    waiting = df_opd.iloc[0]['cnt'] if not df_opd.empty else 0
    if waiting > 0:
        notifications.append({
            "type": "info",
            "icon": "🏥",
            "title": f"{waiting} Patients Waiting in OPD Queue",
            "body":  f"Today's date: {today} · Please call next patient from OPD Queue page.",
            "time":  "Now",
            "action":"OPD"
        })
except: pass

# 6. System stats
try:
    df_stats = pd.read_sql_query("SELECT COUNT(*) as cnt FROM diagnosis", conn)
    total_dx = df_stats.iloc[0]['cnt'] if not df_stats.empty else 0
    notifications.append({
        "type": "success",
        "icon": "🤖",
        "title": f"System Running — {total_dx} Total AI Diagnoses Completed",
        "body":  "Onco AI System is operational. Model accuracy: 93%.",
        "time":  datetime.now(IST).strftime("%Y-%m-%d %H:%M"),
        "action":"Dashboard"
    })
except: pass

conn.close()

# ── Summary counts ─────────────────────────────────────────────────────────────
urgent_c  = sum(1 for n in notifications if n["type"]=="urgent")
warning_c = sum(1 for n in notifications if n["type"]=="warning")
info_c    = sum(1 for n in notifications if n["type"]=="info")

c1,c2,c3,c4 = st.columns(4)
c1.metric("🔔 Total", len(notifications))
c2.metric("🚨 Urgent", urgent_c)
c3.metric("⚠️ Warnings", warning_c)
c4.metric("ℹ️ Info", info_c)

# ── Filter ────────────────────────────────────────────────────────────────────
st.markdown("---")
filter_type = st.selectbox("Filter by type:",
    ["All","🚨 Urgent Only","⚠️ Warnings","✅ Success","ℹ️ Info"])

filtered = notifications
if filter_type == "🚨 Urgent Only":  filtered = [n for n in notifications if n["type"]=="urgent"]
elif filter_type == "⚠️ Warnings":   filtered = [n for n in notifications if n["type"]=="warning"]
elif filter_type == "✅ Success":     filtered = [n for n in notifications if n["type"]=="success"]
elif filter_type == "ℹ️ Info":       filtered = [n for n in notifications if n["type"]=="info"]

st.subheader(f"{'🚨 ' if urgent_c else ''}Notifications ({len(filtered)})")

if filtered:
    for notif in filtered:
        st.markdown(f"""
        <div class="notif-card notif-{notif['type']}">
            <div class="notif-icon">{notif['icon']}</div>
            <div style="flex:1">
                <div class="notif-title">{notif['title']}</div>
                <div class="notif-body">{notif['body']}</div>
                <div class="notif-time">🕐 {notif['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✅ No notifications — all clear!")

# ── Quick Links ────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("⚡ Quick Actions from Notifications")
c1,c2,c3,c4 = st.columns(4)
if c1.button("🏥 Open OPD Queue",   use_container_width=True):
    st.switch_page("pages/31_OPD_Queue.py")
if c2.button("📊 Dashboard",        use_container_width=True):
    st.switch_page("pages/0_Dashboard.py")
if c3.button("🤖 Run AI Prediction",use_container_width=True):
    st.switch_page("pages/2_AI_Prediction.py")
if c4.button("📅 Treatment Tracker",use_container_width=True):
    st.switch_page("pages/32_Treatment_Tracker.py")
