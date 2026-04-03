# pages/12_Patient_Timeline.py
import streamlit as st
import pandas as pd
import sqlite3
from auth.guard import check_login
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"📅 {get_text('patient_timeline', lang)}")
st.write("View diagnosis history of a patient over time.")

pid = st.text_input(get_text("patient_id", lang))

if st.button("Load Timeline", type="primary"):
    conn = sqlite3.connect("patients.db")
    df   = pd.read_sql_query(
        "SELECT created, result, confidence FROM diagnosis WHERE patient_id=? ORDER BY created",
        conn, params=(pid,)
    )
    conn.close()
    if len(df) > 0:
        st.success("Records Found")
        st.subheader("Confidence Trend")
        st.line_chart(df.set_index("created")["confidence"])
        st.subheader("Diagnosis Records")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No records found for this patient.")
