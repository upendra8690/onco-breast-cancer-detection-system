# pages/37_AI_Voice_Assistant.py  ← REPLACE - Fixed voice assistant
import streamlit as st
import pandas as pd
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()

st.markdown("""
<style>
.cmd-card{background:linear-gradient(145deg,#0f172a,#1e293b);
          border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px;margin:6px 0;}
.cmd-trigger{color:#818cf8;font-weight:700;font-size:13px;}
.cmd-desc{color:rgba(255,255,255,0.4);font-size:12px;margin-top:2px;}
.response-ok{background:rgba(34,197,94,0.1);border:1px solid #22c55e;border-radius:12px;padding:16px;margin:12px 0;}
.response-alert{background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:12px;padding:16px;margin:12px 0;}
.response-info{background:rgba(99,102,241,0.1);border:1px solid #6366f1;border-radius:12px;padding:16px;margin:12px 0;}
.stApp{background:#060b18;}
section[data-testid="stSidebar"]{background:#0a0f1e !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:16px 0">
<div style="font-size:11px;color:#818cf8;letter-spacing:2px;text-transform:uppercase">2027 Feature</div>
<h1 style="color:#f8fafc;margin:4px 0">🎤 AI Voice Assistant</h1>
<p style="color:rgba(255,255,255,0.45)">
Hands-free hospital navigation — speak or type commands, get instant responses
</p>
</div>
""", unsafe_allow_html=True)

# ── Command mappings ───────────────────────────────────────────────────────────
COMMANDS = {
    "open dashboard":     ("nav",   "Opening Dashboard...",          "pages/0_Dashboard.py"),
    "show dashboard":     ("nav",   "Opening Dashboard...",          "pages/0_Dashboard.py"),
    "go to dashboard":    ("nav",   "Opening Dashboard...",          "pages/0_Dashboard.py"),
    "register patient":   ("nav",   "Opening Patient Register...",   "pages/1_Patient_Register.py"),
    "new patient":        ("nav",   "Opening Patient Register...",   "pages/1_Patient_Register.py"),
    "add patient":        ("nav",   "Opening Patient Register...",   "pages/1_Patient_Register.py"),
    "ai prediction":      ("nav",   "Opening AI Prediction...",      "pages/2_AI_Prediction.py"),
    "run prediction":     ("nav",   "Opening AI Prediction...",      "pages/2_AI_Prediction.py"),
    "predict":            ("nav",   "Opening AI Prediction...",      "pages/2_AI_Prediction.py"),
    "search patient":     ("nav",   "Opening Patient Search...",     "pages/3_Patient_Search.py"),
    "patient history":    ("nav",   "Opening Patient History...",    "pages/5_History.py"),
    "show history":       ("nav",   "Opening Patient History...",    "pages/5_History.py"),
    "opd queue":          ("nav",   "Opening OPD Queue...",          "pages/31_OPD_Queue.py"),
    "open queue":         ("nav",   "Opening OPD Queue...",          "pages/31_OPD_Queue.py"),
    "compare reports":    ("nav",   "Opening Compare Reports...",    "pages/30_Compare_Reports.py"),
    "compare":            ("nav",   "Opening Compare Reports...",    "pages/30_Compare_Reports.py"),
    "treatment tracker":  ("nav",   "Opening Treatment Tracker...",  "pages/32_Treatment_Tracker.py"),
    "cancer staging":     ("nav",   "Opening Cancer Staging...",     "pages/35_AI_Cancer_Staging.py"),
    "staging":            ("nav",   "Opening Cancer Staging...",     "pages/35_AI_Cancer_Staging.py"),
    "notifications":      ("nav",   "Opening Notifications...",      "pages/34_Notification_Center.py"),
    "alerts":             ("nav",   "Opening Notifications...",      "pages/34_Notification_Center.py"),
    "model evaluation":   ("nav",   "Opening Model Evaluation...",   "pages/6_Model_Evaluation.py"),
    "dataset statistics": ("nav",   "Opening Dataset Statistics...", "pages/7_Dataset_Statistics.py"),
    "risk assessment":    ("nav",   "Opening Risk Assessment...",    "pages/16_Risk_Assessment.py"),
    "download report":    ("nav",   "Opening Download Report...",    "pages/13_Download_Report.py"),
    "send email":         ("nav",   "Opening Email Center...",       "pages/27_Send_Email.py"),
    "qr code":            ("nav",   "Opening QR Login...",           "pages/26_QR_Login.py"),
    "live monitoring":    ("nav",   "Opening Live Monitoring...",    "pages/36_Live_Monitoring.py"),
    "drug interaction":   ("nav",   "Opening Drug Checker...",       "pages/40_Drug_Interaction.py"),
    "federated learning": ("nav",   "Opening Federated Network...", "pages/38_Federated_Learning.py"),
    "genomics":           ("nav",   "Opening Genomics AI...",        "pages/39_Genomics_AI.py"),
    "future roadmap":     ("nav",   "Opening Future Roadmap...",     "pages/42_Future_Roadmap.py"),
}

def process_command(text: str):
    t = text.lower().strip()

    for cmd, (ctype, resp, page) in COMMANDS.items():
        if cmd in t:
            return ctype, resp, page

    # Data queries
    if any(w in t for w in ["how many patients","total patients","patient count"]):
        conn = connect()
        n = pd.read_sql_query("SELECT COUNT(*) as c FROM patients", conn).iloc[0]['c']
        conn.close()
        return "info", f"📊 Total patients registered: **{n}**", None

    if any(w in t for w in ["how many diagnosis","total diagnosis","ai count"]):
        conn = connect()
        n = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis", conn).iloc[0]['c']
        conn.close()
        return "info", f"🤖 Total AI diagnoses done: **{n}**", None

    if any(w in t for w in ["malignant","cancer case","urgent"]):
        conn = connect()
        n = pd.read_sql_query("SELECT COUNT(*) as c FROM diagnosis WHERE result='Malignant'", conn).iloc[0]['c']
        conn.close()
        return "alert", f"⚠️ Malignant cases detected: **{n}** — Please review immediately!", None

    if any(w in t for w in ["accuracy","model score","performance"]):
        return "info", "🎯 Current AI model accuracy: **93.0%** (CNN + VGG19, BUSI Dataset)", None

    if any(w in t for w in ["hello","hi","help","what can you do","namaste","helo"]):
        return "info", """👋 **Hello! I'm the Onco AI Voice Assistant.**

I can navigate you to any page. Try:
- *"Open Dashboard"* · *"Register Patient"* · *"Run Prediction"*
- *"OPD Queue"* · *"Compare Reports"* · *"Cancer Staging"*
- *"How many patients?"* · *"Malignant cases?"*
- *"Treatment Tracker"* · *"Live Monitoring"* · *"Drug Interaction"*""", None

    if any(w in t for w in ["thank","thanks","ok","bye","good"]):
        return "info", "You're welcome! Have a great day! 🌸 Remember: early detection saves lives.", None

    return "unknown", f"❓ I didn't understand '*{text}*'. Try: 'Open Dashboard', 'OPD Queue', or 'How many patients?'", None

# ── Browser Voice Component ────────────────────────────────────────────────────
st.subheader("🎤 Voice Control (Chrome/Edge Browser)")
st.info("**Use the microphone button below** — Works in Chrome and Edge browsers on PC and mobile.")

voice_component = st.components.v1.html("""
<style>
body{margin:0;background:transparent;}
.orb-btn{
    width:90px;height:90px;border-radius:50%;
    background:linear-gradient(135deg,#6366f1,#818cf8);
    border:3px solid rgba(255,255,255,0.2);
    color:white;font-size:28px;cursor:pointer;
    box-shadow:0 0 30px rgba(99,102,241,0.5);
    transition:all 0.3s;display:block;margin:0 auto;
}
.orb-btn:hover{transform:scale(1.05);box-shadow:0 0 50px rgba(99,102,241,0.7);}
.orb-btn.listening{
    background:linear-gradient(135deg,#ef4444,#f97316);
    animation:listenPulse 0.6s infinite;
}
@keyframes listenPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
#transcript{
    color:white;text-align:center;margin:10px auto;font-size:14px;
    min-height:32px;padding:8px 16px;font-weight:600;
    background:rgba(255,255,255,0.06);border-radius:10px;max-width:400px;
}
#status{color:rgba(255,255,255,0.5);text-align:center;font-size:11px;margin-top:4px;}
.copy-btn{
    display:block;margin:8px auto;padding:6px 16px;
    background:rgba(99,102,241,0.3);color:white;border:1px solid rgba(99,102,241,0.5);
    border-radius:8px;cursor:pointer;font-size:12px;
}
.copy-btn:hover{background:rgba(99,102,241,0.5);}
</style>
<div style="text-align:center;padding:10px">
    <button class="orb-btn" id="voiceBtn" onclick="toggleVoice()">🎤</button>
    <div id="transcript">Tap the microphone and speak...</div>
    <div id="status">Checking browser support...</div>
    <button class="copy-btn" id="copyBtn" onclick="copyText()" style="display:none">
        📋 Copy command text to use below
    </button>
</div>
<script>
let recognition=null, isListening=false, lastText='';
const btn=document.getElementById('voiceBtn');
const trans=document.getElementById('transcript');
const status=document.getElementById('status');
const copyBtn=document.getElementById('copyBtn');

if('webkitSpeechRecognition' in window||'SpeechRecognition' in window){
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    recognition=new SR();
    recognition.continuous=false;
    recognition.interimResults=true;
    recognition.lang='en-IN';
    status.textContent='✅ Voice recognition ready! Click mic to speak.';

    recognition.onstart=()=>{
        isListening=true;
        btn.classList.add('listening');
        btn.textContent='🔴';
        status.textContent='🎙️ Listening... Speak now!';
        status.style.color='#ef4444';
        copyBtn.style.display='none';
    };
    recognition.onresult=(e)=>{
        let t='';
        for(let i=e.resultIndex;i<e.results.length;i++) t+=e.results[i][0].transcript;
        trans.textContent='💬 "'+t+'"';
        lastText=t;
        if(e.results[e.results.length-1].isFinal){
            copyBtn.style.display='block';
            status.textContent='✅ Heard: "'+t+'" — Copy it below & execute!';
            status.style.color='#22c55e';
        }
    };
    recognition.onend=()=>{
        isListening=false;
        btn.classList.remove('listening');
        btn.textContent='🎤';
    };
    recognition.onerror=(e)=>{
        btn.classList.remove('listening');
        btn.textContent='🎤';
        isListening=false;
        if(e.error==='not-allowed')
            status.textContent='❌ Mic blocked! Click the 🔒 in address bar → Allow microphone';
        else
            status.textContent='❌ Error: '+e.error+'. Try again.';
        status.style.color='#ef4444';
    };
} else {
    status.textContent='⚠️ Use Chrome or Edge for voice. Type commands below instead.';
    btn.style.opacity='0.4';
    btn.style.cursor='not-allowed';
}

function toggleVoice(){
    if(!recognition){return;}
    if(isListening){recognition.stop();}
    else{recognition.start();}
}

function copyText(){
    if(lastText){
        navigator.clipboard.writeText(lastText).then(()=>{
            copyBtn.textContent='✅ Copied! Paste in box below & click Execute';
        });
    }
}
</script>
""", height=200)

# ── Text Input Command ─────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("⌨️ Type Command (works on all browsers)")

col1, col2 = st.columns([4, 1])
with col1:
    text_cmd = st.text_input(
        "Command:",
        placeholder="e.g. 'Open Dashboard', 'How many patients?', 'OPD Queue'",
        label_visibility="collapsed",
        key="voice_cmd_input"
    )
with col2:
    execute_btn = st.button("▶ Execute", type="primary", use_container_width=True)

# Quick command buttons
st.markdown("**Quick Commands:**")
qcols = st.columns(5)
quick = [
    "Open Dashboard", "OPD Queue", "Run Prediction",
    "Compare Reports", "How many patients?"
]
for i, (col, q) in enumerate(zip(qcols, quick)):
    if col.button(q, key=f"qc_{i}", use_container_width=True):
        ctype, resp, page = process_command(q)
        log_audit("VOICE_CMD", "doctor", f"Quick: {q} → {ctype}")
        st.markdown(f"""
        <div class="response-{'ok' if ctype=='nav' else 'info' if ctype=='info' else 'alert' if ctype=='alert' else 'info'}">
        <b style="color:#f8fafc">🤖 Response:</b><br>{resp}
        </div>
        """, unsafe_allow_html=True)
        if page:
            st.button(f"→ Open Page", key=f"go_{i}", on_click=lambda p=page: st.switch_page(p))

if execute_btn and text_cmd:
    ctype, resp, page = process_command(text_cmd)
    log_audit("VOICE_CMD", "doctor", f"Command: {text_cmd} → {ctype}")

    css_class = ("response-alert" if ctype=="alert" else
                 "response-ok"    if ctype=="nav"   else
                 "response-info"  if ctype=="info"  else
                 "response-info")

    st.markdown(f"""
    <div class="{css_class}">
    <div style="font-size:12px;color:rgba(255,255,255,0.5)">🤖 AI Response</div>
    <div style="font-size:15px;font-weight:700;color:#f8fafc;margin-top:4px">{resp}</div>
    </div>
    """, unsafe_allow_html=True)

    if page:
        if st.button(f"→ Go to {page.split('/')[-1].replace('.py','').replace('_',' ')}", type="primary"):
            st.switch_page(page)

# ── Voice history ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📜 Command History")
conn = connect()
try:
    df_v = pd.read_sql_query(
        "SELECT details, created FROM audit_log WHERE action='VOICE_CMD' ORDER BY created DESC LIMIT 10",
        conn
    )
    if not df_v.empty:
        for _, r in df_v.iterrows():
            st.markdown(f"""
            <div style="display:flex;gap:10px;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04)">
            <span style="font-size:14px">🎤</span>
            <span style="flex:1;color:#94a3b8;font-size:12px">{r['details']}</span>
            <span style="color:rgba(255,255,255,0.25);font-size:11px">{str(r['created'])[:16]}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No commands used yet.")
except:
    st.info("No history yet.")
conn.close()
