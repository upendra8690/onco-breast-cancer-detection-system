# pages/4_Today_List.py
import streamlit as st
import pandas as pd
from auth.guard import check_login
from database.database import connect
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"📋 {get_text('today_patients', lang)}")

conn = connect()
df   = pd.read_sql_query(
    "SELECT patient_id, name, age, gender, phone, address, created FROM patients ORDER BY created DESC",
    conn
)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No patients registered yet.")
