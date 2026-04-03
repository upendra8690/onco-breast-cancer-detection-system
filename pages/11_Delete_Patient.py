# pages/11_Delete_Patient.py
import streamlit as st
import sqlite3
from auth.guard import check_login
from database.database import log_audit
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"🗑️ {get_text('delete_patient', lang)}")

pid = st.text_input(get_text("patient_id", lang))

if st.button("Delete Patient", type="primary"):
    if pid:
        conn = sqlite3.connect("patients.db")
        cur  = conn.cursor()
        cur.execute("DELETE FROM patients  WHERE patient_id=?", (pid,))
        cur.execute("DELETE FROM diagnosis WHERE patient_id=?", (pid,))
        conn.commit()
        conn.close()
        log_audit("DELETE_PATIENT", "admin", f"Patient {pid} deleted")
        st.success("Patient Deleted Successfully")
    else:
        st.warning("Please enter a Patient ID.")
