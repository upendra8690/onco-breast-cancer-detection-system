# pages/32_Treatment_Tracker.py  ← NEW FILE
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()
IST  = pytz.timezone("Asia/Kolkata")

st.markdown("""
<style>
.tx-card {
    background:linear-gradient(145deg,#0f172a,#1e293b);
    border-radius:14px; padding:20px; margin:8px 0;
    border-left:4px solid #6366f1;
}
.tx-active   { border-left-color:#22c55e !important; }
.tx-completed{ border-left-color:#818cf8 !important; }
.tx-scheduled{ border-left-color:#f59e0b !important; }
.med-pill {
    background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.3);
    border-radius:20px; padding:4px 12px; font-size:12px; color:#a5b4fc;
    display:inline-block; margin:2px;
}
.stApp { background:#060b18; }
section[data-testid="stSidebar"] { background:#0a0f1e !important; }
</style>
""", unsafe_allow_html=True)

st.title("💊 Treatment Tracker")
st.write("Track chemotherapy cycles, medications, and treatment plans — like real oncology hospitals.")

# ── DB tables ─────────────────────────────────────────────────────────────────
conn = connect()
cur  = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS treatment_plans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT, treatment_type TEXT, protocol TEXT,
        start_date TEXT, end_date TEXT, total_cycles INTEGER,
        completed_cycles INTEGER DEFAULT 0, status TEXT DEFAULT 'Active',
        doctor TEXT, notes TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS medications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT, medicine_name TEXT, dosage TEXT, frequency TEXT,
        start_date TEXT, end_date TEXT, notes TEXT, prescribed_by TEXT,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS followup_schedule(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT, patient_name TEXT, visit_type TEXT,
        scheduled_date TEXT, scheduled_time TEXT, doctor TEXT,
        notes TEXT, status TEXT DEFAULT 'Scheduled',
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )
""")
conn.commit()
conn.close()

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Treatment Plans", "💊 Medications", "📅 Follow-up Schedule", "📊 Progress"
])

# ── TAB 1: Treatment Plans ─────────────────────────────────────────────────────
with tab1:
    st.subheader("Add Treatment Plan")
    with st.form("tx_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            tx_pid    = st.text_input("Patient ID *")
            tx_type   = st.selectbox("Treatment Type", [
                "Chemotherapy","Radiation Therapy","Hormone Therapy",
                "Targeted Therapy","Immunotherapy","Surgery","Palliative Care",
                "Watch & Wait","Follow-up Monitoring"
            ])
        with c2:
            tx_proto  = st.text_input("Protocol / Regimen", placeholder="e.g. AC-T, FEC, CMF")
            tx_doctor = st.text_input("Oncologist")
        with c3:
            tx_start  = st.date_input("Start Date")
            tx_end    = st.date_input("End Date",
                                      value=datetime.now(IST).date() + timedelta(days=180))
            tx_cycles = st.number_input("Total Cycles", min_value=1, max_value=30, value=6)

        tx_notes = st.text_area("Treatment Notes / Side Effect Instructions")
        if st.form_submit_button("💾 Save Treatment Plan", type="primary", use_container_width=True):
            if tx_pid:
                conn = connect()
                cur  = conn.cursor()
                cur.execute("""
                    INSERT INTO treatment_plans(patient_id,treatment_type,protocol,
                    start_date,end_date,total_cycles,doctor,notes)
                    VALUES(?,?,?,?,?,?,?,?)
                """, (tx_pid, tx_type, tx_proto, str(tx_start), str(tx_end),
                      tx_cycles, tx_doctor, tx_notes))
                conn.commit()
                conn.close()
                log_audit("TREATMENT_ADDED", tx_doctor, f"Treatment {tx_type} for patient {tx_pid}")
                st.success("✅ Treatment plan saved!")
            else:
                st.warning("Please enter Patient ID.")

    st.markdown("---")
    st.subheader("Active Treatment Plans")
    pid_search = st.text_input("Search by Patient ID:")
    conn = connect()
    if pid_search:
        df_tx = pd.read_sql_query(
            "SELECT * FROM treatment_plans WHERE patient_id=? ORDER BY created DESC",
            conn, params=(pid_search,)
        )
    else:
        df_tx = pd.read_sql_query(
            "SELECT * FROM treatment_plans ORDER BY created DESC LIMIT 20", conn
        )
    conn.close()

    if not df_tx.empty:
        for _, row in df_tx.iterrows():
            pct = int((row['completed_cycles'] / row['total_cycles']) * 100) if row['total_cycles'] else 0
            css = f"tx-{row['status'].lower()}"
            st.markdown(f"""
            <div class="tx-card {css}">
                <div style="display:flex;justify-content:space-between">
                    <div>
                        <span style="color:#f8fafc;font-weight:700;font-size:15px">
                            Patient {row['patient_id']} — {row['treatment_type']}
                        </span>
                        <span style="background:rgba(99,102,241,0.2);color:#a5b4fc;
                                     border-radius:6px;padding:2px 8px;font-size:11px;margin-left:8px">
                            {row['protocol'] or 'Standard Protocol'}
                        </span>
                    </div>
                    <span style="color:rgba(255,255,255,0.4);font-size:12px">{row['status']}</span>
                </div>
                <div style="margin-top:10px">
                    <div style="background:rgba(255,255,255,0.08);border-radius:8px;height:8px">
                        <div style="background:linear-gradient(90deg,#6366f1,#818cf8);
                                    width:{pct}%;height:8px;border-radius:8px"></div>
                    </div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:4px">
                        Cycle {row['completed_cycles']}/{row['total_cycles']} · {pct}% complete
                        · Dr. {row['doctor'] or 'N/A'}
                        · {row['start_date']} → {row['end_date']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Update cycle count
        with st.expander("✏️ Update Cycle Completion"):
            upd_id   = st.number_input("Treatment Plan ID", min_value=1, key="upd_id")
            new_cyc  = st.number_input("Completed Cycles", min_value=0, key="new_cyc")
            upd_stat = st.selectbox("Status", ["Active","Completed","Paused","Cancelled"], key="upd_stat")
            if st.button("Update", key="upd_btn"):
                conn = connect()
                cur  = conn.cursor()
                cur.execute("UPDATE treatment_plans SET completed_cycles=?, status=? WHERE id=?",
                            (new_cyc, upd_stat, upd_id))
                conn.commit()
                conn.close()
                st.success("Updated!")
                st.rerun()
    else:
        st.info("No treatment plans found.")

# ── TAB 2: Medications ─────────────────────────────────────────────────────────
with tab2:
    st.subheader("Add Medication")
    with st.form("med_form"):
        c1, c2 = st.columns(2)
        with c1:
            m_pid    = st.text_input("Patient ID *", key="m_pid")
            m_name   = st.text_input("Medicine Name *", placeholder="e.g. Tamoxifen, Herceptin")
            m_dosage = st.text_input("Dosage", placeholder="e.g. 20mg, 500mg/m2")
        with c2:
            m_freq   = st.selectbox("Frequency", [
                "Once daily","Twice daily","Three times daily",
                "Weekly","Every 3 weeks","Monthly","As needed"
            ])
            m_start  = st.date_input("Start Date", key="m_start")
            m_end    = st.date_input("End Date", key="m_end",
                                     value=datetime.now(IST).date() + timedelta(days=90))
            m_doctor = st.text_input("Prescribed By")
        m_notes = st.text_area("Instructions / Side Effects to Watch")
        if st.form_submit_button("💊 Save Medication", type="primary", use_container_width=True):
            if m_pid and m_name:
                conn = connect()
                cur  = conn.cursor()
                cur.execute("""
                    INSERT INTO medications(patient_id,medicine_name,dosage,frequency,
                    start_date,end_date,notes,prescribed_by) VALUES(?,?,?,?,?,?,?,?)
                """, (m_pid, m_name, m_dosage, m_freq, str(m_start), str(m_end), m_notes, m_doctor))
                conn.commit()
                conn.close()
                st.success("✅ Medication saved!")
            else:
                st.warning("Patient ID and Medicine name required.")

    st.markdown("---")
    pid_med = st.text_input("View medications for Patient ID:", key="view_med_pid")
    if pid_med:
        conn = connect()
        df_med = pd.read_sql_query(
            "SELECT * FROM medications WHERE patient_id=? ORDER BY created DESC",
            conn, params=(pid_med,)
        )
        conn.close()
        if not df_med.empty:
            st.write(f"**{len(df_med)} medications for Patient {pid_med}:**")
            for _, m in df_med.iterrows():
                today = datetime.now(IST).date()
                try: end_d = datetime.strptime(str(m['end_date'])[:10], "%Y-%m-%d").date()
                except: end_d = today
                active = end_d >= today
                status_col = "#22c55e" if active else "#64748b"
                status_lbl = "Active" if active else "Completed"
                st.markdown(f"""
                <div class="tx-card" style="border-left-color:{status_col}">
                    <div style="display:flex;justify-content:space-between">
                        <span style="color:#f8fafc;font-weight:700">{m['medicine_name']}</span>
                        <span style="color:{status_col};font-size:12px">● {status_lbl}</span>
                    </div>
                    <div style="margin-top:6px">
                        <span class="med-pill">💊 {m['dosage'] or 'N/A'}</span>
                        <span class="med-pill">🕐 {m['frequency']}</span>
                        <span class="med-pill">📅 {str(m['start_date'])[:10]} → {str(m['end_date'])[:10]}</span>
                        <span class="med-pill">Dr. {m['prescribed_by'] or 'N/A'}</span>
                    </div>
                    {'<div style="margin-top:8px;font-size:12px;color:rgba(255,255,255,0.4)">' + str(m['notes']) + '</div>' if m['notes'] else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No medications found for this patient.")

# ── TAB 3: Follow-up Schedule ──────────────────────────────────────────────────
with tab3:
    st.subheader("Schedule Follow-up Appointment")
    with st.form("fu_form"):
        c1, c2 = st.columns(2)
        with c1:
            fu_pid    = st.text_input("Patient ID *", key="fu_pid")
            fu_name   = st.text_input("Patient Name *", key="fu_name")
            fu_type   = st.selectbox("Visit Type", [
                "Post-chemo review","Routine follow-up (3 months)",
                "Routine follow-up (6 months)","Annual mammogram",
                "AI Prediction review","Biopsy review",
                "Medication review","Oncologist consultation","Emergency"
            ])
        with c2:
            fu_date   = st.date_input("Scheduled Date",
                        value=datetime.now(IST).date() + timedelta(days=30))
            fu_time   = st.selectbox("Time Slot", [
                "09:00 AM","09:30 AM","10:00 AM","10:30 AM",
                "11:00 AM","11:30 AM","02:00 PM","02:30 PM",
                "03:00 PM","03:30 PM","04:00 PM","04:30 PM"
            ])
            fu_doctor = st.text_input("Doctor / Department")
        fu_notes = st.text_area("Notes for appointment")
        if st.form_submit_button("📅 Schedule Appointment", type="primary", use_container_width=True):
            if fu_pid and fu_name:
                conn = connect()
                cur  = conn.cursor()
                cur.execute("""
                    INSERT INTO followup_schedule(patient_id,patient_name,visit_type,
                    scheduled_date,scheduled_time,doctor,notes) VALUES(?,?,?,?,?,?,?)
                """, (fu_pid, fu_name, fu_type, str(fu_date), fu_time, fu_doctor, fu_notes))
                conn.commit()
                conn.close()
                log_audit("FOLLOWUP_SCHEDULED", fu_doctor, f"Follow-up for {fu_pid} on {fu_date}")
                st.success(f"✅ Follow-up scheduled for {fu_name} on {fu_date} at {fu_time}!")
            else:
                st.warning("Patient ID and Name required.")

    st.markdown("---")
    st.subheader("📅 Upcoming Appointments")
    conn = connect()
    today_str = datetime.now(IST).strftime("%Y-%m-%d")
    df_fu = pd.read_sql_query("""
        SELECT patient_id,patient_name,visit_type,scheduled_date,
               scheduled_time,doctor,status
        FROM followup_schedule
        WHERE scheduled_date >= ? ORDER BY scheduled_date, scheduled_time LIMIT 30
    """, conn, params=(today_str,))
    conn.close()
    if not df_fu.empty:
        st.dataframe(df_fu.rename(columns={
            "patient_id":"ID","patient_name":"Patient","visit_type":"Visit Type",
            "scheduled_date":"Date","scheduled_time":"Time","doctor":"Doctor","status":"Status"
        }), use_container_width=True)
    else:
        st.info("No upcoming appointments.")

# ── TAB 4: Progress ────────────────────────────────────────────────────────────
with tab4:
    st.subheader("📊 Treatment Statistics")
    conn = connect()
    try:
        df_stat = pd.read_sql_query(
            "SELECT treatment_type, COUNT(*) as count, status FROM treatment_plans GROUP BY treatment_type, status",
            conn
        )
        df_med_stat = pd.read_sql_query(
            "SELECT medicine_name, COUNT(*) as count FROM medications GROUP BY medicine_name ORDER BY count DESC LIMIT 10",
            conn
        )
    except:
        df_stat = pd.DataFrame()
        df_med_stat = pd.DataFrame()
    conn.close()

    if not df_stat.empty:
        import plotly.express as px
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(df_stat, x="treatment_type", y="count", color="status",
                         title="Treatment Plans by Type",
                         color_discrete_map={"Active":"#22c55e","Completed":"#6366f1","Paused":"#f59e0b"})
            fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                              font_color="white", height=300)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            if not df_med_stat.empty:
                fig2 = px.bar(df_med_stat, x="count", y="medicine_name", orientation="h",
                              title="Most Prescribed Medications",
                              color_discrete_sequence=["#818cf8"])
                fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                                   font_color="white", height=300)
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No treatment statistics yet.")
