# pages/7_Dataset_Statistics.py
import streamlit as st
import pandas as pd
from auth.guard import check_login
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"📊 {get_text('dataset_stats', lang)}")
st.subheader("BUSI Dataset Overview")
df = pd.DataFrame({"Class":["Benign","Malignant","Normal"],"Images":[437,210,133]})
st.dataframe(df, use_container_width=True)
st.subheader("Class Distribution")
st.bar_chart(df.set_index("Class"))
st.subheader("Dataset Information")
st.write("Dataset Name : BUSI Breast Ultrasound Images")
st.write("Total Images : 780")
st.write("Image Size   : 224 x 224")
st.write("Classes      : Benign, Malignant, Normal")
st.info("Dataset used for training CNN and VGG19 models")
