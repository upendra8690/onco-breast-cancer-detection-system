# pages/9_Experiments.py
import streamlit as st
import pandas as pd
from auth.guard import check_login
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"🧪 {get_text('experiments', lang)}")
df = pd.DataFrame({
    "Model":    ["KNN","Random Forest","Decision Tree","CNN","VGG19"],
    "Accuracy": [0.82, 0.88, 0.86, 0.93, 0.96]
})
st.dataframe(df, use_container_width=True)
st.bar_chart(df.set_index("Model"))
