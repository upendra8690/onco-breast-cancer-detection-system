# pages/8_AI_Explainability.py
import streamlit as st
import cv2
import numpy as np
from auth.guard import check_login
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"🔥 {get_text('ai_explainability', lang)}")

uploaded = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded:
    file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    st.image(img, caption="Original Image")
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
    st.image(overlay, caption="GradCAM Heatmap")
