# pages/00_Login.py  ← REPLACE
import streamlit as st
from utils.sidebar import render_sidebar
from utils.language import get_text
from database.database import connect, log_audit

lang = render_sidebar()

st.markdown("""
<style>
.login-wrap {
    max-width: 460px; margin: 30px auto 0 auto;
    background: linear-gradient(145deg,#0f172a,#1e293b);
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 20px; padding: 40px 36px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.5);
}
.login-title { font-size:26px; font-weight:800; color:#f8fafc; text-align:center; margin-bottom:6px; }
.login-sub   { font-size:13px; color:rgba(255,255,255,0.45); text-align:center; margin-bottom:24px; }
.tab-btn { cursor:pointer; padding:8px 20px; border-radius:8px; font-size:13px; font-weight:600; }
.stApp { background:#060b18; }
section[data-testid="stSidebar"] { background:#0a0f1e !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin-bottom:20px">
<span style="font-size:48px">🧬</span>
<div style="font-size:24px;font-weight:900;color:#f8fafc;margin-top:8px">Onco AI System</div>
<div style="font-size:13px;color:rgba(255,255,255,0.45)">CMR University Hospital — Breast Cancer Detection</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👨‍⚕️ Doctor / Admin Login", "🧑 Patient Login"])

# ── Doctor Login ──────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Doctor / Admin Login")
    username = st.text_input(get_text("username", lang), key="doc_user")
    password = st.text_input(get_text("password", lang), type="password", key="doc_pass")

    if st.button("🔐 Login as Doctor", type="primary", key="doc_btn", use_container_width=True):
        # Check custom users from DB first
        conn = connect()
        cur  = conn.cursor()
        cur.execute("SELECT username,password,role FROM users WHERE username=?", (username,))
        db_user = cur.fetchone()
        conn.close()

        if (username == "admin" and password == "admin") or \
           (db_user and db_user[1] == password):
            st.session_state.logged_in   = True
            st.session_state.user_type   = "doctor"
            st.session_state.username    = username
            role = db_user[2] if db_user else "Admin"
            st.session_state.user_role   = role
            log_audit("LOGIN", username, f"Doctor login: {role}")
            st.success(f"✅ Welcome Dr. {username}!")
            st.switch_page("pages/0_Dashboard.py")
        else:
            st.error("❌ Invalid credentials")

    st.markdown("---")
    st.caption("Default: admin / admin  |  Or create a user from User Management")

# ── Patient Login ──────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Patient Self-Service Login")
    st.info("Patients can login with their Patient ID to view their own reports.")

    pat_id   = st.text_input("Patient ID", key="pat_id",   placeholder="e.g. 1, 2, 3...")
    pat_name = st.text_input("Your Name",  key="pat_name", placeholder="Enter your registered name")

    if st.button("🔐 View My Reports", type="primary", key="pat_btn", use_container_width=True):
        conn = connect()
        cur  = conn.cursor()
        cur.execute("SELECT patient_id, name FROM patients WHERE patient_id=?", (pat_id,))
        pt = cur.fetchone()
        conn.close()
        if pt and pt[1].strip().lower() == pat_name.strip().lower():
            st.session_state.logged_in     = True
            st.session_state.user_type     = "patient"
            st.session_state.patient_id    = pat_id
            st.session_state.patient_name  = pt[1]
            st.session_state.username      = f"Patient:{pt[1]}"
            log_audit("PATIENT_LOGIN", pat_id, f"Patient self-login: {pt[1]}")
            st.success(f"✅ Welcome {pt[1]}!")
            st.switch_page("pages/29_Patient_Portal.py")
        else:
            st.error("❌ Patient ID or Name not found. Please check with reception.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.caption("📱 Or scan QR code from reception to login")
    with col2:
        if st.button("📷 Get QR Code", key="qr_nav"):
            st.switch_page("pages/26_QR_Login.py")
