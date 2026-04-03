# pages/23_Digital_Consent.py
import streamlit as st
import sqlite3
from datetime import datetime
from database.database import connect, log_audit
from utils.language import get_text

check_login_needed = False  # Public page for patients

st.title("📝 Digital Patient Consent Form")
st.write("Patients must provide informed consent before AI diagnosis is performed.")

# Consent text
CONSENT_TEXT = """
INFORMED CONSENT FOR AI-ASSISTED BREAST CANCER DIAGNOSIS

1. NATURE OF THE PROCEDURE:
   I understand that this AI system analyzes breast ultrasound images using Convolutional Neural Network (CNN) models trained on the BUSI dataset to classify findings as Benign, Malignant, or Normal.

2. PURPOSE:
   This AI tool serves as clinical decision support only. It does NOT replace professional medical judgment.

3. LIMITATIONS:
   The AI system has an accuracy of approximately 93% and may produce incorrect results. All findings MUST be reviewed by a qualified radiologist or oncologist.

4. DATA STORAGE:
   My ultrasound images, diagnosis results, and personal information will be stored securely in the hospital database. My data will not be shared without consent.

5. RIGHT TO WITHDRAW:
   I understand I can withdraw my data or request its deletion at any time.

6. VOLUNTARY PARTICIPATION:
   My participation is voluntary. Declining AI analysis will not affect my medical care.

7. RISKS AND BENEFITS:
   Benefits: Faster preliminary diagnosis, explainable AI heatmap, risk assessment.
   Risks: Potential for false positives or false negatives requiring clinical verification.

8. CONTACT:
   For questions about this AI system, contact the hospital's AI ethics committee.
"""

# Consent form
st.subheader("Patient Information")
col1, col2 = st.columns(2)
with col1:
    patient_id = st.text_input("Patient ID *")
    patient_name = st.text_input("Full Name *")
    date_of_birth = st.date_input("Date of Birth *")
with col2:
    guardian_name = st.text_input("Guardian Name (if minor)")
    phone = st.text_input("Phone Number *")
    relationship = st.selectbox("If signing for another:", [
        "Self", "Parent", "Legal Guardian", "Spouse", "Child (Adult)"
    ])

st.markdown("---")
st.subheader("Consent Agreement")
st.text_area("Please read the following consent:", CONSENT_TEXT, height=300, disabled=True)

st.markdown("---")

# Checkboxes
c1 = st.checkbox("✅ I have read and understood the above consent form")
c2 = st.checkbox("✅ I consent to AI analysis of my breast ultrasound images")
c3 = st.checkbox("✅ I consent to storage of my medical data in the hospital system")
c4 = st.checkbox("✅ I understand this is a decision support tool and does not replace my doctor")
c5 = st.checkbox("✅ I am 18 years or older, or I am the legal guardian of the patient")

signature = st.text_input("Digital Signature (Type your full name to sign) *")
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.info(f"🕐 Consent timestamp will be recorded as: **{timestamp}**")

if st.button("✍️ Submit Consent Form", type="primary"):
    if all([c1, c2, c3, c4, c5]) and patient_id and patient_name and signature:

        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS consent_forms(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                patient_name TEXT,
                phone TEXT,
                signature TEXT,
                relationship TEXT,
                timestamp TEXT,
                ip_recorded TEXT DEFAULT 'system'
            )
        """)
        cur.execute("""
            INSERT INTO consent_forms(patient_id, patient_name, phone, signature, relationship, timestamp)
            VALUES(?,?,?,?,?,?)
        """, (patient_id, patient_name, phone, signature, relationship, timestamp))
        conn.commit()
        conn.close()

        log_audit("CONSENT_SIGNED", patient_name, f"Patient {patient_id} signed consent at {timestamp}")

        st.success("✅ Consent recorded successfully!")
        st.balloons()

        st.markdown(f"""
        <div style="background:rgba(34,197,94,0.1);border:1px solid #22c55e;
                    border-radius:12px;padding:20px;margin-top:16px">
            <h4 style="color:#22c55e">Consent Confirmation</h4>
            <p>Patient: <b>{patient_name}</b> (ID: {patient_id})</p>
            <p>Signed by: <b>{signature}</b></p>
            <p>Timestamp: <b>{timestamp}</b></p>
            <p style="color:#86efac;font-size:13px">
                This consent is legally recorded and can be used for audit purposes.
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif not all([c1, c2, c3, c4, c5]):
        st.error("Please check all consent boxes before submitting.")
    else:
        st.error("Please fill in all required fields and provide digital signature.")

# View past consents (admin)
st.markdown("---")
with st.expander("🔐 Admin: View Consent Records"):
    conn = connect()
    try:
        import pandas as pd
        df_consent = pd.read_sql_query(
            "SELECT patient_id, patient_name, signature, relationship, timestamp FROM consent_forms ORDER BY timestamp DESC",
            conn
        )
        if not df_consent.empty:
            st.dataframe(df_consent, use_container_width=True)
        else:
            st.info("No consent forms yet.")
    except:
        st.info("No consent forms yet.")
    conn.close()