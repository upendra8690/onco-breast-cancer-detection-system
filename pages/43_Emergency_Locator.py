# pages/43_Emergency_Locator.py
# ═══════════════════════════════════════════════════════════════════
#  ONCO AI — REAL-TIME EMERGENCY HOSPITAL LOCATOR
#  Uses browser GPS + OpenStreetMap/Leaflet.js for REAL map
#  Built by CMR University, Bengaluru — 2026
#  First AI breast cancer system with live emergency locator in India
# ═══════════════════════════════════════════════════════════════════
import streamlit as st

st.set_page_config(page_title="Onco AI Emergency Locator", layout="wide")

import streamlit.components.v1 as components
import pandas as pd
import math
import urllib.parse
import json

from auth.guard import check_login
from database.database import connect, log_audit
from utils.sidebar import render_sidebar


check_login()
lang = render_sidebar()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
*,[class*="css"]{font-family:'Inter',sans-serif !important;}
.stApp{background:#04080f !important;}
section[data-testid="stSidebar"]{background:#070c18 !important;}

.emg-banner{
    background:linear-gradient(135deg,#7f0000,#cc0000,#ff1a1a);
    border-radius:16px;padding:20px 26px;margin-bottom:18px;
    border:2px solid #ff4444;
    box-shadow:0 0 40px rgba(255,0,0,0.35);
    display:flex;justify-content:space-between;align-items:center;
    animation:pulse 2s ease-in-out infinite;
}
@keyframes pulse{0%,100%{box-shadow:0 0 40px rgba(255,0,0,0.3)}50%{box-shadow:0 0 70px rgba(255,0,0,0.6)}}
.eb-title{font-size:22px;font-weight:900;color:white;}
.eb-sub{font-size:11px;color:rgba(255,255,255,0.65);margin-top:3px;}
.eb-nums{text-align:right;}
.eb-num{font-size:26px;font-weight:900;color:white;}
.eb-lbl{font-size:9px;color:rgba(255,255,255,0.55);}

.hcard{
    background:linear-gradient(145deg,#0a1020,#0f1830);
    border:1px solid rgba(255,255,255,0.07);border-radius:14px;
    padding:16px 18px;margin:7px 0;
    border-left:4px solid #6366f1;
}
.hcard-govt{border-left-color:#22c55e !important;}
.hcard-pvt {border-left-color:#60a5fa !important;}
.hcard-onco{border-left-color:#f59e0b !important;}
.hcard-name{font-size:14px;font-weight:800;color:#f0f6ff;margin-bottom:3px;}
.hcard-meta{font-size:11px;color:rgba(255,255,255,0.4);line-height:1.75;}
.hcard-dist{font-size:22px;font-weight:900;color:#818cf8;float:right;line-height:1;}
.hcard-dist-lbl{font-size:9px;color:rgba(255,255,255,0.3);}
.hcard-btns{display:flex;gap:7px;margin-top:10px;flex-wrap:wrap;}
.hbtn{padding:7px 13px;border-radius:8px;font-size:11px;font-weight:700;
      text-decoration:none;display:inline-flex;align-items:center;gap:5px;color:white;}
.hbtn-call{background:linear-gradient(135deg,#16a34a,#22c55e);}
.hbtn-map {background:linear-gradient(135deg,#1d4ed8,#3b82f6);}
.hbtn-wa  {background:linear-gradient(135deg,#15803d,#25d366);}
.hbtn-dir {background:linear-gradient(135deg,#7c3aed,#8b5cf6);}

.enum-card{
    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
    border-radius:12px;padding:14px;text-align:center;cursor:pointer;
}
.tip-box{background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);
         border-radius:12px;padding:14px 16px;margin:6px 0;}
.tip-title{font-size:13px;font-weight:700;color:#fca5a5;margin-bottom:4px;}
.tip-body{font-size:12px;color:rgba(255,255,255,0.45);line-height:1.65;}
.nearest-tag{background:#f59e0b22;color:#fbbf24;border:1px solid #f59e0b44;
             border-radius:5px;padding:2px 8px;font-size:9px;font-weight:800;
             letter-spacing:1px;margin-left:6px;}
.badge{display:inline-block;padding:2px 8px;border-radius:5px;font-size:9px;
       font-weight:700;margin:2px;}
.badge-govt{background:#22c55e22;color:#4ade80;border:1px solid #22c55e33;}
.badge-emg {background:#ef444422;color:#fca5a5;border:1px solid #ef444433;}
.badge-ay  {background:#818cf822;color:#a5b4fc;border:1px solid #818cf833;}
</style>
""", unsafe_allow_html=True)

HOSPITALS = [
    {"name":"Kidwai Memorial Institute of Oncology","city":"Bengaluru","type":"govt",
     "lat":12.9364,"lon":77.5916,"phone":"080-26094000","ayushman":True,"emergency":True,
     "beds":650,"address":"Dr M H Marigowda Rd, Bengaluru 560029",
     "speciality":"Breast Cancer, Chemo, Radiation"},
    {"name":"CMR University Hospital — Onco AI Centre","city":"Bengaluru","type":"onco",
     "lat":13.1880,"lon":77.6510,"phone":"9342900666","ayushman":True,"emergency":True,
     "beds":200,"address":"CMR University (Lakeside Campus), Off Bagalur Main Rd, near Kempegowda International Airport, Mitganahalli, Hennur Gardens, Chagalahatti, Bengaluru, Karnataka 562149",
     "speciality":"AI Breast Cancer Detection"},
    {"name":"HCG Cancer Centre","city":"Bengaluru","type":"pvt",
     "lat":12.9726,"lon":77.5946,"phone":"080-40206000","ayushman":False,"emergency":True,
     "beds":300,"address":"P. Kalinga Rao Road, Bengaluru",
     "speciality":"Breast Surgery, Oncology"},
    {"name":"Manipal Comprehensive Cancer Centre","city":"Bengaluru","type":"pvt",
     "lat":12.9591,"lon":77.6414,"phone":"1800-102-1111","ayushman":False,"emergency":True,
     "beds":450,"address":"HAL Airport Rd, Bengaluru",
     "speciality":"Multi-specialty Cancer"},
    {"name":"Narayana Health City","city":"Bengaluru","type":"pvt",
     "lat":12.9013,"lon":77.6475,"phone":"080-71222222","ayushman":False,"emergency":True,
     "beds":1000,"address":"Bommasandra, Bengaluru",
     "speciality":"Cancer, Cardiac, Neuro"},
    {"name":"Bangalore Institute of Oncology","city":"Bengaluru","type":"onco",
     "lat":12.9654,"lon":77.6015,"phone":"080-67801000","ayushman":True,"emergency":True,
     "beds":200,"address":"KR Road, Bengaluru 560002",
     "speciality":"Breast Oncology, Surgery"},
    {"name":"MNJ Institute of Oncology","city":"Hyderabad","type":"govt",
     "lat":17.3920,"lon":78.4630,"phone":"040-23308500","ayushman":True,"emergency":True,
     "beds":850,"address":"Red Hills, Lakdikapul, Hyderabad 500004",
     "speciality":"Cancer, Chemo, Radiation"},
    {"name":"Basavatarakam Cancer Hospital","city":"Hyderabad","type":"pvt",
     "lat":17.4126,"lon":78.4482,"phone":"040-23548888","ayushman":False,"emergency":True,
     "beds":400,"address":"Banjara Hills Rd 10, Hyderabad",
     "speciality":"Breast Cancer, All Cancers"},
    {"name":"AIIMS Hyderabad","city":"Hyderabad","type":"govt",
     "lat":17.5500,"lon":78.5300,"phone":"040-24651111","ayushman":True,"emergency":True,
     "beds":750,"address":"Bibinagar, Telangana",
     "speciality":"All Specialities"},
    {"name":"Yashoda Hospitals Cancer Centre","city":"Hyderabad","type":"pvt",
     "lat":17.4330,"lon":78.4374,"phone":"040-45674567","ayushman":False,"emergency":True,
     "beds":350,"address":"Alexander Rd, Secunderabad",
     "speciality":"Breast Cancer, Oncology"},
    {"name":"Cancer Institute (WIA)","city":"Chennai","type":"govt",
     "lat":13.0061,"lon":80.2285,"phone":"044-22350241","ayushman":True,"emergency":True,
     "beds":1000,"address":"38 Sardar Patel Rd, Chennai 600036",
     "speciality":"Breast Cancer, Gynaec Onco"},
    {"name":"Apollo Cancer Centre","city":"Chennai","type":"pvt",
     "lat":13.0600,"lon":80.2500,"phone":"044-28290200","ayushman":False,"emergency":True,
     "beds":450,"address":"21 Greams Lane, Chennai 600006",
     "speciality":"Comprehensive Cancer Care"},
    {"name":"MIOT International","city":"Chennai","type":"pvt",
     "lat":13.0358,"lon":80.2161,"phone":"044-22490000","ayushman":False,"emergency":True,
     "beds":600,"address":"Mount Poonamallee Rd, Chennai",
     "speciality":"Cancer, Ortho, Cardiac"},
    {"name":"Tata Memorial Hospital","city":"Mumbai","type":"govt",
     "lat":18.9982,"lon":72.8126,"phone":"022-24177000","ayushman":True,"emergency":True,
     "beds":1300,"address":"Dr E Borges Road, Parel, Mumbai 400012",
     "speciality":"All Cancers — Premier Centre"},
    {"name":"Kokilaben Dhirubhai Ambani Hospital","city":"Mumbai","type":"pvt",
     "lat":19.1313,"lon":72.8265,"phone":"022-42696969","ayushman":False,"emergency":True,
     "beds":750,"address":"Andheri West, Mumbai",
     "speciality":"Comprehensive Cancer"},
    {"name":"Jaslok Hospital Cancer Centre","city":"Mumbai","type":"pvt",
     "lat":18.9745,"lon":72.8113,"phone":"022-66573333","ayushman":False,"emergency":True,
     "beds":350,"address":"Dr G Deshmukh Marg, Mumbai",
     "speciality":"Cancer, Neurosurgery"},
    {"name":"AIIMS New Delhi — Cancer Centre","city":"New Delhi","type":"govt",
     "lat":28.5672,"lon":77.2100,"phone":"011-26588500","ayushman":True,"emergency":True,
     "beds":2500,"address":"Ansari Nagar, New Delhi",
     "speciality":"All Specialities"},
    {"name":"Rajiv Gandhi Cancer Institute","city":"New Delhi","type":"pvt",
     "lat":28.6897,"lon":77.1627,"phone":"011-47022222","ayushman":False,"emergency":True,
     "beds":400,"address":"Rohini, New Delhi 110085",
     "speciality":"Breast Cancer, Radiology"},
    {"name":"BLK-Max Cancer Centre","city":"New Delhi","type":"pvt",
     "lat":28.6458,"lon":77.1826,"phone":"011-30403040","ayushman":False,"emergency":True,
     "beds":650,"address":"Pusa Road, New Delhi",
     "speciality":"Oncology, Transplant"},
    {"name":"Chittaranjan National Cancer Institute","city":"Kolkata","type":"govt",
     "lat":22.5141,"lon":88.3622,"phone":"033-24748960","ayushman":True,"emergency":True,
     "beds":850,"address":"37 S P Mukherjee Road, Kolkata 700026",
     "speciality":"All Cancers"},
    {"name":"Regional Cancer Centre (RCC)","city":"Thiruvananthapuram","type":"govt",
     "lat":8.5241,"lon":76.9366,"phone":"0471-2442541","ayushman":True,"emergency":True,
     "beds":850,"address":"Medical College Campus, TVM 695011",
     "speciality":"All Cancers"},
    {"name":"Ruby Hall Clinic Cancer Centre","city":"Pune","type":"pvt",
     "lat":18.5204,"lon":73.8767,"phone":"020-66455555","ayushman":False,"emergency":True,
     "beds":380,"address":"40 Sassoon Road, Pune 411001",
     "speciality":"Breast Oncology, Surgery"},
    {"name":"Gujarat Cancer Research Institute","city":"Ahmedabad","type":"govt",
     "lat":23.0225,"lon":72.5714,"phone":"079-26305060","ayushman":True,"emergency":True,
     "beds":700,"address":"Civil Hospital Campus, Ahmedabad 380016",
     "speciality":"All Cancers"},
]

EMERGENCY_NUMS = [
    {"name":"Ambulance","number":"108","icon":"🚑","color":"#ef4444"},
    {"name":"Emergency","number":"112","icon":"🚨","color":"#ef4444"},
    {"name":"Health Helpline","number":"104","icon":"🏥","color":"#22c55e"},
    {"name":"Ayushman Bharat","number":"14555","icon":"🇮🇳","color":"#3b82f6"},
    {"name":"Cancer Aid Society","number":"1800-103-0009","icon":"🎗️","color":"#f59e0b"},
    {"name":"NIMHANS Crisis","number":"080-46110007","icon":"🧠","color":"#8b5cf6"},
    {"name":"iCall India","number":"9152987821","icon":"📞","color":"#06b6d4"},
    {"name":"Police","number":"100","icon":"👮","color":"#6366f1"},
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d = math.radians
    dlat = d(lat2-lat1); dlon = d(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(d(lat1))*math.cos(d(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def gdir(from_lat, from_lon, to_lat, to_lon):
    return f"https://www.google.com/maps/dir/{from_lat},{from_lon}/{to_lat},{to_lon}"

def gmap(lat, lon, name):
    q = urllib.parse.quote(name)
    return f"https://www.google.com/maps/search/{q}/@{lat},{lon},16z"

def wa_msg(h, pat):
    m = (f"🚨 EMERGENCY — Onco AI CMR University Hospital (Lakeside Campus)\nPatient: {pat}\n"
         f"Nearest Hospital: {h['name']}\nAddress: {h['address']}\n"
         f"Phone: {h['phone']}\nPlease keep oncology team ready. Arriving now.")
    return f"https://wa.me/?text={urllib.parse.quote(m)}"

st.markdown("""
<div class="emg-banner">
  <div>
    <div class="eb-title">🚨 Emergency Hospital Locator</div>
    <div class="eb-sub">
      Real-time GPS · Nearest cancer hospitals · Live directions · One-tap call<br>
      First AI breast cancer system with live emergency locator — CMR University (Lakeside Campus) 2026
    </div>
  </div>
  <div class="eb-nums">
    <div class="eb-num">📞 108</div><div class="eb-lbl">Ambulance</div>
    <div style="margin-top:4px"><span class="eb-num" style="font-size:20px">📞 112</span></div>
    <div class="eb-lbl">National Emergency</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📞 Emergency Helplines — Tap to Call")
cols = st.columns(4)
for i, en in enumerate(EMERGENCY_NUMS):
    with cols[i % 4]:
        st.markdown(f"""
        <a href="tel:{en['number']}" style="text-decoration:none">
        <div class="enum-card" style="border:1px solid {en['color']}33">
            <div style="font-size:22px">{en['icon']}</div>
            <div style="font-size:10px;font-weight:700;color:#f0f6ff;margin-top:3px">{en['name']}</div>
            <div style="font-size:16px;font-weight:900;color:{en['color']};margin-top:3px">{en['number']}</div>
        </div></a>
        """, unsafe_allow_html=True)

conn = connect()
try:
    df_pts = pd.read_sql_query("SELECT patient_id, name FROM patients ORDER BY name", conn)
except:
    df_pts = pd.DataFrame()
conn.close()

pat_name = "Patient"
if not df_pts.empty:
    pt_opts = ["-- Select Patient --"] + df_pts.apply(lambda r: f"{r['patient_id']} — {r['name']}", axis=1).tolist()
    pt_sel = st.sidebar.selectbox("👤 Patient for alerts:", pt_opts)
    if pt_sel != "-- Select Patient --":
        pat_name = pt_sel.split(" — ")[1]

st.markdown("---")
st.markdown("### 🗺️ Live Map — Find Nearest Cancer Hospitals")
st.info("📍 Click **Use My Location** on the map to detect your real GPS location, draw a route line, and show the nearest hospitals automatically.")

hosp_json = json.dumps([{
    "name": h["name"],
    "city": h["city"],
    "type": h["type"],
    "lat": h["lat"],
    "lon": h["lon"],
    "phone": h["phone"],
    "address": h["address"],
    "speciality": h["speciality"],
    "beds": h["beds"],
    "ayushman": h["ayushman"],
    "emergency": h["emergency"],
} for h in HOSPITALS])

MAP_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Onco AI Emergency Locator</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<style>
  * {{ margin:0;padding:0;box-sizing:border-box; font-family:'Segoe UI',Arial,sans-serif; }}
  body {{ background:#04080f; color:#f0f6ff; }}
  #map {{ width:100%; height:480px; border-radius:0 0 16px 16px; border:2px solid rgba(99,102,241,0.3); }}
  .top-bar {{ background:linear-gradient(90deg,#001533,#002966); padding:12px 16px; border:2px solid rgba(0,100,200,0.3); border-radius:16px 16px 0 0; display:flex;justify-content:space-between;align-items:center; }}
  .top-bar-title {{ font-size:14px;font-weight:700;color:white; }}
  .top-bar-sub {{ font-size:10px;color:rgba(255,255,255,0.5);margin-top:2px; }}
  .controls {{ background:#0a1020; padding:10px 16px; display:flex;gap:8px;flex-wrap:wrap;align-items:center; border-left:2px solid rgba(99,102,241,0.3); border-right:2px solid rgba(99,102,241,0.3); }}
  .btn {{ padding:8px 16px;border-radius:8px;border:none; font-size:12px;font-weight:700;cursor:pointer; display:inline-flex;align-items:center;gap:5px; transition:all 0.2s; }}
  .btn-gps {{ background:linear-gradient(135deg,#dc2626,#ef4444);color:white; }}
  .btn-gps:hover {{ transform:scale(1.04); box-shadow:0 0 20px rgba(239,68,68,0.4); }}
  .btn-filter {{ background:rgba(255,255,255,0.06);color:#a5b4fc;border:1px solid rgba(99,102,241,0.3); }}
  .btn-filter.active {{ background:rgba(99,102,241,0.25);border-color:#6366f1;color:white; }}
  .status-bar {{ background:#070f20; padding:8px 16px; font-size:11px;color:rgba(255,255,255,0.5); border-left:2px solid rgba(99,102,241,0.3); border-right:2px solid rgba(99,102,241,0.3); display:flex;align-items:center;gap:8px; }}
  .status-dot {{ width:8px;height:8px;border-radius:50%;background:#22c55e; animation:blink 1.5s infinite; }}
  @keyframes blink {{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
  .leaflet-popup-content-wrapper {{ background:#0f1e38 !important; border:1px solid rgba(99,102,241,0.4) !important; border-radius:12px !important; box-shadow:0 8px 32px rgba(0,0,0,0.6) !important; color:#f0f6ff !important; min-width:260px; }}
  .leaflet-popup-tip {{ background:#0f1e38 !important; }}
  .leaflet-popup-content {{ margin:14px 16px !important; }}
  .popup-name {{ font-size:14px;font-weight:800;color:#f0f6ff;margin-bottom:4px; }}
  .popup-type {{ display:inline-block;padding:2px 8px;border-radius:5px; font-size:9px;font-weight:700;margin-bottom:6px; }}
  .popup-meta {{ font-size:11px;color:rgba(255,255,255,0.45);line-height:1.7;margin-bottom:8px; }}
  .popup-dist {{ font-size:18px;font-weight:900;color:#818cf8; }}
  .popup-btns {{ display:flex;gap:5px;margin-top:8px;flex-wrap:wrap; }}
  .popup-btn {{ padding:6px 10px;border-radius:7px;font-size:10px;font-weight:700; text-decoration:none;color:white;display:inline-flex;align-items:center;gap:4px; }}
  .pb-call{{ background:#16a34a; }}
  .pb-dir {{ background:#1d4ed8; }}
  .pb-wa  {{ background:#15803d; }}
  .popup-badge {{ display:inline-block;padding:2px 6px;border-radius:4px; font-size:8px;font-weight:700;margin:1px; }}
</style>
</head>
<body>

<div class="top-bar">
  <div>
    <div class="top-bar-title">🏥 CMR University (Lakeside Campus) — Emergency Hospital Locator</div>
    <div class="top-bar-sub">Real-time GPS · OpenStreetMap · Nearest oncology centres</div>
  </div>
  <div style="font-size:10px;color:rgba(255,255,255,0.4);text-align:right">
    🔴 Your Location &nbsp; 🟢 Government &nbsp; 🔵 Private &nbsp; 🟡 Oncology
  </div>
</div>

<div class="controls">
  <button class="btn btn-gps" onclick="locateMe()">📍 Use My Location (GPS)</button>
  <button class="btn btn-filter active" id="f-all" onclick="filterMap('all')">All</button>
  <button class="btn btn-filter" id="f-govt" onclick="filterMap('govt')">🟢 Government</button>
  <button class="btn btn-filter" id="f-pvt" onclick="filterMap('pvt')">🔵 Private</button>
  <button class="btn btn-filter" id="f-onco" onclick="filterMap('onco')">🟡 Oncology</button>
  <button class="btn btn-filter" id="f-near" onclick="showNearest()">📍 3 Nearest</button>
</div>

<div class="status-bar">
  <div class="status-dot"></div>
  <span id="statusText">Click 📍 Use My Location to find nearest hospitals automatically</span>
</div>

<div id="map"></div>

<script>
var map = L.map('map', {{
    center: [20, 79],
    zoom: 5,
    zoomControl: true,
}});

L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
}}).addTo(map);

var hospitals = {hosp_json};

function makeIcon(color, label) {{
    return L.divIcon({{
        className: '',
        html: `<div style="
            background:${{color}};
            width:32px;height:32px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;
            font-size:14px;border:3px solid white;
            box-shadow:0 4px 12px rgba(0,0,0,0.5);
            font-weight:900;color:white;
        ">${{label}}</div>`,
        iconSize: [32,32],
        iconAnchor: [16,16],
        popupAnchor: [0,-18],
    }});
}}

var iconMap = {{
    'govt': makeIcon('#22c55e', '🏥'),
    'pvt':  makeIcon('#3b82f6', '🏨'),
    'onco': makeIcon('#f59e0b', '🎗️'),
}};

var userIcon = L.divIcon({{
    className: '',
    html: `<div style="
        background:#ef4444;width:20px;height:20px;
        border-radius:50%;border:3px solid white;
        box-shadow:0 0 20px rgba(239,68,68,0.7);
        animation:userpulse 1.5s infinite;
    "></div>
    <style>@keyframes userpulse{{
        0%,100%{{box-shadow:0 0 20px rgba(239,68,68,0.7)}}
        50%{{box-shadow:0 0 40px rgba(239,68,68,1)}}
    }}</style>`,
    iconSize: [20,20],
    iconAnchor: [10,10],
    popupAnchor: [0,-15],
}});

function haversine(lat1, lon1, lat2, lon2) {{
    var R = 6371;
    var d = Math.PI / 180;
    var dlat = (lat2-lat1)*d, dlon = (lon2-lon1)*d;
    var a = Math.sin(dlat/2)**2 + Math.cos(lat1*d)*Math.cos(lat2*d)*Math.sin(dlon/2)**2;
    return R * 2 * Math.asin(Math.sqrt(a));
}}

function buildPopup(h, dist) {{
    var typeColor = h.type==='govt'?'#22c55e':h.type==='pvt'?'#3b82f6':'#f59e0b';
    var typeName  = h.type==='govt'?'Government':h.type==='pvt'?'Private Hospital':'Oncology Specialty';
    var distHtml  = dist!==null ? `<div class="popup-dist">${{dist.toFixed(1)}} km away</div>` : '';
    var dirLink   = userLat ?
        `https://www.google.com/maps/dir/${{userLat}},${{userLon}}/${{h.lat}},${{h.lon}}` :
        `https://www.google.com/maps/dir/Current+Location/${{h.lat}},${{h.lon}}`;
    var gmapLink  = `https://www.google.com/maps/search/${{encodeURIComponent(h.name)}}/@${{h.lat}},${{h.lon}},16z`;
    var waMsg = encodeURIComponent(
        "🚨 EMERGENCY — Onco AI CMR University Hospital (Lakeside Campus)\\nNearest Hospital: " + h.name +
        "\\nAddress: " + h.address + "\\nPhone: " + h.phone + "\\nArriving now — please keep oncology team ready."
    );
    var ayBadge = h.ayushman ? '<span class="popup-badge" style="background:#3b82f622;color:#93c5fd;border:1px solid #3b82f633">🇮🇳 Ayushman</span>' : '';
    var emgBadge = h.emergency ? '<span class="popup-badge" style="background:#ef444422;color:#fca5a5;border:1px solid #ef444433">🚨 24/7 Emergency</span>' : '';
    
    return `
    <div class="popup-name">${{h.name}}</div>
    <span class="popup-type" style="background:${{typeColor}}22;color:${{typeColor}};border:1px solid ${{typeColor}}44">${{typeName}}</span>
    ${{distHtml}}
    <div class="popup-meta">
        📍 ${{h.address}}<br>
        📞 ${{h.phone}}<br>
        🛏️ ${{h.beds}} beds &nbsp;·&nbsp; 🎗️ ${{h.speciality}}
    </div>
    <div style="margin-bottom:6px">${{emgBadge}} ${{ayBadge}}</div>
    <div class="popup-btns">
        <a href="tel:${{h.phone}}" class="popup-btn pb-call">📞 Call</a>
        <a href="${{dirLink}}" target="_blank" class="popup-btn pb-dir">🗺️ Directions</a>
        <a href="${{gmapLink}}" target="_blank" class="popup-btn pb-dir" style="background:#4338ca">📍 Maps</a>
        <a href="https://wa.me/?text=${{waMsg}}" target="_blank" class="popup-btn pb-wa">💚 WhatsApp</a>
    </div>`;
}}

var allMarkers = [];
var userLat = null, userLon = null, userMarker = null, userCircle = null;
var lineGroup = L.layerGroup().addTo(map);

hospitals.forEach(function(h) {{
    var marker = L.marker([h.lat, h.lon], {{icon: iconMap[h.type]}})
        .bindPopup(buildPopup(h, null), {{maxWidth:280}});
    marker._hospitalData = h;
    marker._type = h.type;
    marker.addTo(map);
    allMarkers.push(marker);
}});

function drawRouteLine(toLat, toLon, color) {{
    L.polyline([[userLat, userLon], [toLat, toLon]], {{
        color: color,
        weight: 4,
        opacity: 0.9,
        dashArray: '7,5'
    }}).addTo(lineGroup);
}}

function locateMe() {{
    document.getElementById('statusText').textContent = '📡 Detecting your GPS location...';
    
    if (!navigator.geolocation) {{
        document.getElementById('statusText').textContent = '❌ GPS not available in this browser.';
        return;
    }}
    
    navigator.geolocation.getCurrentPosition(function(pos) {{
        userLat = pos.coords.latitude;
        userLon = pos.coords.longitude;
        
        if(userMarker) map.removeLayer(userMarker);
        if(userCircle) map.removeLayer(userCircle);
        lineGroup.clearLayers();
        
        userMarker = L.marker([userLat, userLon], {{icon: userIcon}})
            .bindPopup('<b style="color:#ef4444">📍 Your Location</b><br>' + userLat.toFixed(5) + ', ' + userLon.toFixed(5))
            .addTo(map);
        
        userCircle = L.circle([userLat, userLon], {{
            radius: pos.coords.accuracy || 200,
            color: '#ef4444',
            fillColor: '#ef4444',
            fillOpacity: 0.06,
            weight: 2,
        }}).addTo(map);
        
        var withDist = hospitals.map(function(h) {{
            return Object.assign({{}}, h, {{dist: haversine(userLat, userLon, h.lat, h.lon)}});
        }});
        withDist.sort(function(a,b){{return a.dist-b.dist;}});
        
        allMarkers.forEach(function(m) {{
            var h = m._hospitalData;
            var d = haversine(userLat, userLon, h.lat, h.lon);
            m._dist = d;
            m.setPopupContent(buildPopup(h, d));
        }});
        
        withDist.slice(0,5).forEach(function(h,i) {{
            var color = i===0 ? '#ef4444' : i===1 ? '#f59e0b' : '#60a5fa';
            drawRouteLine(h.lat, h.lon, color);
        }});
        
        var pts = [[userLat, userLon]];
        withDist.slice(0,3).forEach(function(h){{ pts.push([h.lat, h.lon]); }});
        map.fitBounds(pts, {{padding:[40,40]}});
        
        var nearest = withDist[0];
        allMarkers.forEach(function(m) {{
            if(m._hospitalData.name === nearest.name) {{
                m.openPopup();
            }}
        }});
        
        document.getElementById('statusText').textContent =
            '✅ Located! Nearest: ' + nearest.name + ' — ' + nearest.dist.toFixed(1) + ' km away | Tap 🗺️ Directions for route | ' +
            withDist.slice(0,5).map(function(h){{return h.name.split(' ')[0]+' ('+h.dist.toFixed(1)+'km)'}}).join(' · ');
    }}, function(err) {{
        var msgs = {{
            1: 'Location permission denied. Please allow location access in browser settings.',
            2: 'GPS position unavailable. Try again or enter coordinates manually.',
            3: 'GPS timeout. Check your internet connection and try again.',
        }};
        document.getElementById('statusText').textContent = '❌ ' + (msgs[err.code] || 'GPS Error. Try again.');
    }}, {{
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0,
    }});
}}

var activeFilter = 'all';
function filterMap(type) {{
    activeFilter = type;
    ['all','govt','pvt','onco','near'].forEach(function(t){{
        var el = document.getElementById('f-'+t);
        if(el) el.classList.remove('active');
    }});
    var el2 = document.getElementById('f-'+type);
    if(el2) el2.classList.add('active');
    
    allMarkers.forEach(function(m) {{
        if(type==='all' || m._type===type) {{
            if(!map.hasLayer(m)) m.addTo(map);
        }} else {{
            if(map.hasLayer(m)) map.removeLayer(m);
        }}
    }});
    document.getElementById('statusText').textContent =
        type==='all' ? 'Showing all hospitals.' : 'Filtered: '+type+' hospitals only.';
}}

function showNearest() {{
    if(!userLat) {{
        locateMe();
        return;
    }}
    ['all','govt','pvt','onco','near'].forEach(function(t){{
        var el = document.getElementById('f-'+t);
        if(el) el.classList.remove('active');
    }});
    document.getElementById('f-near').classList.add('active');
    
    var sorted = allMarkers.slice().sort(function(a,b){{
        return (a._dist||999)-(b._dist||999);
    }});
    
    allMarkers.forEach(function(m){{ if(map.hasLayer(m)) map.removeLayer(m); }});
    sorted.slice(0,3).forEach(function(m){{ m.addTo(map); m.openPopup(); }});
    document.getElementById('statusText').textContent = '📍 Showing 3 nearest hospitals to your location.';
}}

document.getElementById('statusText').textContent =
    'Showing ' + hospitals.length + ' cancer hospitals across India. Click 📍 Use My Location for nearest hospitals.';
</script>
</body>
</html>
"""

components.html(MAP_HTML, height=600)

st.markdown("---")
st.markdown("### 🏥 Browse Hospitals by City")

cities = sorted(list(set(h['city'] for h in HOSPITALS)))
sel_city = st.selectbox("Select City:", cities, index=cities.index("Bengaluru"))

df_h = pd.DataFrame(HOSPITALS)
df_city = df_h[df_h['city'] == sel_city].reset_index(drop=True)

if sel_city == "Bengaluru":
    ref_lat, ref_lon = 13.1880, 77.6510
else:
    city_coords = df_city.iloc[0][['lat','lon']].values if not df_city.empty else [12.97, 77.59]
    ref_lat, ref_lon = float(city_coords[0]), float(city_coords[1])

df_city['dist'] = df_city.apply(lambda r: haversine(ref_lat, ref_lon, r['lat'], r['lon']), axis=1)
df_city = df_city.sort_values('dist').reset_index(drop=True)

for rank, (_, h) in enumerate(df_city.iterrows()):
    t = h['type']
    tc = {'govt':'#22c55e','pvt':'#60a5fa','onco':'#f59e0b'}.get(t,'#818cf8')
    tl = {'govt':'Government','pvt':'Private Hospital','onco':'Oncology Specialty'}.get(t,'Hospital')
    nearest = '<span class="nearest-tag">⭐ NEAREST</span>' if rank==0 else ""
    ay_badge = '<span class="badge badge-ay">🇮🇳 Ayushman Bharat</span>' if h['ayushman'] else ""
    emg_badge = '<span class="badge badge-emg">🚨 24/7 Emergency</span>'
    dir_link = gdir(ref_lat, ref_lon, h['lat'], h['lon'])
    map_link = gmap(h['lat'], h['lon'], h['name'])
    wa_link = wa_msg(h, pat_name)

    st.markdown(f"""
    <div class="hcard hcard-{t}">
      <div style="float:right;text-align:right">
        <div class="hcard-dist">{h.get('dist',0):.1f}</div>
        <div class="hcard-dist-lbl">km from city centre</div>
        <div style="font-size:11px;color:{tc};font-weight:700;margin-top:4px">● {tl}</div>
      </div>
      <div class="hcard-name">{h['name']}{nearest}</div>
      <div class="hcard-meta">
        📍 {h['address']}<br>
        📞 {h['phone']} &nbsp;&nbsp;·&nbsp;&nbsp; 🛏️ {h['beds']} beds<br>
        🎗️ {h['speciality']}
      </div>
      <div style="margin-top:7px">{emg_badge} {ay_badge}</div>
      <div class="hcard-btns">
        <a href="tel:{h['phone']}" class="hbtn hbtn-call">📞 Call Now</a>
        <a href="{dir_link}" target="_blank" class="hbtn hbtn-dir">🗺️ Get Directions</a>
        <a href="{map_link}" target="_blank" class="hbtn hbtn-map">📍 View on Google Maps</a>
        <a href="{wa_link}" target="_blank" class="hbtn hbtn-wa">💚 WhatsApp Alert</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 🚑 What to Do in a Breast Cancer Emergency")

TIPS = [
    ("🚨 Sudden rapidly growing or painful lump",
     "Call 108 immediately. Do NOT massage or apply heat. Lie down, stay calm. Carry all medical records including your Onco AI PDF report. Mention 'breast emergency' to ER staff."),
    ("🩸 Nipple discharge with blood",
     "Go to oncology emergency immediately. Do NOT press the breast. Note exact onset time. Call ahead — tell hospital 'possible ductal carcinoma emergency'. Bring your Onco AI report showing previous scans."),
    ("🌡️ Fever during chemotherapy (Neutropenic Fever)",
     "LIFE THREATENING. Temperature ≥38°C during chemo = call 108 immediately. Neutropenic sepsis can be fatal within hours. Tell ER: your chemo drug, last dose date, cycle number."),
    ("📋 How your Onco AI report helps in emergency",
     "Download the PDF from 'Download Report' page before going to ER. It contains: Patient ID, AI result, BIRADS score, confidence %, GradCAM image, doctor notes, and complete visit history."),
    ("💊 Missed chemotherapy or medication",
     "Call your oncologist immediately — do NOT double dose. Use Onco AI Treatment Tracker to show your current medication schedule. Emergency helpline: 104 (National Health Helpline)."),
]

for title, body in TIPS:
    st.markdown(f"""
    <div class="tip-box">
      <div class="tip-title">{title}</div>
      <div class="tip-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)

log_audit("EMERGENCY_LOCATOR", "user", f"Emergency locator accessed — {sel_city}")

st.markdown("---")
st.caption("""
🏥 **CMR University Hospital** — Bengaluru 562149 · 📞 9342900666  
**Onco AI Emergency Locator — First-ever AI breast cancer system with live GPS hospital finder in India.**  
Built by CMR University (Lakeside Campus) Final Year Students — 2026 Batch.
""")