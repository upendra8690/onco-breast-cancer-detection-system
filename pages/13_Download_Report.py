# pages/13_Download_Report.py

import streamlit as st
import sqlite3
import os
from auth.guard import check_login
from utils.report_generator import generate_report
from utils.sidebar import render_sidebar
from utils.language import get_text
from database.database import connect

check_login()
lang = render_sidebar()

# ===== HEADER WITH LOGO (SAFE VERSION) =====
col1, col2 = st.columns([1, 6])

with col1:
    logo_path = "assets/logo.png"
    
    if os.path.exists(logo_path):
        st.image(logo_path, width=80)
    else:
        st.warning("⚠️ Logo not found. Put logo.png inside assets folder")

with col2:
    st.markdown("""
    <h2 style='margin-bottom:0;'>CMR University Hospital</h2>
    <p style='margin-top:0; font-size:14px;'>
    Onco AI Breast Cancer Detection System | AI-Powered Medical Diagnosis<br>
    📍 CMR University, Bengaluru – 562149 &nbsp;&nbsp;&nbsp; 📞 9342900666<br>
    🌐 www.cmruniversity.edu.in &nbsp;&nbsp;&nbsp; ✉️ onco@cmruniversity.edu.in
    </p>
    """, unsafe_allow_html=True)

st.markdown("---")

# ===== EXISTING CODE (UNCHANGED) =====
st.title(f"📄 {get_text('download_report', lang)}")
st.write("Generate a professional hospital-style PDF report with ultrasound images, GradCAM, diagnosis history, risk assessment, and doctor notes.")

patient_id = st.text_input(get_text("patient_id", lang))

# Show what's available for this patient
if patient_id:
    conn = connect()
    cur  = conn.cursor()
    cur.execute("SELECT id, result, confidence, created FROM diagnosis WHERE patient_id=? ORDER BY created DESC LIMIT 1",
                (patient_id,))
    latest_dx = cur.fetchone()
    conn.close()

    if latest_dx:
        result     = latest_dx[1]
        res_icon   = "🔴" if result=="Malignant" else ("🟢" if result=="Benign" else "🔵")
        st.info(f"{res_icon} Latest diagnosis: **{result}** ({latest_dx[2]:.1f}%) on {str(latest_dx[3])[:16]}")

st.markdown("""
**This report includes:**
- ✅ CMR University Hospital header with phone & address
- ✅ Patient Information with QR verification code  
- ✅ Uploaded Ultrasound Image + GradCAM Heatmap
- ✅ AI Impression & Suggestion (like Drlogy format)
- ✅ All Diagnosis Visits history table
- ✅ AI Confidence Trend Chart
- ✅ Risk Assessment
- ✅ Doctor Notes & Recommendations
- ✅ 3 Signature blocks (Lab Technician, Radiologist, Oncologist)
""")

if st.button(f"📋 {get_text('generate_report', lang)}", type="primary", use_container_width=True):
    if not patient_id:
        st.warning("Please enter a Patient ID")
    else:
        # Fetch latest images from database
        us_bytes   = None
        gcam_bytes = None
        try:
            conn = connect()
            cur  = conn.cursor()
            cur.execute("""
                SELECT ultrasound_img, gradcam_img FROM diagnosis
                WHERE patient_id=? AND ultrasound_img IS NOT NULL
                ORDER BY created DESC LIMIT 1
            """, (patient_id,))
            img_row = cur.fetchone()
            conn.close()
            if img_row:
                us_bytes   = bytes(img_row[0]) if img_row[0] else None
                gcam_bytes = bytes(img_row[1]) if img_row[1] else None
        except Exception as e:
            st.warning(f"Note: Could not load stored images ({e}). Report will be generated without images.")

        with st.spinner("Generating hospital-style PDF report..."):
            file = generate_report(
                patient_id,
                lang,
                ultrasound_img_bytes=us_bytes,
                gradcam_img_bytes=gcam_bytes
            )

        if file is None:
            st.error("Patient not found in database.")
        else:
            with open(file, "rb") as f:
                st.download_button(
                    label="⬇️ Download Report PDF",
                    data=f,
                    file_name=file,
                    mime="application/pdf",
                    use_container_width=True
                )
            if us_bytes:
                st.success("✅ Report generated with ultrasound images!")
            else:
                st.success("✅ Report generated! Run AI Prediction first to include ultrasound images.")