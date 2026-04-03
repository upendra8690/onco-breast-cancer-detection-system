# utils/sidebar.py  ← FINAL PRO VERSION (GLOBAL LEVEL UI)

import streamlit as st
from utils.language import LANGUAGES, get_text

def render_sidebar() -> str:

    # ────────────────────────────────────────────────────────────
    # 🎨 ULTRA CLEAN SIDEBAR UI (GLOBAL STANDARD DESIGN)
    # ────────────────────────────────────────────────────────────
    st.markdown("""
    <style>

    /* Hide default Streamlit navigation completely */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }

    /* Sidebar main container */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050a18, #0b1228);
        padding-top: 10px;
    }

    /* Sidebar scrollbar */
    section[data-testid="stSidebar"]::-webkit-scrollbar {
        width: 4px;
    }
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: #1f2a44;
        border-radius: 10px;
    }

    /* Links */
    section[data-testid="stSidebar"] a {
        color: #c7d2fe !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        padding: 6px 10px !important;
        margin: 2px 0 !important;
        display: block !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] a:hover {
        background: rgba(99,102,241,0.15);
        color: #ffffff !important;
        transform: translateX(3px);
    }

    /* Section divider */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08);
        margin: 8px 0;
    }

    /* Title branding */
    .brand-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .brand-sub {
        font-size: 11px;
        color: #94a3b8;
        margin-bottom: 10px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────
    # 🏥 BRAND HEADER
    # ────────────────────────────────────────────────────────────
    st.sidebar.markdown("""
    <div class="brand-title">🏥 ONCO AI v2.0</div>
    <div class="brand-sub">CMR University · 2026 Batch</div>
    """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────
    # 🌐 LANGUAGE SELECTOR
    # ────────────────────────────────────────────────────────────
    if "app_language" not in st.session_state:
        st.session_state["app_language"] = "English"

    idx = LANGUAGES.index(st.session_state["app_language"]) \
        if st.session_state["app_language"] in LANGUAGES else 0

    lang = st.sidebar.selectbox(
        "🌐 Language",
        LANGUAGES,
        index=idx,
        key="global_lang"
    )

    if lang != st.session_state["app_language"]:
        st.session_state["app_language"] = lang
        st.rerun()

    # ────────────────────────────────────────────────────────────
    # 🔗 SAFE PAGE LINK FUNCTION
    # ────────────────────────────────────────────────────────────
    def lnk(key: str, page: str):
        try:
            st.sidebar.page_link(page, label=get_text(key, lang))
        except Exception:
            pass

    # ────────────────────────────────────────────────────────────
    # 📊 NAVIGATION GROUPS
    # ────────────────────────────────────────────────────────────

    st.sidebar.markdown("---")
    st.sidebar.caption("🏠 MAIN")
    lnk("nav_app", "app.py")
    lnk("nav_dashboard", "pages/0_Dashboard.py")
    lnk("nav_login", "pages/00_Login.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("👤 PATIENT")
    lnk("nav_register", "pages/1_Patient_Register.py")
    lnk("nav_search", "pages/3_Patient_Search.py")
    lnk("nav_today", "pages/4_Today_List.py")
    lnk("nav_history", "pages/5_History.py")
    lnk("nav_timeline", "pages/12_Patient_Timeline.py")
    lnk("nav_portal", "pages/29_Patient_Portal.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("🤖 AI SYSTEM")
    lnk("nav_prediction", "pages/2_AI_Prediction.py")
    lnk("nav_explain", "pages/8_AI_Explainability.py")
    lnk("nav_second_opinion", "pages/19_AI_Second_Opinion.py")
    lnk("nav_compare", "pages/30_Compare_Reports.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("🩺 CLINICAL")
    lnk("nav_risk", "pages/16_Risk_Assessment.py")
    lnk("nav_symptoms", "pages/14_Symptoms_Checker.py")
    lnk("nav_imaging", "pages/15_Imaging_Guide.py")
    lnk("nav_staging", "pages/35_AI_Cancer_Staging.py")
    lnk("nav_doctor_notes", "pages/17_Doctor_Notes.py")
    lnk("nav_chatbot", "pages/21_AI_Chatbot.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("🏥 OPERATIONS")
    lnk("nav_opd", "pages/31_OPD_Queue.py")
    lnk("nav_treatment", "pages/32_Treatment_Tracker.py")
    lnk("nav_report", "pages/13_Download_Report.py")
    lnk("nav_notif", "pages/34_Notification_Center.py")
    lnk("nav_live", "pages/36_Live_Monitoring.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("📡 COMMUNICATION")
    lnk("nav_email", "pages/27_Send_Email.py")
    lnk("nav_sms", "pages/28_SMS_WhatsApp.py")
    lnk("nav_telemedicine", "pages/22_Telemedicine.py")
    lnk("nav_qr", "pages/26_QR_Login.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("📊 RESEARCH")
    lnk("nav_model_eval", "pages/6_Model_Evaluation.py")
    lnk("nav_dataset", "pages/7_Dataset_Statistics.py")
    lnk("nav_experiments", "pages/9_Experiments.py")
    lnk("nav_analytics", "pages/20_Population_Analytics.py")
    lnk("nav_benchmark", "pages/25_Research_Benchmark.py")
    lnk("nav_export", "pages/24_Export_Data.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("🔐 ADMIN")
    lnk("nav_users", "pages/10_User_Management.py")
    lnk("nav_delete", "pages/11_Delete_Patient.py")
    lnk("nav_audit", "pages/18_Audit_Log.py")
    lnk("nav_consent", "pages/23_Digital_Consent.py")
    lnk("nav_gov", "pages/33_Government_Reports.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("🚨 EMERGENCY")
    lnk("nav_emergency", "pages/43_Emergency_Locator.py")

    st.sidebar.markdown("---")
    st.sidebar.caption("🚀 FUTURE AI")
    lnk("nav_voice", "pages/37_AI_Voice_Assistant.py")
    lnk("nav_federated", "pages/38_Federated_Learning.py")
    lnk("nav_genomics", "pages/39_Genomics_AI.py")
    lnk("nav_drug", "pages/40_Drug_Interaction.py")
    lnk("nav_wearables", "pages/41_Patient_Wearables.py")
    lnk("nav_roadmap", "pages/42_Future_Roadmap.py")

    # ────────────────────────────────────────────────────────────
    # 🎯 FOOTER (UPDATED WITH TEAM DETAILS)
    # ────────────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "🏥 CMR University Bengaluru\n"
        "Lakeside Campus — 562149\n\n"
        "👨‍💻 Developed By:\n"
        "Upendra · Nivi · Mounika · Nayana\n\n"
        "👩‍🏫 Project Guide:\n"
        "Prof. Rajani Kodagali\n\n"
        "🚀 Built by Final Year Students (2026 Batch)\n"
        "🌍 Designed for Global Healthcare Impact\n\n"
        "🔬 Onco AI v2.0\n"
        "© 2026"
    )

    return lang