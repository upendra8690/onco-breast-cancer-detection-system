# pages/28_SMS_WhatsApp.py
import streamlit as st
import urllib.parse
from auth.guard import check_login
from database.database import connect, log_audit
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()

st.markdown("""
<style>
.msg-card {
    background: linear-gradient(145deg, #0f172a, #1e293b);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 24px; margin-bottom: 16px;
}
.wa-btn {
    background: #25d366 !important; color: white !important;
    border-radius: 12px; padding: 12px 24px;
    font-weight: 700; font-size: 15px;
    display: inline-block; text-decoration: none;
    margin: 8px 0;
}
.sms-btn {
    background: #3b82f6 !important; color: white !important;
    border-radius: 12px; padding: 12px 24px;
    font-weight: 700; font-size: 15px;
    display: inline-block; text-decoration: none;
    margin: 8px 0;
}
.stApp { background: #060b18; }
section[data-testid="stSidebar"] { background: #0a0f1e !important; }
</style>
""", unsafe_allow_html=True)

st.title("📱 SMS & WhatsApp Alerts")
st.write("Send diagnosis results and alerts via WhatsApp and SMS to patients and doctors.")

tab1, tab2, tab3 = st.tabs(["💚 WhatsApp Message", "📱 SMS Alert", "📋 Bulk WhatsApp"])

# ── TAB 1: WhatsApp ───────────────────────────────────────────────────────────
with tab1:
    st.subheader("💚 Send WhatsApp Message")
    st.info("Uses WhatsApp Web — opens directly on your phone or browser. No API needed!")

    col1, col2 = st.columns(2)
    with col1:
        wa_phone  = st.text_input("Phone Number with Country Code",
                                  placeholder="919876543210 (91 = India code, no + or spaces)")
        wa_pid    = st.text_input("Patient ID (optional)", key="wa_pid")
        wa_name   = st.text_input("Patient Name (optional)", key="wa_name")
        wa_result = st.selectbox("Diagnosis Result", ["Benign","Malignant","Normal","General"], key="wa_result")

    with col2:
        if wa_result == "Malignant":
            default_msg = f"""🚨 URGENT — Onco AI Alert

Dear Patient/Doctor,

Patient ID   : {wa_pid if wa_pid else '[ID]'}
Patient Name : {wa_name if wa_name else '[Name]'}
AI Diagnosis : ⚠️ MALIGNANT
Action       : Please contact oncologist immediately.

This is from Onco AI System — CMR University.
For clinical use only."""
        elif wa_result == "Benign":
            default_msg = f"""✅ Onco AI Report

Patient ID   : {wa_pid if wa_pid else '[ID]'}
Patient Name : {wa_name if wa_name else '[Name]'}
AI Diagnosis : ✅ Benign
Status       : No malignant findings detected.

Please continue with regular screening.
Onco AI System — CMR University"""
        else:
            default_msg = f"""📋 Onco AI — Patient Update

Patient ID   : {wa_pid if wa_pid else '[ID]'}
Patient Name : {wa_name if wa_name else '[Name]'}

Your diagnosis report is ready. Please contact your doctor.

Onco AI System — CMR University
AI Powered Medical Diagnosis Platform"""

        wa_message = st.text_area("Message", value=default_msg, height=220)

    if st.button("💚 Open WhatsApp", type="primary"):
        if wa_phone:
            clean_phone = wa_phone.replace("+","").replace(" ","").replace("-","")
            encoded_msg = urllib.parse.quote(wa_message)
            wa_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
            st.markdown(f"""
            <a href="{wa_url}" target="_blank" class="wa-btn">
                💚 Click here to send on WhatsApp
            </a>
            """, unsafe_allow_html=True)
            st.success("✅ WhatsApp link ready! Click the green button above.")
            log_audit("WHATSAPP_SENT", "doctor", f"WhatsApp to {wa_phone} for patient {wa_pid}")
        else:
            st.warning("Please enter a phone number.")

    st.markdown("---")
    st.subheader("📲 WhatsApp from Database")
    st.write("Select a patient from your database and auto-fill their number.")

    import pandas as pd
    conn = connect()
    try:
        df_pts = pd.read_sql_query(
            "SELECT patient_id, name, phone FROM patients ORDER BY created DESC", conn
        )
    except:
        df_pts = pd.DataFrame()
    conn.close()

    if not df_pts.empty:
        selected = st.selectbox(
            "Select Patient",
            df_pts.apply(lambda r: f"{r['patient_id']} — {r['name']} ({r['phone']})", axis=1).tolist()
        )
        if st.button("Load Patient Info"):
            row = df_pts.iloc[df_pts.apply(
                lambda r: f"{r['patient_id']} — {r['name']} ({r['phone']})", axis=1
            ).tolist().index(selected)]
            phone_raw = str(row["phone"])
            if not phone_raw.startswith("91"):
                phone_raw = "91" + phone_raw
            st.info(f"Phone: **{phone_raw}** — copy this into the field above")
    else:
        st.info("No patients in database yet.")

# ── TAB 2: SMS ────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("📱 SMS Alert")
    st.markdown("""
    <div class="msg-card">
    <p style="color:#94a3b8">
    <b style="color:#f8fafc">Two ways to send SMS:</b><br><br>
    <b>Option A — Twilio (Paid, Professional)</b><br>
    Sign up at <a href="https://www.twilio.com" target="_blank" style="color:#60a5fa">twilio.com</a>
    → Get free trial ($15 credit) → Use the code below<br><br>
    <b>Option B — Fast2SMS (Free for India)</b><br>
    Sign up at <a href="https://www.fast2sms.com" target="_blank" style="color:#60a5fa">fast2sms.com</a>
    → Get free API key → Use the code below<br>
    </p>
    </div>
    """, unsafe_allow_html=True)

    sms_method = st.radio("Choose SMS Method", ["Fast2SMS (Free - India)", "Twilio (International)"])

    sms_phone  = st.text_input("Phone Number", placeholder="9876543210 (India, 10 digits)")
    sms_msg    = st.text_area("Message (max 160 chars)", max_chars=160,
                              value="Onco AI: Your diagnosis report is ready. Please contact your doctor. CMR University Hospital.")

    if sms_method == "Fast2SMS (Free - India)":
        fast2sms_key = st.text_input("Fast2SMS API Key", type="password",
                                     placeholder="Get from fast2sms.com dashboard")

        if st.button("📱 Send SMS via Fast2SMS", type="primary"):
            if not fast2sms_key:
                st.error("Please enter your Fast2SMS API key.")
            elif not sms_phone:
                st.error("Please enter phone number.")
            else:
                try:
                    import requests
                    resp = requests.get(
                        "https://www.fast2sms.com/dev/bulkV2",
                        params={
                            "authorization": fast2sms_key,
                            "message":       sms_msg,
                            "language":      "english",
                            "route":         "q",
                            "numbers":       sms_phone
                        },
                        timeout=10
                    )
                    result = resp.json()
                    if result.get("return") == True:
                        log_audit("SMS_SENT", "doctor", f"SMS sent to {sms_phone}")
                        st.success(f"✅ SMS sent successfully to {sms_phone}!")
                    else:
                        st.error(f"SMS failed: {result.get('message','Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    else:  # Twilio
        twilio_sid   = st.text_input("Twilio Account SID",   type="password")
        twilio_token = st.text_input("Twilio Auth Token",    type="password")
        twilio_from  = st.text_input("Twilio Phone Number",  placeholder="+1234567890")

        if st.button("📱 Send SMS via Twilio", type="primary"):
            if not all([twilio_sid, twilio_token, twilio_from, sms_phone]):
                st.error("Please fill in all Twilio fields.")
            else:
                try:
                    from twilio.rest import Client
                    client  = Client(twilio_sid, twilio_token)
                    message = client.messages.create(
                        body=sms_msg,
                        from_=twilio_from,
                        to=f"+91{sms_phone}" if not sms_phone.startswith("+") else sms_phone
                    )
                    log_audit("SMS_TWILIO", "doctor", f"SMS sent to {sms_phone}: {message.sid}")
                    st.success(f"✅ SMS sent! Message SID: {message.sid}")
                except ImportError:
                    st.error("Install Twilio: pip install twilio")
                except Exception as e:
                    st.error(f"Twilio error: {str(e)}")

# ── TAB 3: Bulk WhatsApp ──────────────────────────────────────────────────────
with tab3:
    st.subheader("📢 Bulk WhatsApp — All Patients with Diagnosis")
    st.write("Generate WhatsApp links for all patients who have diagnosis results.")

    import pandas as pd
    conn = connect()
    try:
        df_bulk = pd.read_sql_query("""
            SELECT p.patient_id, p.name, p.phone, d.result, d.confidence, d.created
            FROM patients p
            JOIN diagnosis d ON p.patient_id = d.patient_id
            ORDER BY d.created DESC
        """, conn)
    except:
        df_bulk = pd.DataFrame()
    conn.close()

    if not df_bulk.empty:
        st.dataframe(df_bulk, use_container_width=True)
        st.write(f"Total: **{len(df_bulk)}** patients with diagnosis results")

        for _, row in df_bulk.iterrows():
            phone = str(row["phone"]).replace(" ","").replace("-","")
            if not phone.startswith("91"):
                phone = "91" + phone

            if row["result"] == "Malignant":
                msg = f"🚨 URGENT — Onco AI: Patient {row['patient_id']} ({row['name']}) — MALIGNANT detected ({row['confidence']:.1f}%). Contact oncologist immediately. CMR University."
            else:
                msg = f"✅ Onco AI: Patient {row['patient_id']} ({row['name']}) — {row['result']} ({row['confidence']:.1f}%). Report ready. CMR University."

            encoded  = urllib.parse.quote(msg)
            wa_link  = f"https://wa.me/{phone}?text={encoded}"

            col1, col2, col3 = st.columns([2,2,1])
            col1.write(f"**{row['name']}** ({row['patient_id']})")
            col2.write(f"{'🔴' if row['result']=='Malignant' else '🟢'} {row['result']}")
            col3.markdown(f'<a href="{wa_link}" target="_blank" style="background:#25d366;color:white;padding:6px 14px;border-radius:8px;font-size:12px;text-decoration:none">WhatsApp</a>', unsafe_allow_html=True)
    else:
        st.info("No patient diagnosis data yet.")
