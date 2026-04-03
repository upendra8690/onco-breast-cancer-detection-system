# pages/2_AI_Prediction.py

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import sqlite3
import tensorflow as tf
from ai.predict import predict
from ai.gradcam import gradcam, overlay_heatmap
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar

check_login()
lang = render_sidebar()

# ===== MEDICAL HEADER =====
st.markdown("""
<div style="background:#0f172a;padding:15px;border-radius:12px">
<h2 style="color:white;margin:0">🏥 CMR University Hospital</h2>
<p style="color:#94a3b8;margin:0">AI Breast Cancer Detection System</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🤖 AI Clinical Prediction")

# ===== INPUT =====
patient_id = st.text_input("🆔 Patient ID")
uploaded = st.file_uploader("📤 Upload Ultrasound Image", type=["png","jpg","jpeg"])

# ===== IMAGE =====
if uploaded:
    raw_bytes = uploaded.read()
    file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    st.image(image, caption="🖼 Ultrasound Scan", use_column_width=True)

    if st.button("🚀 Analyze with AI", use_container_width=True):

        # ===== AI PREDICTION =====
        with st.spinner("Analyzing..."):
            label, confidence, probs = predict(image)

        # ===== RISK LEVEL =====
        if confidence > 80 and label == "Malignant":
            risk = "HIGH RISK"
            risk_color = "#ef4444"
        elif label == "Benign":
            risk = "LOW RISK"
            risk_color = "#22c55e"
        else:
            risk = "MEDIUM RISK"
            risk_color = "#f59e0b"

        # ===== RESULT CARD =====
        st.markdown(f"""
        <div style="background:#1e293b;padding:20px;border-radius:15px;
        border-left:6px solid {risk_color}">
        <h3 style="margin:0">{label}</h3>
        <p>Confidence: {confidence:.2f}%</p>
        <p style="color:{risk_color};font-weight:bold">{risk}</p>
        </div>
        """, unsafe_allow_html=True)

        # ===== PROGRESS =====
        st.progress(int(confidence))

        # ===== PROBABILITY CHART =====
        classes = ["Benign","Malignant","Normal"]
        df = pd.DataFrame({"Class": classes, "Probability": probs})
        st.bar_chart(df.set_index("Class"))

        # ===== GRADCAM =====
        with st.spinner("Generating Heatmap..."):
            try:
                model = tf.keras.models.load_model("models/cnn_model.h5")
                img_r = cv2.resize(image, (224,224))
                img_n = img_r / 255.0
                img_e = np.expand_dims(img_n, 0)
                heatmap = gradcam(model, img_e, "conv2d_2")
                cam = overlay_heatmap(heatmap, image)
            except:
                cam = image

        col1, col2 = st.columns(2)

        with col1:
            st.image(image, caption="Original Scan")

        with col2:
            st.image(cam, caption="AI Attention (GradCAM)")

        # ===== AI INTERPRETATION =====
        if label == "Malignant":
            interpretation = "Irregular mass detected with high suspicion of malignancy."
            suggestion = "Immediate biopsy and oncologist consultation recommended."
        elif label == "Benign":
            interpretation = "Well-defined structure suggests non-cancerous tissue."
            suggestion = "Routine monitoring advised."
        else:
            interpretation = "No significant abnormality detected."
            suggestion = "Maintain regular screening."

        st.markdown("### 🧠 AI Clinical Interpretation")
        st.info(interpretation)

        st.markdown("### 📌 Recommendation")
        st.success(suggestion)

        # ===== SAVE TO DB =====
        _, us_enc = cv2.imencode('.png', image)
        _, gcam_enc = cv2.imencode('.png', cam)

        conn = connect()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO diagnosis(patient_id, result, confidence, created, ultrasound_img, gradcam_img)
        VALUES(?,?,?,?,?,?)
        """, (patient_id, label, confidence, get_ist_time(),
              sqlite3.Binary(us_enc.tobytes()),
              sqlite3.Binary(gcam_enc.tobytes())))

        conn.commit()
        conn.close()

        log_audit("AI_PREDICTION", "doctor", f"{patient_id}: {label}")

        st.success("✅ Diagnosis saved")

        # ===== DOWNLOAD REPORT =====
        if st.button("📄 Download Clinical Report", use_container_width=True):
            from utils.report_generator import generate_report

            file = generate_report(
                patient_id,
                ultrasound_img_bytes=us_enc.tobytes(),
                gradcam_img_bytes=gcam_enc.tobytes()
            )

            if file:
                with open(file, "rb") as f:
                    st.download_button(
                        "⬇ Download PDF Report",
                        data=f,
                        file_name=file,
                        mime="application/pdf",
                        use_container_width=True
                    )

        # ===== DISCLAIMER =====
        st.markdown("""
        <div style="background:#facc15;color:black;padding:10px;border-radius:10px">
        ⚕️ AI is assistive only. Final diagnosis must be done by certified medical professionals.
        </div>
        """, unsafe_allow_html=True)