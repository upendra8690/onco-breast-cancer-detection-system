# pages/17_Doctor_Notes.py
import streamlit as st
import pandas as pd
from auth.guard import check_login
from database.database import connect, log_audit
from utils.language import get_text

check_login()

lang = st.session_state.get("app_language", "English")

st.title(f"📝 {get_text('doctor_notes', lang)}")
st.write("Add clinical notes, recommendations, and follow-up schedules for patients.")

tab1, tab2 = st.tabs(["Add Doctor Note", "View Patient Notes"])

with tab1:
    st.subheader("Add New Doctor Note")

    patient_id = st.text_input(get_text("patient_id", lang))
    doctor_name = st.text_input("Doctor Name")

    # Show recent diagnoses for this patient
    if patient_id:
        conn = connect()
        df_diag = pd.read_sql_query(
            "SELECT id, result, confidence, created FROM diagnosis WHERE patient_id=? ORDER BY created DESC",
            conn, params=(patient_id,)
        )
        conn.close()
        if not df_diag.empty:
            st.write("Recent Diagnoses:")
            st.dataframe(df_diag)
            diagnosis_id = st.selectbox("Link note to diagnosis (select ID):", df_diag["id"].tolist())
        else:
            st.info("No diagnoses found for this patient.")
            diagnosis_id = None
    else:
        diagnosis_id = None

    note = st.text_area("Clinical Note", placeholder="Enter your clinical observations, findings, and assessment...")

    recommendation = st.selectbox("Recommendation", [
        "Continue monitoring",
        "Schedule follow-up ultrasound in 3 months",
        "Schedule follow-up ultrasound in 6 months",
        "Refer to oncologist",
        "Biopsy recommended",
        "Chemotherapy discussion needed",
        "Annual mammogram",
        "Genetic counseling advised",
        "No further action needed",
        "Other"
    ])

    follow_up_date = st.date_input("Follow-up Date")

    if st.button("💾 Save Doctor Note"):
        if patient_id and doctor_name and note:
            conn = connect()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO doctor_notes(patient_id, diagnosis_id, doctor_name, note, recommendation, follow_up_date)
                VALUES(?,?,?,?,?,?)
            """, (patient_id, diagnosis_id, doctor_name, note, recommendation, str(follow_up_date)))
            conn.commit()
            conn.close()
            log_audit("DOCTOR_NOTE", doctor_name, f"Note added for patient {patient_id}")
            st.success("Doctor note saved successfully!")
        else:
            st.warning("Please fill in Patient ID, Doctor Name, and Note.")

with tab2:
    st.subheader("View Doctor Notes for a Patient")

    search_pid = st.text_input("Enter Patient ID to view notes:", key="view_notes_pid")

    if st.button("🔍 Load Notes"):
        conn = connect()
        df_notes = pd.read_sql_query("""
            SELECT dn.doctor_name, dn.note, dn.recommendation, dn.follow_up_date, dn.created,
                   d.result as diagnosis_result, d.confidence
            FROM doctor_notes dn
            LEFT JOIN diagnosis d ON dn.diagnosis_id = d.id
            WHERE dn.patient_id = ?
            ORDER BY dn.created DESC
        """, conn, params=(search_pid,))
        conn.close()

        if not df_notes.empty:
            for _, row in df_notes.iterrows():
                with st.expander(f"📋 {row['created']} — Dr. {row['doctor_name']}"):
                    if row['diagnosis_result']:
                        result_icon = "🔴" if row['diagnosis_result'] == "Malignant" else "🟢"
                        st.write(f"**Linked Diagnosis:** {result_icon} {row['diagnosis_result']} ({row['confidence']:.1f}%)")
                    st.write(f"**Clinical Note:** {row['note']}")
                    st.write(f"**Recommendation:** {row['recommendation']}")
                    st.write(f"**Follow-up Date:** {row['follow_up_date']}")
        else:
            st.warning("No notes found for this patient.")