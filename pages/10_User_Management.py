# pages/10_User_Management.py
import streamlit as st
import sqlite3
from auth.guard import check_login
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"👥 {get_text('user_management', lang)}")

conn   = sqlite3.connect("patients.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, password TEXT, role TEXT
    )
""")

username = st.text_input(get_text("username", lang))
password = st.text_input(get_text("password", lang), type="password")
role     = st.selectbox("Role", ["Doctor","Admin"])

if st.button("Create User", type="primary"):
    if username and password:
        cursor.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            (username, password, role)
        )
        conn.commit()
        st.success("User Created Successfully")
    else:
        st.warning("Please fill in all fields.")
conn.close()
