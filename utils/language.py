# utils/language.py  ← FINAL GLOBAL PRO VERSION

import streamlit as st

# ─────────────────────────────────────────────────────────────
# 🌐 SUPPORTED LANGUAGES
# ─────────────────────────────────────────────────────────────
LANGUAGES = ["English", "Hindi", "Telugu", "Tamil", "Kannada"]

DEFAULT_LANG = "English"


# ─────────────────────────────────────────────────────────────
# 🌍 TRANSLATION DICTIONARY
# ─────────────────────────────────────────────────────────────
T = {

# ── APP ──────────────────────────────────────────────────────
"app_title": {
    "English": "Onco Breast Cancer Detection System",
    "Hindi": "ओंको स्तन कैंसर पहचान प्रणाली",
    "Telugu": "ఓంకో స్తన క్యాన్సర్ గుర్తింపు వ్యవస్థ",
    "Tamil": "ஓங்கோ மார்பக புற்றுநோய் கண்டறிதல்",
    "Kannada": "ಓಂಕೋ ಸ್ತನ ಕ್ಯಾನ್ಸರ್ ಪತ್ತೆ ವ್ಯವಸ್ಥೆ"
},

"app_subtitle": {
    "English": "AI Powered Medical Diagnosis Platform",
    "Hindi": "AI संचालित चिकित्सा निदान मंच",
    "Telugu": "AI ఆధారిత వైద్య నిర్ధారణ వేదిక",
    "Tamil": "AI இயங்கும் மருத்துவ நோயறிதல் தளம்",
    "Kannada": "AI ಚಾಲಿತ ವೈದ್ಯಕೀಯ ರೋಗನಿರ್ಣಯ ವೇದಿಕೆ"
},

"please_login": {
    "English": "Please login from sidebar — Use admin / admin",
    "Hindi": "कृपया साइडबार से लॉगिन करें — admin / admin",
    "Telugu": "దయచేసి లాగిన్ చేయండి — admin / admin",
    "Tamil": "உள்நுழையவும் — admin / admin",
    "Kannada": "ಲಾಗಿನ್ ಮಾಡಿ — admin / admin"
},

# ── NAV (Same as yours — cleaned Telugu + consistency) ───────
"nav_app": {"English":"🏠 Home","Hindi":"🏠 होम","Telugu":"🏠 హోమ్","Tamil":"🏠 முகப்பு","Kannada":"🏠 ಮನೆ"},
"nav_dashboard":{"English":"🏥 Dashboard","Hindi":"🏥 डैशबोर्ड","Telugu":"🏥 డాష్‌బోర్డ్","Tamil":"🏥 டாஷ்போர்டு","Kannada":"🏥 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್"},
"nav_login":{"English":"🔐 Login","Hindi":"🔐 लॉगिन","Telugu":"🔐 లాగిన్","Tamil":"🔐 உள்நுழைவு","Kannada":"🔐 ಲಾಗಿನ್"},

# PATIENT
"nav_register":{"English":"👤 Patient Register","Hindi":"👤 मरीज पंजीकरण","Telugu":"👤 రోగి నమోదు","Tamil":"👤 நோயாளி பதிவு","Kannada":"👤 ರೋಗಿ ನೋಂದಣಿ"},
"nav_search":{"English":"🔍 Patient Search","Hindi":"🔍 मरीज खोज","Telugu":"🔍 రోగి వెతుకులాట","Tamil":"🔍 நோயாளி தேடல்","Kannada":"🔍 ರೋಗಿ ಹುಡುಕಾಟ"},
"nav_today":{"English":"📋 Today's Patients","Hindi":"📋 आज के मरीज","Telugu":"📋 నేటి రోగులు","Tamil":"📋 இன்றைய நோயாளிகள்","Kannada":"📋 ಇಂದಿನ ರೋಗಿಗಳು"},
"nav_history":{"English":"📜 History","Hindi":"📜 इतिहास","Telugu":"📜 చరిత్ర","Tamil":"📜 வரலாறு","Kannada":"📜 ಇತಿಹಾಸ"},
"nav_timeline":{"English":"📅 Patient Timeline","Hindi":"📅 मरीज समयरेखा","Telugu":"📅 రోగి టైమ్‌లైన్","Tamil":"📅 காலவரிசை","Kannada":"📅 ಟೈಮ್‌ಲೈನ್"},
"nav_portal":{"English":"🧑 Patient Portal","Hindi":"🧑 मरीज पोर्टल","Telugu":"🧑 రోగి పోర్టల్","Tamil":"🧑 நோயாளி போர்டல்","Kannada":"🧑 ರೋಗಿ ಪೋರ್ಟಲ್"},

# AI
"nav_prediction":{"English":"🤖 AI Prediction","Hindi":"🤖 AI भविष्यवाणी","Telugu":"🤖 AI అంచనా","Tamil":"🤖 AI கணிப்பு","Kannada":"🤖 AI ಭವಿಷ್ಯ"},
"nav_explain":{"English":"🔥 AI Explainability","Hindi":"🔥 AI व्याख्या","Telugu":"🔥 AI వివరణ","Tamil":"🔥 AI விளக்கம்","Kannada":"🔥 AI ವಿವರಣೆ"},
"nav_second_opinion":{"English":"🔬 AI Second Opinion","Hindi":"🔬 AI दूसरी राय","Telugu":"🔬 AI రెండవ అభిప్రాయం","Tamil":"🔬 AI இரண்டாவது கருத்து","Kannada":"🔬 AI ಎರಡನೇ ಅಭಿಪ್ರಾಯ"},
"nav_compare":{"English":"🔄 Compare Reports","Hindi":"🔄 रिपोर्ट तुलना","Telugu":"🔄 నివేదికలు పోల్చు","Tamil":"🔄 அறிக்கை ஒப்பிடு","Kannada":"🔄 ವರದಿ ಹೋಲಿಕೆ"},

# CLINICAL
"nav_risk":{"English":"⚠️ Risk Assessment","Hindi":"⚠️ जोखिम मूल्यांकन","Telugu":"⚠️ ప్రమాద మూల్యాంకనం","Tamil":"⚠️ ஆபத்து மதிப்பீடு","Kannada":"⚠️ ಅಪಾಯ ಮೌಲ್ಯಮಾಪನ"},
"nav_symptoms":{"English":"🩺 Symptoms Checker","Hindi":"🩺 लक्षण जांचकर्ता","Telugu":"🩺 లక్షణాలు చెక్","Tamil":"🩺 அறிகுறி சரிபார்","Kannada":"🩺 ರೋಗಲಕ್ಷಣ ಪರಿಶೀಲಕ"},
"nav_imaging":{"English":"📡 Imaging Guide","Hindi":"📡 इमेजिंग गाइड","Telugu":"📡 ఇమేజింగ్ గైడ్","Tamil":"📡 படமெடுப்பு","Kannada":"📡 ಇಮೇಜಿಂಗ್ ಮಾರ್ಗದರ್ಶಿ"},
"nav_staging":{"English":"🔬 AI Cancer Staging","Hindi":"🔬 AI कैंसर स्टेजिंग","Telugu":"🔬 AI క్యాన్సర్ స్టేజింగ్","Tamil":"🔬 AI நிலை","Kannada":"🔬 AI ಕ್ಯಾನ್ಸರ್ ಸ್ಟೇಜಿಂಗ್"},
"nav_doctor_notes":{"English":"📝 Doctor Notes","Hindi":"📝 डॉक्टर नोट्स","Telugu":"📝 డాక్టర్ నోట్స్","Tamil":"📝 மருத்துவர் குறிப்பு","Kannada":"📝 ವೈದ್ಯರ ಟಿಪ್ಪಣಿ"},
"nav_chatbot":{"English":"💬 AI Chatbot","Hindi":"💬 AI चैटबॉट","Telugu":"💬 AI చాట్‌బాట్","Tamil":"💬 AI அரட்டை","Kannada":"💬 AI ಚಾಟ್‌ಬಾಟ್"},

# EMERGENCY (IMPORTANT)
"nav_emergency":{"English":"🚨 Emergency Locator","Hindi":"🚨 आपातकाल लोकेटर","Telugu":"🚨 అత్యవసర లొకేటర్","Tamil":"🚨 அவசரம் கண்டுபிடி","Kannada":"🚨 ತುರ್ತು ಪತ್ತೆ"},

# LOGIN
"login":{"English":"Login","Hindi":"लॉगिन","Telugu":"లాగిన్","Tamil":"உள்நுழை","Kannada":"ಲಾಗಿನ್"},
"username":{"English":"Username","Hindi":"यूज़र","Telugu":"వినియోగదారు పేరు","Tamil":"பயனர்","Kannada":"ಬಳಕೆದಾರ"},
"password":{"English":"Password","Hindi":"पासवर्ड","Telugu":"పాస్‌వర్డ్","Tamil":"கடவுச்சொல்","Kannada":"ಪಾಸ್ವರ್ಡ್"},

# STATUS
"system_running":{
    "English":"✅ System Running Successfully",
    "Hindi":"✅ सिस्टम चालू है",
    "Telugu":"✅ సిస్టమ్ నడుస్తోంది",
    "Tamil":"✅ அமைப்பு இயங்குகிறது",
    "Kannada":"✅ ವ್ಯವಸ್ಥೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತಿದೆ"
}

}


# ─────────────────────────────────────────────────────────────
# ⚙️ CORE FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_current_language():
    """Get language globally from session"""
    return st.session_state.get("app_language", DEFAULT_LANG)


def set_language(lang: str):
    """Set language globally"""
    if lang in LANGUAGES:
        st.session_state["app_language"] = lang


def get_text(key: str, lang: str = None) -> str:
    """Fetch translated text safely"""
    if lang is None:
        lang = get_current_language()

    row = T.get(key)

    if not row:
        return key  # fallback if missing

    return row.get(lang) or row.get(DEFAULT_LANG) or key


def get_all_texts(lang: str = None) -> dict:
    """Get all translations for current language"""
    if lang is None:
        lang = get_current_language()

    return {k: get_text(k, lang) for k in T}