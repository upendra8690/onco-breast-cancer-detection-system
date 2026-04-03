# pages/26_QR_Login.py  ← REPLACE - Works on ANY phone, ANY network via public URL
import streamlit as st
import qrcode
import io
import socket
import subprocess
import os
from utils.sidebar import render_sidebar
from utils.language import get_text
from database.database import connect

lang = render_sidebar()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
.qr-col { background:linear-gradient(145deg,#0f172a,#1e293b);
          border:1px solid rgba(255,255,255,0.07); border-radius:16px;
          padding:20px; text-align:center; }
.step-card{background:linear-gradient(145deg,#0f172a,#1e293b);
           border:1px solid rgba(255,255,255,0.07);
           border-radius:14px;padding:16px;text-align:center;}
.step-num{font-size:30px;font-weight:900;color:#6366f1;}
.step-text{font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;line-height:1.5;}
.public-url-box{
    background:linear-gradient(135deg,rgba(34,197,94,0.12),rgba(22,163,74,0.08));
    border:2px solid #22c55e; border-radius:16px; padding:24px;
    text-align:center; margin:16px 0;
}
.local-url-box{
    background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.3);
    border-radius:12px; padding:16px; margin:8px 0;
}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.title(f"📱 {get_text('qr_login', lang)}")
st.write(get_text("scan_instructions", lang))

# ─────────────────────────────────────────────────────────────────────────────
# QR GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def make_qr(data, fill="#003366", size=10):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size, border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill, back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ─────────────────────────────────────────────────────────────────────────────
# LOCAL IP DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

local_ip = get_local_ip()
port = st.sidebar.text_input("Port", value="8501")
local_url = f"http://{local_ip}:{port}"

# ═════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ═════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "🌐 Public URL (Any Phone/Network)",
    "📡 Local WiFi QR",
    "🏷️ Patient QR Cards"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: PUBLIC URL via ngrok — works on any phone, any network, anywhere
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div class="public-url-box">
    <h3 style="color:#4ade80;margin:0">🌍 Make Your App Public — Works on ANY Phone</h3>
    <p style="color:rgba(255,255,255,0.6);margin:8px 0 0 0;font-size:14px">
    Using <b>ngrok</b> to create a public URL. Phone can be on any network — mobile data, different WiFi, anywhere in India.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.info("""
    **Step 1:** Open a NEW terminal (keep Streamlit running in the other one)
    
    **Step 2:** Run this command:
    ```
    pip install pyngrok
    ```
    
    **Step 3:** Run:
    ```
    ngrok http 8501
    ```
    
    **Step 4:** Copy the `https://xxxx.ngrok.io` URL that appears
    
    **Step 5:** Paste it below 👇
    """)

    ngrok_url = st.text_input(
        "🔗 Paste your ngrok URL here:",
        placeholder="https://abc123.ngrok.io",
        help="Run 'ngrok http 8501' in terminal and paste the https URL here"
    )

    if ngrok_url and ngrok_url.startswith("http"):
        st.success(f"✅ Public URL: **{ngrok_url}**")
        st.markdown(f"""
        <div class="public-url-box">
        <div style="font-size:13px;color:rgba(255,255,255,0.6)">Public URL — works on any phone, any network</div>
        <div style="font-size:20px;font-weight:700;color:#4ade80;margin:8px 0">{ngrok_url}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.4)">Share this with doctors, patients, evaluators anywhere in India</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            buf = make_qr(ngrok_url, fill="#14532d")
            st.markdown('<div class="qr-col">', unsafe_allow_html=True)
            st.image(buf, caption="🌐 Open Website", width=200)
            buf.seek(0)
            st.download_button("⬇️ Download", buf.getvalue(), "public_website_qr.png", "image/png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            login_url = f"{ngrok_url}/Login"
            buf2 = make_qr(login_url, fill="#7f1d1d")
            st.markdown('<div class="qr-col">', unsafe_allow_html=True)
            st.image(buf2, caption="🔐 Login Page", width=200)
            buf2.seek(0)
            st.download_button("⬇️ Download", buf2.getvalue(), "public_login_qr.png", "image/png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c3:
            dash_url = f"{ngrok_url}/Dashboard"
            buf3 = make_qr(dash_url, fill="#1e3a5f")
            st.markdown('<div class="qr-col">', unsafe_allow_html=True)
            st.image(buf3, caption="🏥 Dashboard", width=200)
            buf3.seek(0)
            st.download_button("⬇️ Download", buf3.getvalue(), "public_dashboard_qr.png", "image/png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📲 CEO / Teacher Demo QR — Print This!")
        demo_msg = (
            f"🧬 ONCO AI — Breast Cancer Detection System\n"
            f"CMR University Hospital\n"
            f"URL: {ngrok_url}\n\n"
            f"Doctor Login: admin / admin\n"
            f"Features: AI Prediction, GradCAM, Multi-language,\n"
            f"OPD Queue, Treatment Tracker, Cancer Staging\n\n"
            f"IEEE Publication Ready | 93% Accuracy\n"
            f"Scan to access from anywhere!"
        )
        buf_demo = make_qr(demo_msg, fill="#581c87", size=8)
        col1, col2 = st.columns([1,2])
        with col1:
            st.image(buf_demo, caption="CEO Demo QR", width=220)
            buf_demo.seek(0)
            st.download_button("⬇️ Download Demo QR", buf_demo.getvalue(),
                               "ceo_demo_qr.png", "image/png", use_container_width=True)
        with col2:
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#0f172a,#1e293b);
                        border:1px solid rgba(99,102,241,0.3);border-radius:14px;padding:20px">
            <h4 style="color:#818cf8;margin:0">How to use for Demo:</h4>
            <ol style="color:rgba(255,255,255,0.6);font-size:13px;margin-top:8px;padding-left:18px">
                <li>Print this QR or show it on screen</li>
                <li>Ask evaluator to scan with their phone</li>
                <li>Works on any phone, any SIM, anywhere</li>
                <li>They can browse full system on their phone</li>
                <li>Login: <b style="color:#f8fafc">admin / admin</b></li>
            </ol>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Paste your ngrok URL above to generate public QR codes.")
        st.markdown("""
        **Alternative: Use Streamlit Cloud for permanent public URL**

        1. Go to [share.streamlit.io](https://share.streamlit.io)
        2. Connect your GitHub
        3. Deploy your app → get a permanent `https://yourapp.streamlit.app` URL
        4. That URL works everywhere, forever, no terminal needed
        """)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Local WiFi QR (same as before)
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.info(f"🌐 Local Network URL: **{local_url}** — Works only on same WiFi")

    st.markdown("""
    <div style="background:rgba(245,158,11,0.1);border:1px solid #f59e0b;border-radius:12px;padding:14px;margin-bottom:16px">
    ⚠️ <b>Limitation:</b> These QR codes only work when phone is on the SAME WiFi network as this computer.
    For demos with people on different networks, use the <b>Public URL tab above</b>.
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, (url_suffix, label, fill) in zip(
        [c1, c2, c3],
        [("", "🌐 Open Website", "#003366"),
         ("/Login", "🔐 Login", "#7f1d1d"),
         ("/Dashboard", "🏥 Dashboard", "#14532d")]
    ):
        with col:
            full_url = local_url + url_suffix
            buf = make_qr(full_url, fill=fill)
            st.image(buf, caption=label, width=210)
            buf.seek(0)
            st.download_button("⬇️ Download", buf.getvalue(),
                               f"local_{label.split()[1].lower()}_qr.png", "image/png",
                               use_container_width=True)

    # How to scan
    st.markdown("---")
    st.subheader("📋 How to Scan (Same WiFi Only)")
    c1,c2,c3,c4 = st.columns(4)
    for col, (n, text) in zip([c1,c2,c3,c4], [
        ("1","Connect phone to SAME WiFi as this computer"),
        ("2","Open Camera app — no extra app needed"),
        ("3","Point at QR code until link appears"),
        ("4","Tap link — Onco AI opens in phone!"),
    ]):
        col.markdown(f'<div class="step-card"><div class="step-num">{n}</div><div class="step-text">{text}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Patient QR Cards
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("🏷️ Generate Patient QR Card")
    st.write("Print and attach to patient file. Patient scans → opens their portal.")

    conn = connect()
    import pandas as pd
    try:
        df_pts = pd.read_sql_query(
            "SELECT patient_id, name, phone FROM patients ORDER BY created DESC", conn
        )
    except:
        df_pts = pd.DataFrame()
    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        pid_input = st.text_input("Enter Patient ID:")
    with col2:
        if not df_pts.empty:
            opts = ["-- Select Patient --"] + df_pts.apply(
                lambda r: f"{r['patient_id']} — {r['name']}", axis=1).tolist()
            sel = st.selectbox("Or pick from list:", opts)
            if sel != "-- Select Patient --":
                pid_input = sel.split(" — ")[0]

    use_public = st.checkbox("Use public URL (ngrok) for QR", value=bool(ngrok_url) if 'ngrok_url' in dir() else False)

    if st.button("🖨️ Generate Patient QR", type="primary", use_container_width=True):
        if pid_input:
            base = ngrok_url if (use_public and ngrok_url and ngrok_url.startswith("http")) else local_url
            qr_data = (
                f"ONCO AI PATIENT CARD\n"
                f"CMR University Hospital\n"
                f"Patient ID: {pid_input}\n"
                f"Portal: {base}/Login\n"
                f"Instructions: Enter your Patient ID + Name to login\n"
                f"Help: 040-12345678"
            )
            buf_p = make_qr(qr_data, fill="#003366", size=8)
            c1, c2 = st.columns([1,2])
            with c1:
                st.image(buf_p, caption=f"Patient {pid_input}", width=220)
                buf_p.seek(0)
                st.download_button(
                    f"⬇️ Download Patient {pid_input} QR",
                    buf_p.getvalue(), f"patient_{pid_input}_qr.png", "image/png",
                    use_container_width=True
                )
            with c2:
                st.markdown(f"""
                <div style="background:linear-gradient(145deg,#0f172a,#1e293b);
                            border:1px solid rgba(99,102,241,0.25);border-radius:14px;padding:18px">
                <h4 style="color:#818cf8;margin:0">Patient {pid_input} QR Card</h4>
                <p style="color:rgba(255,255,255,0.5);font-size:13px;margin:10px 0">
                📌 <b>Instructions for patient:</b><br>
                1. Scan this QR with your phone camera<br>
                2. You will see the Onco AI login page<br>
                3. Enter your Patient ID: <b style="color:#f8fafc">{pid_input}</b><br>
                4. Enter your registered name<br>
                5. View all your diagnosis reports
                </p>
                <p style="color:rgba(255,255,255,0.3);font-size:11px">
                Portal: {base}/Login
                </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Enter Patient ID first.")

    st.markdown("---")
    st.info("""
    💡 **Best Practice for Hospitals:**
    - Print QR Login page → laminate → keep at reception
    - Generate per-patient QR → attach to paper file
    - Use **ngrok** or **Streamlit Cloud** for public URL that works on any phone
    """)
