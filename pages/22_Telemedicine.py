# pages/22_Telemedicine.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import random
import string
from auth.guard import check_login
from database.database import connect, log_audit

check_login()

st.title("📹 Telemedicine — Consultation Scheduler")
st.write("Schedule virtual consultations between patients and oncologists for remote second opinions.")

def generate_meeting_id():
    return "ONCO-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_meeting_link(meeting_id):
    return f"https://meet.jit.si/{meeting_id}"

tab1, tab2, tab3 = st.tabs(["📅 Schedule Consultation", "📋 View Appointments", "👨‍⚕️ Available Doctors"])

with tab1:
    st.subheader("Schedule New Teleconsultation")

    col1, col2 = st.columns(2)

    with col1:
        patient_id = st.text_input("Patient ID")
        patient_name = st.text_input("Patient Name")
        complaint = st.selectbox("Reason for Consultation", [
            "Review AI diagnosis result",
            "Second opinion on Malignant finding",
            "Risk assessment discussion",
            "Post-treatment follow-up",
            "Genetic counseling inquiry",
            "Biopsy report review",
            "Chemotherapy consultation",
            "Routine screening review",
            "Other"
        ])
        notes = st.text_area("Additional Notes (optional)")

    with col2:
        doctor = st.selectbox("Select Oncologist / Radiologist", [
            "Dr. Priya Sharma — Oncologist",
            "Dr. Rajesh Kumar — Radiologist",
            "Dr. Anita Patel — Surgical Oncologist",
            "Dr. Venkatesh Rao — Medical Oncologist",
            "Dr. Lakshmi Devi — Breast Specialist"
        ])

        # Available time slots (next 7 days, 9am-5pm)
        today = datetime.now()
        date_options = [(today + timedelta(days=i)).strftime("%Y-%m-%d")
                        for i in range(1, 8)]
        date_selected = st.selectbox("Select Date", date_options)

        time_slots = [
            "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
            "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM",
            "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"
        ]
        time_selected = st.selectbox("Select Time Slot", time_slots)
        platform = st.selectbox("Platform", ["Jitsi Meet (Free)", "Google Meet", "Zoom", "Microsoft Teams"])

    if st.button("📅 Schedule Consultation", type="primary"):
        if patient_id and patient_name:
            meeting_id = generate_meeting_id()
            meeting_link = generate_meeting_link(meeting_id)

            conn = connect()
            cur = conn.cursor()

            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS appointments(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT,
                    patient_name TEXT,
                    doctor TEXT,
                    date TEXT,
                    time TEXT,
                    complaint TEXT,
                    notes TEXT,
                    meeting_id TEXT,
                    meeting_link TEXT,
                    status TEXT DEFAULT 'Scheduled',
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cur.execute("""
                INSERT INTO appointments(patient_id, patient_name, doctor, date, time, complaint, notes, meeting_id, meeting_link)
                VALUES(?,?,?,?,?,?,?,?,?)
            """, (patient_id, patient_name, doctor, date_selected, time_selected,
                  complaint, notes, meeting_id, meeting_link))

            conn.commit()
            conn.close()
            log_audit("TELEMEDICINE_SCHEDULED", "staff",
                      f"Patient {patient_id} scheduled with {doctor} on {date_selected} {time_selected}")

            st.success("✅ Teleconsultation Scheduled Successfully!")
            st.info(f"**Meeting ID:** `{meeting_id}`")
            st.info(f"**Meeting Link:** {meeting_link}")

            # Meeting card
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0f172a,#1e293b);
                        border:1px solid rgba(99,102,241,0.4);
                        border-radius:16px;padding:24px;margin-top:16px">
                <h3 style="color:#818cf8">📹 Appointment Confirmation</h3>
                <p style="color:#94a3b8"><b style="color:#f8fafc">Patient:</b> {patient_name} ({patient_id})</p>
                <p style="color:#94a3b8"><b style="color:#f8fafc">Doctor:</b> {doctor}</p>
                <p style="color:#94a3b8"><b style="color:#f8fafc">Date & Time:</b> {date_selected} at {time_selected}</p>
                <p style="color:#94a3b8"><b style="color:#f8fafc">Reason:</b> {complaint}</p>
                <p style="color:#94a3b8"><b style="color:#f8fafc">Meeting Link:</b>
                    <a href="{meeting_link}" target="_blank" style="color:#60a5fa">{meeting_link}</a>
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please fill in Patient ID and Name.")

with tab2:
    st.subheader("All Scheduled Appointments")

    conn = connect()
    try:
        df_appt = pd.read_sql_query(
            "SELECT patient_id, patient_name, doctor, date, time, complaint, status, meeting_link FROM appointments ORDER BY date, time",
            conn
        )
    except:
        df_appt = pd.DataFrame()
    conn.close()

    if not df_appt.empty:
        # Status filter
        status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Completed", "Cancelled"])
        if status_filter != "All":
            df_appt = df_appt[df_appt["status"] == status_filter]

        st.dataframe(df_appt, use_container_width=True)

        # Stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Appointments", len(df_appt))
    else:
        st.info("No appointments scheduled yet.")

with tab3:
    st.subheader("🏥 Available Oncologists")

    doctors = [
        {
            "name": "Dr. Priya Sharma",
            "speciality": "Surgical Oncologist",
            "experience": "15 years",
            "qualification": "MS, MCh (Onco), FACS",
            "availability": "Mon–Fri 9AM–5PM",
            "languages": "English, Hindi, Telugu"
        },
        {
            "name": "Dr. Rajesh Kumar",
            "speciality": "Radiologist (Breast Imaging)",
            "experience": "12 years",
            "qualification": "MD Radiology, FRCR",
            "availability": "Mon–Sat 10AM–4PM",
            "languages": "English, Hindi"
        },
        {
            "name": "Dr. Anita Patel",
            "speciality": "Medical Oncologist",
            "experience": "18 years",
            "qualification": "MD, DM Oncology",
            "availability": "Tue–Sat 11AM–6PM",
            "languages": "English, Gujarati, Hindi"
        },
        {
            "name": "Dr. Venkatesh Rao",
            "speciality": "Breast Specialist",
            "experience": "10 years",
            "qualification": "MS Surgery, Fellowship Breast Oncology",
            "availability": "Mon–Thu 9AM–3PM",
            "languages": "English, Telugu, Kannada"
        },
    ]

    cols = st.columns(2)
    for i, doc in enumerate(doctors):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0f172a,#1e293b);
                        border:1px solid rgba(255,255,255,0.07);
                        border-radius:16px;padding:20px;margin-bottom:12px">
                <h4 style="color:#60a5fa;margin:0">👨‍⚕️ {doc['name']}</h4>
                <p style="color:#94a3b8;margin:4px 0;font-size:14px">
                    <b style="color:#f8fafc">{doc['speciality']}</b>
                </p>
                <p style="color:#64748b;font-size:13px;margin:2px 0">
                    🎓 {doc['qualification']} · {doc['experience']} experience
                </p>
                <p style="color:#64748b;font-size:13px;margin:2px 0">
                    📅 {doc['availability']}
                </p>
                <p style="color:#64748b;font-size:13px;margin:2px 0">
                    🌐 {doc['languages']}
                </p>
            </div>
            """, unsafe_allow_html=True)