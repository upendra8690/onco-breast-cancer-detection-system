# pages/31_OPD_Queue.py  ← REPLACE (fixed blank screen issue)
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import pytz
from auth.guard import check_login
from database.database import connect, get_ist_time
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()
IST  = pytz.timezone("Asia/Kolkata")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
.token-waiting{background:linear-gradient(145deg,#0f172a,#1e293b);
               border:2px solid rgba(99,102,241,0.4);border-radius:14px;
               padding:16px;margin:6px 0;display:flex;align-items:center;gap:14px;}
.token-urgent {border-color:rgba(239,68,68,0.6) !important;
               background:linear-gradient(145deg,#1a0a0a,#200d0d) !important;}
.now-serving  {background:linear-gradient(135deg,#14532d,#15803d);
               border-radius:20px;padding:28px;text-align:center;margin-bottom:16px;}
.now-num      {font-size:72px;font-weight:900;color:white;line-height:1;}
.now-name     {font-size:20px;color:rgba(255,255,255,0.8);margin-top:6px;}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.title(f"🏥 {get_text('opd_queue', lang)}")
st.write("Government-style patient token management — real-time queue with urgent priority.")

# ── Create OPD table ──────────────────────────────────────────────────────────
conn = connect()
cur  = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS opd_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_no INTEGER,
        patient_id TEXT,
        patient_name TEXT,
        age INTEGER,
        gender TEXT,
        complaint TEXT,
        priority TEXT DEFAULT 'Normal',
        status TEXT DEFAULT 'Waiting',
        counter TEXT DEFAULT 'Counter 1',
        registered_at TEXT,
        called_at TEXT,
        done_at TEXT
    )
""")
conn.commit()
conn.close()

# ── Load today's data ─────────────────────────────────────────────────────────
today = datetime.now(IST).strftime("%Y-%m-%d")

@st.cache_data(ttl=5)
def load_queue(today_date):
    c = connect()
    df = pd.read_sql_query(
        "SELECT * FROM opd_queue WHERE registered_at LIKE ? ORDER BY token_no",
        c, params=(f"{today_date}%",)
    )
    c.close()
    return df

df_queue = load_queue(today)

# ── Stats ─────────────────────────────────────────────────────────────────────
total   = len(df_queue)
waiting = len(df_queue[df_queue["status"]=="Waiting"])  if total else 0
serving = len(df_queue[df_queue["status"]=="Serving"])  if total else 0
done    = len(df_queue[df_queue["status"]=="Done"])     if total else 0
urgent  = len(df_queue[df_queue["priority"]=="Urgent"]) if total else 0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("📋 Total Today",  total)
c2.metric("⏳ Waiting",      waiting)
c3.metric("🟢 Serving",      serving)
c4.metric("✅ Done",          done)
c5.metric("🔴 Urgent",       urgent)

tab1, tab2, tab3 = st.tabs([
    f"📺 Live Queue Board",
    f"➕ Register Patient",
    f"📊 Today's Analytics"
])

# ── TAB 1: Live Queue ─────────────────────────────────────────────────────────
with tab1:
    # Reload button
    if st.button("🔄 Refresh Queue", use_container_width=False):
        st.cache_data.clear()
        st.rerun()

    # Now Serving
    df_serving = df_queue[df_queue["status"]=="Serving"] if total else pd.DataFrame()
    if not df_serving.empty:
        sr = df_serving.iloc[0]
        st.markdown(f"""
        <div class="now-serving">
            <div style="color:rgba(255,255,255,0.7);font-size:13px;font-weight:600;
                        letter-spacing:2px;text-transform:uppercase">{get_text('now_serving', lang)}</div>
            <div class="now-num">{int(sr['token_no']):03d}</div>
            <div class="now-name">{sr['patient_name']}</div>
            <div style="color:rgba(255,255,255,0.55);font-size:13px;margin-top:4px">
                {sr['complaint']} &nbsp;·&nbsp; {sr['counter']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"No patient currently being served. Click **{get_text('call_next', lang)}** to call the first patient.")

    # Action buttons
    col_act, col_skip = st.columns(2)
    with col_act:
        if st.button(get_text("call_next", lang), type="primary", use_container_width=True):
            conn = connect()
            cur  = conn.cursor()
            # Mark current as done
            cur.execute(
                "UPDATE opd_queue SET status='Done', done_at=? WHERE status='Serving' AND registered_at LIKE ?",
                (get_ist_time(), f"{today}%")
            )
            # Get next (urgent first, then by token number)
            cur.execute("""
                SELECT id, token_no, patient_name FROM opd_queue
                WHERE status='Waiting' AND registered_at LIKE ?
                ORDER BY CASE priority WHEN 'Urgent' THEN 0 ELSE 1 END, token_no
                LIMIT 1
            """, (f"{today}%",))
            nxt = cur.fetchone()
            if nxt:
                cur.execute(
                    "UPDATE opd_queue SET status='Serving', called_at=? WHERE id=?",
                    (get_ist_time(), nxt[0])
                )
                conn.commit()
                conn.close()
                st.success(f"✅ Token {nxt[1]:03d} — {nxt[2]} called!")
                st.cache_data.clear()
                st.rerun()
            else:
                conn.commit()
                conn.close()
                st.info("No more patients in queue.")
                st.cache_data.clear()
                st.rerun()

    with col_skip:
        if st.button("⏭️ Skip / Send Back to Queue", use_container_width=True):
            conn = connect()
            cur  = conn.cursor()
            cur.execute(
                "UPDATE opd_queue SET status='Waiting', called_at=NULL WHERE status='Serving' AND registered_at LIKE ?",
                (f"{today}%",)
            )
            conn.commit()
            conn.close()
            st.info("Patient sent back to queue.")
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # Queue display
    df_wait = df_queue[df_queue["status"]=="Waiting"] if total else pd.DataFrame()
    if not df_wait.empty:
        st.subheader(f"⏳ {get_text('waiting', lang)} ({len(df_wait)})")
        for _, row in df_wait.head(8).iterrows():
            is_urgent = row['priority'] == 'Urgent'
            card_cls  = "token-urgent" if is_urgent else "token-waiting"
            badge     = "🔴 URGENT" if is_urgent else ""
            st.markdown(f"""
            <div class="{card_cls}">
                <div style="font-size:32px;font-weight:900;color:#818cf8;min-width:60px;text-align:center">
                    {int(row['token_no']):03d}
                </div>
                <div style="flex:1">
                    <div style="font-size:15px;font-weight:700;color:#f8fafc">{row['patient_name']}</div>
                    <div style="font-size:12px;color:rgba(255,255,255,0.45)">
                        {row['complaint']} · {row['gender']}, {row['age']}y · {row['counter']}
                    </div>
                </div>
                <div style="color:#ef4444;font-size:12px;font-weight:700">{badge}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Queue is empty! All patients served.")

    # Full table
    if total:
        with st.expander("📋 Full Queue Table"):
            st.dataframe(
                df_queue[["token_no","patient_name","age","gender","complaint",
                           "priority","status","registered_at"]].rename(
                    columns={"token_no":"Token","patient_name":"Name","age":"Age",
                             "gender":"Gender","complaint":"Complaint",
                             "priority":"Priority","status":"Status",
                             "registered_at":"Registered At"}
                ), use_container_width=True
            )

# ── TAB 2: Register ────────────────────────────────────────────────────────────
with tab2:
    st.subheader(f"➕ Register New Patient in Queue")

    with st.form("opd_register_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            q_name     = st.text_input(f"Patient Name *")
            q_pid      = st.text_input(f"Patient ID (if registered)")
            q_age      = st.number_input(f"Age", min_value=1, max_value=120, value=35)
            q_gender   = st.selectbox(f"Gender",
                [get_text("female",lang), get_text("male",lang), "Other"])
        with c2:
            q_complaint = st.selectbox("Complaint / Reason", [
                "Breast lump checkup",
                "AI Prediction result review",
                "Follow-up visit",
                "Routine annual screening",
                "Pain / discomfort",
                "Nipple discharge",
                "Post-surgery follow-up",
                "New patient consultation",
                "Second opinion request",
                "Chemotherapy review",
                "Report collection",
                "Other"
            ])
            q_priority = st.selectbox("Priority", ["Normal","Urgent"])
            q_counter  = st.selectbox("Counter / Room", [
                "Counter 1 — General",
                "Counter 2 — Screening",
                "Counter 3 — Follow-up",
                "Doctor Room 1",
                "Doctor Room 2",
                "Oncology Ward"
            ])

        submitted = st.form_submit_button(
            get_text("issue_token", lang), type="primary", use_container_width=True
        )

    if submitted:
        if q_name:
            conn = connect()
            cur  = conn.cursor()
            cur.execute(
                "SELECT MAX(token_no) FROM opd_queue WHERE registered_at LIKE ?",
                (f"{today}%",)
            )
            max_t = cur.fetchone()[0]
            new_t = (max_t or 0) + 1
            cur.execute("""
                INSERT INTO opd_queue(token_no,patient_id,patient_name,age,gender,
                                      complaint,priority,counter,registered_at)
                VALUES(?,?,?,?,?,?,?,?,?)
            """, (new_t, q_pid, q_name, q_age, q_gender,
                  q_complaint, q_priority, q_counter, get_ist_time()))
            conn.commit()
            conn.close()
            st.cache_data.clear()

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#14532d,#15803d);
                        border-radius:16px;padding:28px;text-align:center;margin:12px 0">
                <div style="color:rgba(255,255,255,0.7);font-size:12px;letter-spacing:2px">TOKEN ISSUED</div>
                <div style="font-size:72px;font-weight:900;color:white;line-height:1">{new_t:03d}</div>
                <div style="color:rgba(255,255,255,0.85);font-size:18px">{q_name}</div>
                <div style="color:rgba(255,255,255,0.55);font-size:13px;margin-top:6px">
                    {q_complaint} · {q_counter}
                    {"&nbsp;·&nbsp; 🔴 URGENT" if q_priority=="Urgent" else ""}
                </div>
                <div style="color:rgba(255,255,255,0.4);font-size:12px;margin-top:8px">
                    Please wait — you will be called shortly
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
            st.rerun()
        else:
            st.warning("Please enter patient name.")

# ── TAB 3: Analytics ──────────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 Today's OPD Summary")

    if total:
        import plotly.express as px

        c1, c2 = st.columns(2)
        with c1:
            status_df = df_queue["status"].value_counts().reset_index()
            status_df.columns = ["Status","Count"]
            fig = px.pie(status_df, names="Status", values="Count",
                         title="Queue Status Distribution",
                         color="Status",
                         color_discrete_map={"Waiting":"#6366f1","Serving":"#22c55e",
                                             "Done":"#94a3b8"},
                         hole=0.4)
            fig.update_layout(paper_bgcolor="#0f172a", font_color="white", height=280)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            comp_df = df_queue["complaint"].value_counts().head(6).reset_index()
            comp_df.columns = ["Complaint","Count"]
            fig2 = px.bar(comp_df, x="Count", y="Complaint", orientation="h",
                          title="Top Complaints Today",
                          color_discrete_sequence=["#818cf8"])
            fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                               font_color="white", height=280)
            st.plotly_chart(fig2, use_container_width=True)

        # Priority breakdown
        pri_df = df_queue["priority"].value_counts().reset_index()
        pri_df.columns = ["Priority","Count"]
        st.metric("Urgent Cases Today", urgent, delta=None)
        st.dataframe(df_queue[["token_no","patient_name","status","priority","complaint"]].rename(
            columns={"token_no":"Token","patient_name":"Patient","status":"Status",
                     "priority":"Priority","complaint":"Complaint"}
        ), use_container_width=True)
    else:
        st.info("No patients registered today yet. Use the Register tab.")
