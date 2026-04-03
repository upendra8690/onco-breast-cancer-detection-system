# pages/0_Dashboard.py  ← REPLACE
import streamlit as st
import pandas as pd
import plotly.express as px
from auth.guard import check_login
from database.database import connect
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

# ── Logout button at top right ────────────────────────────────────────────────
col_title, col_logout = st.columns([5, 1])
with col_title:
    st.title(f"🏥 {get_text('dashboard', lang)}")
with col_logout:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", key="dash_logout"):
        st.session_state["show_rating_doctor"] = True
        st.rerun()

if st.session_state.get("show_rating_doctor"):
    st.markdown("---")
    st.subheader("⭐ Rate Onco AI System Before Logout")
    rating = st.select_slider(
        "Your rating:",
        options=["1 ⭐ Poor", "2 ⭐⭐ Fair", "3 ⭐⭐⭐ Good", "4 ⭐⭐⭐⭐ Very Good", "5 ⭐⭐⭐⭐⭐ Excellent"],
        value="5 ⭐⭐⭐⭐⭐ Excellent"
    )
    feedback = st.text_area("Suggestions? (optional)", key="doc_fb")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit & Logout", type="primary", use_container_width=True):
            conn = connect()
            cur  = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS ratings(id INTEGER PRIMARY KEY AUTOINCREMENT,user_type TEXT,user_id TEXT,rating TEXT,feedback TEXT,created TEXT DEFAULT (datetime('now','+5 hours 30 minutes')))")
            cur.execute("INSERT INTO ratings(user_type,user_id,rating,feedback) VALUES(?,?,?,?)",
                        ("doctor", st.session_state.get("username","admin"), rating, feedback))
            conn.commit(); conn.close()
            for k in ["logged_in","user_type","username","user_role","show_rating_doctor"]:
                st.session_state.pop(k, None)
            st.success("Thank you! Logging out...")
            st.switch_page("pages/00_Login.py")
    with col2:
        if st.button("Skip & Logout", use_container_width=True):
            for k in ["logged_in","user_type","username","user_role","show_rating_doctor"]:
                st.session_state.pop(k, None)
            st.switch_page("pages/00_Login.py")
    st.stop()

st.write(get_text("app_subtitle", lang))

conn = connect()
cur  = conn.cursor()
cur.execute("SELECT COUNT(*) FROM patients");   patients  = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM diagnosis");  diagnosis = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM diagnosis WHERE result='Malignant'"); malignant = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM diagnosis WHERE result='Benign'");    benign    = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM diagnosis WHERE result='Normal'");    normal    = cur.fetchone()[0]
cur.execute("SELECT AVG(confidence) FROM diagnosis");                   avg_conf  = cur.fetchone()[0]
conn.close()

col1, col2, col3, col4 = st.columns(4)
col1.metric(get_text("total_patients",  lang), patients)
col2.metric(get_text("total_diagnoses", lang), diagnosis)
col3.metric("Malignant Cases", malignant)
col4.metric("Avg Confidence", f"{avg_conf:.1f}%" if avg_conf else "N/A")
st.success(get_text("system_running", lang))

if diagnosis > 0:
    st.subheader("📊 Diagnosis Distribution")
    c1, c2 = st.columns(2)
    with c1:
        pie = pd.DataFrame({
            "Diagnosis": [get_text("benign",lang), get_text("malignant",lang), get_text("normal",lang)],
            "Count": [benign, malignant, normal]
        })
        fig = px.pie(pie, names="Diagnosis", values="Count",
                     color_discrete_sequence=["#2ecc71","#e74c3c","#3498db"])
        fig.update_layout(paper_bgcolor="#0f172a", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        bar = pd.DataFrame({
            "Type":  [get_text("benign",lang), get_text("malignant",lang), get_text("normal",lang)],
            "Count": [benign, malignant, normal]
        })
        fig2 = px.bar(bar, x="Type", y="Count", color="Type",
                      color_discrete_sequence=["#2ecc71","#e74c3c","#3498db"])
        fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b", font_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🕐 Recent Diagnoses")
    conn = connect()
    df = pd.read_sql_query("""
        SELECT p.patient_id, p.name, p.age, d.result, d.confidence, d.created
        FROM diagnosis d JOIN patients p ON d.patient_id=p.patient_id
        ORDER BY d.created DESC LIMIT 10
    """, conn)
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
else:
    st.info("No diagnoses yet. Register patients and run AI predictions.")

# Ratings summary
st.markdown("---")
st.subheader("⭐ System Ratings")
conn = connect()
try:
    df_r = pd.read_sql_query("SELECT user_type, rating, created FROM ratings ORDER BY created DESC LIMIT 10", conn)
    if not df_r.empty:
        st.dataframe(df_r, use_container_width=True)
        avg_text = df_r["rating"].str.extract(r"(\d)").astype(float).mean().values[0]
        st.metric("Average Rating", f"{avg_text:.1f} / 5 ⭐")
    else:
        st.info("No ratings yet.")
except:
    st.info("Ratings table will appear after first logout.")
conn.close()
