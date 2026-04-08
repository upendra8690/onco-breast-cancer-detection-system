# pages/2_AI_Prediction.py  ← STREAMLIT CLOUD COMPATIBLE
# Onco AI — CMR University Bengaluru 2026
# Developer: Mopuru Upendra Reddy

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import sqlite3

# ── Safe TensorFlow import (works on Streamlit Cloud) ─────────────
TF_AVAILABLE = False
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except Exception:
    pass

from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"🤖 {get_text('ai_prediction', lang)}")

# ── Cloud notice if TF not loaded ──────────────────────────────────
if not TF_AVAILABLE:
    st.warning("""
    ⚠️ **Running in Demo Mode** — TensorFlow model is not loaded on this cloud instance.
    
    For **full AI prediction** with your real trained model:
    - Run the app **locally** on your computer (`streamlit run app.py`)
    - Or purchase the **Full Version** — includes setup support
    
    📧 upendra8680@gmail.com | 💚 WhatsApp: 8639897710
    """)

patient_id = st.text_input(get_text("patient_id", lang), placeholder="e.g. P101, 1, 2...")
uploaded   = st.file_uploader(get_text("upload_image", lang), type=["png","jpg","jpeg"])

if uploaded:
    raw_bytes  = uploaded.read()
    file_bytes = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
    image      = cv2.imdecode(file_bytes, 1)
    if image is not None:
        st.image(image, caption="Uploaded Ultrasound Image", use_column_width=True)

    if st.button(get_text("run_prediction", lang), type="primary"):
        if not patient_id:
            st.warning("Please enter a Patient ID first.")
            st.stop()

        # ── Try real model, fall back to demo ─────────────────────
        if TF_AVAILABLE:
            try:
                from ai.predict import predict
                from ai.gradcam import gradcam, overlay_heatmap
                with st.spinner("Running AI Prediction..."):
                    label, confidence, probs = predict(image)
                model_mode = "real"
            except Exception as e:
                st.warning(f"Model error: {e} — Using demo mode.")
                model_mode = "demo"
        else:
            model_mode = "demo"

        if model_mode == "demo":
            # Demo mode — realistic simulation for Streamlit Cloud
            import hashlib
            seed = int(hashlib.md5(raw_bytes[:100]).hexdigest(), 16) % 100
            if seed < 40:
                label, confidence = "Benign", 92.5 + (seed % 7)
            elif seed < 65:
                label, confidence = "Malignant", 78.3 + (seed % 12)
            else:
                label, confidence = "Normal", 96.1 + (seed % 4)
            probs = {
                "Benign":   [0.85,0.08,0.07][["Benign","Malignant","Normal"].index(label)],
                "Malignant":[0.08,0.85,0.07][["Benign","Malignant","Normal"].index(label)],
                "Normal":   [0.07,0.08,0.85][["Benign","Malignant","Normal"].index(label)],
            }
            probs = list(probs.values())
            st.info("ℹ️ Demo prediction shown — run locally for real CNN model results.")

        # ── Display results ────────────────────────────────────────
        if label == "Malignant":
            st.error(f"🔴 {get_text('prediction_label', lang)}: **{label}**")
        elif label == "Benign":
            st.success(f"🟢 {get_text('prediction_label', lang)}: **{label}**")
        else:
            st.info(f"🔵 {get_text('prediction_label', lang)}: **{label}**")

        st.write(f"**{get_text('confidence', lang)}: {confidence:.2f}%**")

        classes = ["Benign", "Malignant", "Normal"]
        prob_df = pd.DataFrame({"Class": classes, "Probability": probs})
        st.bar_chart(prob_df.set_index("Class"))

        # ── Save to database ───────────────────────────────────────
        us_bytes   = raw_bytes
        gcam_bytes = raw_bytes  # use original if no real GradCAM

        if TF_AVAILABLE and model_mode == "real":
            try:
                from ai.gradcam import gradcam, overlay_heatmap
                model   = tf.keras.models.load_model("models/cnn_model.h5")
                img_r   = cv2.resize(image, (224, 224))
                img_n   = img_r / 255.0
                img_e   = np.expand_dims(img_n, 0)
                heatmap = gradcam(model, img_e, "conv2d_2")
                cam     = overlay_heatmap(heatmap, image)
                _, gcam_enc = cv2.imencode('.png', cam)
                gcam_bytes  = gcam_enc.tobytes()
                st.subheader(get_text("gradcam_title", lang))
                st.image(cam, caption=get_text("heatmap_caption", lang))
            except Exception:
                pass

        _, us_enc = cv2.imencode('.png', image)
        us_bytes  = us_enc.tobytes()

        conn = connect()
        cur  = conn.cursor()
        try: cur.execute("ALTER TABLE diagnosis ADD COLUMN ultrasound_img BLOB")
        except: pass
        try: cur.execute("ALTER TABLE diagnosis ADD COLUMN gradcam_img BLOB")
        except: pass

        cur.execute("""
            INSERT INTO diagnosis(patient_id, result, confidence, created,
                                  ultrasound_img, gradcam_img)
            VALUES(?,?,?,?,?,?)
        """, (patient_id, label, float(confidence), get_ist_time(),
              sqlite3.Binary(us_bytes), sqlite3.Binary(gcam_bytes)))
        conn.commit()
        conn.close()

        log_audit("AI_PREDICTION","doctor",
                  f"Patient {patient_id}: {label} ({confidence:.2f}%) [{model_mode}]")
        st.info(get_text("diagnosis_saved", lang))

        # ── WhatsApp alert for Malignant ───────────────────────────
        if label == "Malignant" and patient_id:
            import urllib.parse
            conn2 = connect()
            cur2  = conn2.cursor()
            cur2.execute("SELECT phone, name FROM patients WHERE patient_id=?", (patient_id,))
            row = cur2.fetchone()
            conn2.close()
            if row and row[0]:
                phone = str(row[0]).replace(" ","").replace("-","")
                if not phone.startswith("91"): phone = "91" + phone
                msg = (f"🚨 URGENT — Onco AI CMR University\n"
                       f"Patient: {row[1]} (ID:{patient_id})\n"
                       f"MALIGNANT detected ({confidence:.1f}%).\n"
                       f"Please contact oncologist immediately.")
                wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                st.markdown(f"""
                <div style="background:rgba(239,68,68,0.1);border:1px solid #ef4444;
                            border-radius:12px;padding:16px;margin-top:12px">
                <b style="color:#ef4444">⚠️ MALIGNANT — Send WhatsApp alert to patient?</b><br><br>
                <a href="{wa_url}" target="_blank"
                   style="background:#25d366;color:white;padding:10px 20px;border-radius:8px;
                          text-decoration:none;font-weight:800;display:inline-block">
                   💚 Send WhatsApp Alert
                </a>
                </div>
                """, unsafe_allow_html=True)

        st.warning("⚕️ AI prediction is for clinical decision support only. Always confirm with a qualified doctor.")

        # ── Quick download ─────────────────────────────────────────
        st.markdown("---")
        if st.button("📥 Generate & Download Report Now", type="primary"):
            from utils.report_generator import generate_report
            with st.spinner("Building report..."):
                file = generate_report(patient_id,
                                       ultrasound_img_bytes=us_bytes,
                                       gradcam_img_bytes=gcam_bytes)
            if file:
                with open(file,"rb") as f:
                    st.download_button("⬇️ Download Complete Report PDF",
                                       data=f, file_name=file, mime="application/pdf",
                                       use_container_width=True)
                st.success("✅ Report with images generated!")
            else:
                st.error("Patient not found in database.")
