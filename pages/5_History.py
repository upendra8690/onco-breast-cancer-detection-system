# pages/5_History.py
import streamlit as st
import pandas as pd
from auth.guard import check_login
from database.database import connect
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"📜 {get_text('patient_history', lang)}")

conn = connect()
df   = pd.read_sql_query("""
    SELECT p.patient_id, p.name, p.age, p.gender,
           d.result, d.confidence, d.created
    FROM patients p
    LEFT JOIN diagnosis d ON p.patient_id = d.patient_id
    ORDER BY d.created DESC
""", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.warning(get_text("no_history", lang))
