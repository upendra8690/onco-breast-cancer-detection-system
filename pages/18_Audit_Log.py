# pages/18_Audit_Log.py
import streamlit as st
import pandas as pd
from auth.guard import check_login
from database.database import connect
from utils.language import get_text

check_login()

lang = st.session_state.get("app_language", "English")

st.title(f"📋 {get_text('audit_log', lang)}")
st.write("System audit trail — all actions logged for transparency and accountability.")

conn = connect()

col1, col2 = st.columns(2)

# Filters
with col1:
    action_filter = st.selectbox("Filter by Action", [
        "All",
        "PATIENT_REGISTER",
        "AI_PREDICTION",
        "SYMPTOMS_LOG",
        "RISK_ASSESSMENT",
        "DOCTOR_NOTE",
        "DELETE_PATIENT",
        "LOGIN"
    ])

with col2:
    limit = st.selectbox("Show last N records", [25, 50, 100, 500])

if action_filter == "All":
    df = pd.read_sql_query(
        "SELECT action, user, details, created FROM audit_log ORDER BY created DESC LIMIT ?",
        conn, params=(limit,)
    )
else:
    df = pd.read_sql_query(
        "SELECT action, user, details, created FROM audit_log WHERE action=? ORDER BY created DESC LIMIT ?",
        conn, params=(action_filter, limit)
    )

conn.close()

if not df.empty:
    st.success(f"Showing {len(df)} audit records")
    st.dataframe(df, use_container_width=True)

    # Summary
    st.subheader("Action Summary")
    conn2 = connect()
    summary = pd.read_sql_query(
        "SELECT action, COUNT(*) as count FROM audit_log GROUP BY action ORDER BY count DESC",
        conn2
    )
    conn2.close()
    st.bar_chart(summary.set_index("action"))
else:
    st.info("No audit log entries found.")