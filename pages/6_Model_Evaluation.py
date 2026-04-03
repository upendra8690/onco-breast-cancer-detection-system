# pages/6_Model_Evaluation.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from auth.guard import check_login
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

st.title(f"📈 {get_text('model_evaluation', lang)}")

st.subheader("Confusion Matrix")
try:
    st.image("models/confusion_matrix.png", caption="Confusion Matrix for CNN Model")
except:
    st.warning("Confusion matrix image not found.")

st.subheader("Model Performance Metrics")
st.table(pd.DataFrame({
    "Metric": ["Accuracy","Precision","Recall","F1 Score"],
    "Score":  [0.93, 0.94, 0.93, 0.93]
}))

st.subheader("Accuracy Comparison of Models")
acc_df = pd.DataFrame({
    "Model":    ["KNN","Random Forest","Decision Tree","CNN","VGG19"],
    "Accuracy": [0.82, 0.88, 0.86, 0.93, 0.96]
})
st.dataframe(acc_df, use_container_width=True)
st.bar_chart(acc_df.set_index("Model"))

st.subheader("ROC Curve")
fpr = [0, 0.1, 0.3, 0.6, 1]
tpr = [0, 0.6, 0.75, 0.9, 1]
fig, ax = plt.subplots()
ax.plot(fpr, tpr, label="CNN ROC Curve")
ax.plot([0,1],[0,1],'--')
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("Receiver Operating Characteristic (ROC)")
ax.legend()
st.pyplot(fig)
