# pages/29_Patient_Portal.py  ← NEW FILE
import streamlit as st
import pandas as pd
from database.database import connect, log_audit
from utils.report_generator import generate_report
from utils.sidebar import render_sidebar

lang = render_sidebar()

# Patient must be logged in as patient type
if not st.session_state.get("logged_in") or st.session_state.get("user_type") != "patient":
    st.warning("Please login as a patient first.")
    st.stop()

patient_id   = st.session_state.get("patient_id", "")
patient_name = st.session_state.get("patient_name", "Patient")

st.markdown("""
<style>
.patient-hero {
    background: linear-gradient(135deg, #0a0f1e, #1a2744);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px; padding: 32px; margin-bottom: 24px;
}
.visit-card {
    background: linear-gradient(145deg, #0f172a, #1e293b);
    border-radius: 16px; padding: 20px; margin-bottom: 12px;
    border-left: 4px solid #6366f1;
}
.visit-malignant { border-left-color: #ef4444 !important; }
.visit-benign    { border-left-color: #22c55e !important; }
.visit-normal    { border-left-color: #60a5fa !important; }
.stApp { background: #060b18; }
section[data-testid="stSidebar"] { background: #0a0f1e !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="patient-hero">
<h2 style="color:#f8fafc;margin:0">👋 Welcome, {patient_name}</h2>
<p style="color:rgba(255,255,255,0.5);margin:8px 0 0 0">
Patient ID: <b style="color:#818cf8">{patient_id}</b> &nbsp;·&nbsp;
CMR University Hospital &nbsp;·&nbsp; Onco AI System
</p>
</div>
""", unsafe_allow_html=True)

# Tabs for patient
tab1, tab2, tab3 = st.tabs(["📋 My Reports", "📊 My History", "📥 Download Report"])

with tab1:
    conn = connect()
    df_diag = pd.read_sql_query(
        "SELECT result, confidence, created FROM diagnosis WHERE patient_id=? ORDER BY created DESC",
        conn, params=(patient_id,)
    )
    df_pt = pd.read_sql_query(
        "SELECT name,age,gender,phone,address FROM patients WHERE patient_id=?",
        conn, params=(patient_id,)
    )
    conn.close()

    if not df_pt.empty:
        row = df_pt.iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Age", f"{row['age']} years")
        col2.metric("Gender", row['gender'])
        col3.metric("Total Visits", len(df_diag))

    st.subheader("📋 All My Diagnosis Visits")
    if not df_diag.empty:
        for i, row in df_diag.iterrows():
            visit_num  = len(df_diag) - i
            result     = row['result']
            card_class = f"visit-{result.lower()}"
            icon = "🔴" if result=="Malignant" else ("🟢" if result=="Benign" else "🔵")
            color= "#ef4444" if result=="Malignant" else ("#22c55e" if result=="Benign" else "#60a5fa")

            st.markdown(f"""
            <div class="visit-card {card_class}">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span style="font-size:13px;color:rgba(255,255,255,0.5)">Visit {visit_num}</span>
                        <div style="font-size:18px;font-weight:800;color:{color}">{icon} {result}</div>
                        <div style="font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px">
                            {row['created'][:19]}
                        </div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:28px;font-weight:900;color:{color}">{row['confidence']:.1f}%</div>
                        <div style="font-size:11px;color:rgba(255,255,255,0.4)">AI Confidence</div>
                    </div>
                </div>
                {'<div style="background:rgba(239,68,68,0.15);border-radius:8px;padding:8px;margin-top:10px;font-size:12px;color:#fca5a5">⚠️ <b>Action Required:</b> Please consult your doctor for this result.</div>' if result=="Malignant" else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No diagnosis records found yet.")

with tab2:
    conn = connect()
    df_h = pd.read_sql_query(
        "SELECT result, confidence, created FROM diagnosis WHERE patient_id=? ORDER BY created",
        conn, params=(patient_id,)
    )
    conn.close()

    if len(df_h) > 1:
        import plotly.express as px
        df_h["Visit"] = [f"V{i+1}" for i in range(len(df_h))]
        fig = px.line(df_h, x="Visit", y="confidence",
                      title="My Confidence Score Over Visits",
                      markers=True,
                      color_discrete_sequence=["#6366f1"])
        fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                          font_color="white", height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_h[["Visit","result","confidence","created"]], use_container_width=True)
    elif len(df_h) == 1:
        st.info("You have 1 visit. Multiple visits will show a trend chart.")
        st.dataframe(df_h, use_container_width=True)
    else:
        st.info("No history yet.")

with tab3:
    st.subheader("📥 Download Your Complete Report")
    st.info("This report includes all your visits, diagnosis history, and risk assessment.")

    if st.button("📄 Generate & Download My Report", type="primary", use_container_width=True):
        with st.spinner("Generating your report..."):
            file = generate_report(patient_id)
        if file:
            with open(file, "rb") as f:
                st.download_button(
                    "⬇️ Download Report PDF",
                    data=f,
                    file_name=file,
                    mime="application/pdf",
                    use_container_width=True
                )
            log_audit("PATIENT_REPORT_DOWNLOAD", patient_id, f"{patient_name} downloaded report")
            st.success("✅ Report ready!")
        else:
            st.error("Could not generate report.")

# Logout button
st.markdown("---")
col1, col2 = st.columns([3,1])
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        # Show rating before logout
        st.session_state["show_rating"] = True
        st.rerun()

if st.session_state.get("show_rating"):
    st.markdown("---")
    st.subheader("⭐ Rate Your Experience")
    rating = st.select_slider(
        "How was your experience with Onco AI System?",
        options=["1 ⭐", "2 ⭐⭐", "3 ⭐⭐⭐", "4 ⭐⭐⭐⭐", "5 ⭐⭐⭐⭐⭐"],
        value="5 ⭐⭐⭐⭐⭐"
    )
    feedback = st.text_area("Any comments or suggestions? (optional)")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit & Logout", type="primary", use_container_width=True):
            conn = connect()
            cur  = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ratings(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_type TEXT, user_id TEXT,
                    rating TEXT, feedback TEXT,
                    created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
                )
            """)
            cur.execute("INSERT INTO ratings(user_type,user_id,rating,feedback) VALUES(?,?,?,?)",
                        ("patient", patient_id, rating, feedback))
            conn.commit(); conn.close()
            log_audit("RATING", patient_id, f"Rating: {rating}")
            for key in ["logged_in","user_type","patient_id","patient_name","username","show_rating"]:
                st.session_state.pop(key, None)
            st.success("✅ Thank you for your feedback! Logging out...")
            st.switch_page("pages/00_Login.py")
    with col2:
        if st.button("Skip & Logout", use_container_width=True):
            for key in ["logged_in","user_type","patient_id","patient_name","username","show_rating"]:
                st.session_state.pop(key, None)
            st.switch_page("pages/00_Login.py")
