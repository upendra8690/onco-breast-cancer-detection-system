# pages/3_Patient_Search.py
import streamlit as st
from auth.guard import check_login
from database.database import connect
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"🔍 {get_text('patient_search', lang)}")

pid = st.text_input(get_text("patient_id", lang))

if st.button(get_text("search_btn", lang), type="primary"):
    conn = connect()
    cur  = conn.cursor()
    cur.execute(
        "SELECT patient_id,name,age,gender,phone,address FROM patients WHERE patient_id=?",
        (pid,)
    )
    data = cur.fetchone()
    conn.close()
    if data:
        st.success(get_text("patient_found", lang))
        st.write(f"**{get_text('patient_id',    lang)}:** {data[0]}")
        st.write(f"**{get_text('patient_name',  lang)}:** {data[1]}")
        st.write(f"**{get_text('age',           lang)}:** {data[2]}")
        st.write(f"**{get_text('gender',        lang)}:** {data[3]}")
        st.write(f"**{get_text('phone',         lang)}:** {data[4]}")
        st.write(f"**{get_text('address',       lang)}:** {data[5]}")
    else:
        st.warning(get_text("patient_not_found", lang))
