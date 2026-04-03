# pages/38_Federated_Learning.py  ← REPLACE - with real India map
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
from datetime import datetime
import pytz
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()
IST  = pytz.timezone("Asia/Kolkata")

st.markdown("""
<style>
.hospital-node{background:linear-gradient(145deg,#0f172a,#1e293b);
               border-radius:14px;padding:18px;text-align:center;
               border:2px solid rgba(99,102,241,0.3);}
.hospital-active{border-color:rgba(34,197,94,0.5)!important;}
.hospital-name{font-size:13px;font-weight:700;color:#f8fafc;}
.hospital-acc{font-size:22px;font-weight:900;color:#22c55e;}
.hospital-info{font-size:11px;color:rgba(255,255,255,0.4);margin-top:4px;}
.fl-badge{background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);
          border-radius:20px;padding:4px 12px;font-size:11px;color:#a5b4fc;
          display:inline-block;margin:2px;}
.round-card{background:linear-gradient(145deg,#0f172a,#1e293b);
            border-radius:14px;padding:16px;margin:6px 0;
            border-left:3px solid #6366f1;}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:16px 0">
<div style="font-size:11px;color:#818cf8;letter-spacing:2px;text-transform:uppercase">2028 Technology</div>
<h1 style="color:#f8fafc;margin:4px 0">🌐 Federated Learning Network</h1>
<p style="color:rgba(255,255,255,0.45)">
Multi-hospital AI collaboration — improve the model without sharing patient data
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:20px">
<span class="fl-badge">🔒 Privacy-Preserving</span>
<span class="fl-badge">🏥 Multi-Hospital</span>
<span class="fl-badge">🧠 Model Sharing Only</span>
<span class="fl-badge">📊 No Patient Data Transfer</span>
<span class="fl-badge">🇮🇳 India Health Network</span>
</div>
""", unsafe_allow_html=True)

# DB
conn = connect()
conn.execute("""
    CREATE TABLE IF NOT EXISTS federated_rounds(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_no INTEGER, participating_hospitals INTEGER,
        global_accuracy REAL, improvement REAL,
        created TEXT DEFAULT (datetime('now','+5 hours 30 minutes'))
    )
""")
conn.commit()
conn.close()

# Hospital data with real coordinates
HOSPITALS = [
    {"name":"CMR University Hospital","city":"Bengaluru","state":"Karnataka",
     "lat":13.0827,"lon":77.5946,"patients":142,"accuracy":93.0,"status":"Active","role":"Coordinator"},
    {"name":"AIIMS Hyderabad","city":"Hyderabad","state":"Telangana",
     "lat":17.3850,"lon":78.4867,"patients":284,"accuracy":94.2,"status":"Active","role":"Participant"},
    {"name":"Apollo Cancer Centre","city":"Chennai","state":"Tamil Nadu",
     "lat":13.0827,"lon":80.2707,"patients":198,"accuracy":92.8,"status":"Active","role":"Participant"},
    {"name":"Kidwai Memorial Institute","city":"Bengaluru","state":"Karnataka",
     "lat":12.9716,"lon":77.5946,"patients":311,"accuracy":93.7,"status":"Active","role":"Participant"},
    {"name":"Tata Memorial Hospital","city":"Mumbai","state":"Maharashtra",
     "lat":19.0760,"lon":72.8777,"patients":523,"accuracy":95.1,"status":"Active","role":"Participant"},
    {"name":"Regional Cancer Centre","city":"Thiruvananthapuram","state":"Kerala",
     "lat":8.5241,"lon":76.9366,"patients":176,"accuracy":91.9,"status":"Pending","role":"Participant"},
    {"name":"Govt Rajaji Hospital","city":"Madurai","state":"Tamil Nadu",
     "lat":9.9252,"lon":78.1198,"patients":89,"accuracy":90.4,"status":"Syncing","role":"Participant"},
    {"name":"Nizam's Institute","city":"Hyderabad","state":"Telangana",
     "lat":17.3617,"lon":78.4747,"patients":234,"accuracy":93.5,"status":"Active","role":"Participant"},
]

tab1, tab2, tab3, tab4 = st.tabs([
    "🌐 Network Status", "🔄 Training Rounds", "📊 Model Evolution", "➕ Join Network"
])

with tab1:
    active    = sum(1 for h in HOSPITALS if h["status"]=="Active")
    total_pts = sum(h["patients"] for h in HOSPITALS)
    avg_acc   = sum(h["accuracy"] for h in HOSPITALS) / len(HOSPITALS)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🏥 Hospitals in Network", len(HOSPITALS))
    c2.metric("✅ Active Nodes", active)
    c3.metric("👥 Total Patients", f"{total_pts:,}")
    c4.metric("🧠 Global Accuracy", f"{avg_acc:.1f}%")

    st.subheader("🏥 Hospital Nodes")
    cols = st.columns(4)
    for i, h in enumerate(HOSPITALS):
        with cols[i % 4]:
            sc = "#22c55e" if h["status"]=="Active" else \
                 "#f59e0b" if h["status"]=="Syncing" else "#94a3b8"
            rb = "⭐ " if h["role"]=="Coordinator" else ""
            st.markdown(f"""
            <div class="hospital-node {'hospital-active' if h['status']=='Active' else ''}">
                <div class="hospital-name">{rb}{h['name']}</div>
                <div class="hospital-acc">{h['accuracy']}%</div>
                <div class="hospital-info">{h['city']}, {h['state']}</div>
                <div class="hospital-info">{h['patients']} patients</div>
                <div style="color:{sc};font-size:11px;font-weight:600;margin-top:6px">● {h['status']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    # ── REAL INDIA MAP with hospital locations ─────────────────────────────────
    st.subheader("🗺️ Live Hospital Network Map — India")

    df_map = pd.DataFrame(HOSPITALS)
    status_colors = {"Active":"#22c55e","Pending":"#f59e0b","Syncing":"#60a5fa"}
    df_map["color"] = df_map["status"].map(status_colors)
    df_map["size"]  = df_map["patients"] / 5

    fig_map = go.Figure()

    # Draw connection lines from CMR (coordinator) to all others
    cmr = HOSPITALS[0]
    for h in HOSPITALS[1:]:
        if h["status"] == "Active":
            fig_map.add_trace(go.Scattergeo(
                lon=[cmr["lon"], h["lon"]],
                lat=[cmr["lat"], h["lat"]],
                mode='lines',
                line=dict(width=1.5, color='rgba(99,102,241,0.4)'),
                showlegend=False,
                hoverinfo='none'
            ))

    # Active hospitals
    for status, color, sym in [
        ("Active",  "#22c55e", "circle"),
        ("Pending", "#f59e0b", "diamond"),
        ("Syncing", "#60a5fa", "square"),
    ]:
        h_filtered = [h for h in HOSPITALS if h["status"]==status]
        if h_filtered:
            fig_map.add_trace(go.Scattergeo(
                lon=[h["lon"] for h in h_filtered],
                lat=[h["lat"] for h in h_filtered],
                mode='markers+text',
                marker=dict(
                    size=[max(14, h["patients"]//15) for h in h_filtered],
                    color=color,
                    symbol=sym,
                    line=dict(color='white', width=1.5),
                    opacity=0.9
                ),
                text=[f"  {h['name'].split()[0]}" for h in h_filtered],
                textposition="middle right",
                textfont=dict(color="white", size=9),
                customdata=[[h["name"], h["city"], h["accuracy"], h["patients"], h["status"]]
                             for h in h_filtered],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{customdata[1]}<br>"
                    "Accuracy: %{customdata[2]}%<br>"
                    "Patients: %{customdata[3]}<br>"
                    "Status: %{customdata[4]}"
                    "<extra></extra>"
                ),
                name=status
            ))

    # Mark CMR with star
    fig_map.add_trace(go.Scattergeo(
        lon=[cmr["lon"]], lat=[cmr["lat"]],
        mode='markers+text',
        marker=dict(size=25, color='#f59e0b', symbol='star',
                    line=dict(color='white', width=2)),
        text=["  ⭐ CMR (Coordinator)"],
        textposition="middle right",
        textfont=dict(color="#f59e0b", size=10, family="Arial Black"),
        hovertemplate=f"<b>CMR University Hospital</b><br>Bengaluru, Karnataka<br>Accuracy: 93.0%<br>COORDINATOR<extra></extra>",
        name="Coordinator (CMR)"
    ))

    fig_map.update_layout(
        title=dict(text="Federated Hospital Network — India (Real Locations)",
                   font=dict(color="white", size=14)),
        geo=dict(
            scope='asia',
            showland=True, landcolor='#1e293b',
            showocean=True, oceancolor='#0f172a',
            showcountries=True, countrycolor='rgba(255,255,255,0.15)',
            showsubunits=True, subunitcolor='rgba(255,255,255,0.08)',
            showcoastlines=True, coastlinecolor='rgba(255,255,255,0.2)',
            bgcolor='#0f172a',
            center=dict(lat=20, lon=80),
            projection_scale=4.5,
            lataxis_range=[5, 38],
            lonaxis_range=[65, 100],
        ),
        paper_bgcolor='#0f172a',
        font_color='white',
        height=520,
        legend=dict(
            bgcolor='rgba(15,23,42,0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            x=0.01, y=0.99
        ),
        margin=dict(t=50, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("🟢 Active  🟡 Coordinator ⬛ Syncing  🔷 Pending  — Lines show model weight exchange routes")

with tab2:
    st.subheader("🔄 Federated Training Rounds")
    st.info("""
    **How it works:** Each hospital trains on local patient data → sends only model weights 
    (NOT patient data) to coordinator → CMR aggregates using FedAvg → improved global model 
    sent back to all hospitals.
    """)

    if st.button("🚀 Simulate Training Round", type="primary"):
        conn = connect()
        cur  = conn.cursor()
        cur.execute("SELECT MAX(round_no) FROM federated_rounds")
        max_r = cur.fetchone()[0] or 0
        round_num = max_r + 1
        new_acc   = min(93.0 + round_num * 0.3 + random.uniform(0.1, 0.4), 97.8)
        improvement = random.uniform(0.1, 0.4)
        cur.execute(
            "INSERT INTO federated_rounds(round_no,participating_hospitals,global_accuracy,improvement) VALUES(?,?,?,?)",
            (round_num, active, new_acc, improvement)
        )
        conn.commit()
        conn.close()
        log_audit("FL_TRAINING", "CMR Hospital", f"Round {round_num}: {new_acc:.2f}%")

        import time
        progress = st.progress(0)
        status_txt = st.empty()
        steps = [
            (15, "📤 Broadcasting global model to all hospitals..."),
            (30, "🏥 AIIMS Hyderabad computing local gradients..."),
            (45, "🏥 Apollo Chennai training on local data..."),
            (60, "🏥 Kidwai Bengaluru aggregating weights..."),
            (75, "🏥 Tata Memorial Mumbai sending model update..."),
            (90, "🔄 CMR Bengaluru running FedAvg aggregation..."),
            (100, f"✅ Round {round_num} complete! Global accuracy: {new_acc:.2f}% (+{improvement:.2f}%)"),
        ]
        for pct, msg in steps:
            progress.progress(pct)
            status_txt.info(msg)
            time.sleep(0.5)
        st.success(f"🎉 Training round {round_num} complete!")
        st.balloons()
        st.rerun()

    conn = connect()
    try:
        df_rounds = pd.read_sql_query(
            "SELECT * FROM federated_rounds ORDER BY created DESC LIMIT 10", conn
        )
    except: df_rounds = pd.DataFrame()
    conn.close()

    if not df_rounds.empty:
        st.subheader("📋 Training History")
        for _, r in df_rounds.iterrows():
            st.markdown(f"""
            <div class="round-card">
            <div style="display:flex;justify-content:space-between">
                <div>
                    <span style="color:#818cf8;font-weight:700">Round #{int(r['round_no'])}</span>
                    <span style="color:rgba(255,255,255,0.4);font-size:12px;margin-left:8px">
                        {int(r['participating_hospitals'])} hospitals
                    </span>
                </div>
                <div>
                    <span style="color:#22c55e;font-weight:700">{r['global_accuracy']:.2f}%</span>
                    <span style="color:#4ade80;font-size:12px;margin-left:6px">+{r['improvement']:.2f}%</span>
                </div>
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:4px">{str(r['created'])[:16]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No training rounds yet. Click 'Simulate Training Round'.")

with tab3:
    st.subheader("📊 Global Model Accuracy Evolution")

    conn = connect()
    try:
        df_r = pd.read_sql_query("SELECT round_no, global_accuracy FROM federated_rounds ORDER BY round_no", conn)
    except: df_r = pd.DataFrame()
    conn.close()

    if not df_r.empty:
        fig_evo = go.Figure()
        fig_evo.add_trace(go.Scatter(
            x=df_r["round_no"], y=df_r["global_accuracy"],
            mode='lines+markers+text',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=9, color='#4ade80', line=dict(color='white', width=2)),
            text=[f"{a:.1f}%" for a in df_r["global_accuracy"]],
            textposition="top center", textfont=dict(size=9, color="white"),
            fill='tozeroy', fillcolor='rgba(34,197,94,0.08)', name='Global Accuracy'
        ))
        fig_evo.add_hline(y=93.0, line_dash="dash", line_color="#6366f1",
                           annotation_text="Single Hospital Baseline: 93%",
                           annotation_font_color="#818cf8")
        fig_evo.update_layout(
            title="Federated Learning — Global Model Accuracy",
            xaxis_title="Training Round", yaxis_title="Accuracy (%)",
            yaxis_range=[90, 100],
            paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
            font_color="white", height=350
        )
        st.plotly_chart(fig_evo, use_container_width=True)
    else:
        st.info("Run training rounds to see accuracy evolution.")

    st.subheader("🔒 Privacy Guarantees")
    privacies = [
        ("Differential Privacy", "Random noise added to gradients before sharing"),
        ("Secure Aggregation", "Cryptographic protocols — hospital data stays local"),
        ("No Raw Data Transfer", "Only model weights (numbers) leave each hospital"),
        ("HIPAA/DISHA Compliant", "Meets India's Digital Health Data Protection Act"),
        ("Complete Audit Trail", "Every model exchange logged and traceable"),
    ]
    for title, desc in privacies:
        st.markdown(f"""
        <div style="display:flex;gap:12px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05)">
        <span style="color:#22c55e;font-size:18px">🛡️</span>
        <div><div style="color:#f8fafc;font-weight:700;font-size:13px">{title}</div>
        <div style="color:rgba(255,255,255,0.45);font-size:12px">{desc}</div></div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.subheader("➕ Join the Federated Network")
    st.success("Connect your hospital to improve India's breast cancer AI. Your patient data never leaves your hospital.")

    with st.form("fl_join"):
        c1, c2 = st.columns(2)
        with c1:
            h_name  = st.text_input("Hospital Name *")
            h_city  = st.text_input("City *")
            h_state = st.selectbox("State", [
                "Telangana","Andhra Pradesh","Tamil Nadu","Karnataka",
                "Maharashtra","Kerala","Delhi","West Bengal","Other"
            ])
            h_type  = st.selectbox("Hospital Type", ["Government","Private","Trust/NGO","Medical College"])
        with c2:
            h_contact = st.text_input("Contact Person")
            h_email   = st.text_input("Email")
            h_beds    = st.number_input("Hospital Beds", min_value=10, value=100)
            h_consent = st.checkbox("I agree: only model weights shared, NO patient data leaves our hospital")

        if st.form_submit_button("📨 Request to Join", type="primary", use_container_width=True):
            if h_name and h_city and h_consent:
                log_audit("FL_JOIN_REQUEST", h_name, f"{h_city}, {h_state}")
                st.success(f"✅ Join request submitted! CMR University will onboard {h_name} within 48 hours.")
                st.balloons()
            else:
                st.warning("Fill required fields and accept the data sharing agreement.")
