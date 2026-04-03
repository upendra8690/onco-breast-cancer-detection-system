# pages/16_Risk_Assessment.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from auth.guard import check_login
from database.database import connect, log_audit
from utils.language import get_text

check_login()

lang = st.session_state.get("app_language", "English")

st.title(f"⚠️ {get_text('risk_assessment', lang)}")
st.write("Evaluate a patient's risk of developing breast cancer based on known risk factors.")

patient_id = st.text_input(get_text("patient_id", lang))

st.markdown("---")
st.subheader("Risk Factor Questionnaire")

# Risk Factors with Weights
col1, col2 = st.columns(2)

with col1:
    age_factor = st.selectbox(
        "Patient Age Group",
        ["Under 30 (Low Risk)", "30-40 (Moderate Risk)", "40-50 (High Risk)", "Above 50 (Very High Risk)"]
    )
    age_score = {"Under 30 (Low Risk)": 0, "30-40 (Moderate Risk)": 1,
                 "40-50 (High Risk)": 2, "Above 50 (Very High Risk)": 3}[age_factor]

    family_history = st.radio(
        "Family history of breast cancer (mother/sister/daughter)?",
        ["No", "Yes"]
    )
    family_score = 3 if family_history == "Yes" else 0

    hormone_therapy = st.radio(
        "Currently on or previously used hormone replacement therapy?",
        ["No", "Yes"]
    )
    hormone_score = 2 if hormone_therapy == "Yes" else 0

    dense_breast = st.radio(
        "Diagnosed with dense breast tissue?",
        ["No", "Yes", "Unknown"]
    )
    dense_score = 2 if dense_breast == "Yes" else 0

with col2:
    previous_biopsy = st.radio(
        "Previous breast biopsy (especially with abnormal cells)?",
        ["No", "Yes - Normal", "Yes - Atypical Cells"]
    )
    biopsy_score = {"No": 0, "Yes - Normal": 1, "Yes - Atypical Cells": 3}[previous_biopsy]

    alcohol_use = st.radio(
        "Regular alcohol consumption?",
        ["No", "Occasional", "Regular"]
    )
    alcohol_score = {"No": 0, "Occasional": 1, "Regular": 2}[alcohol_use]

    obesity = st.radio(
        "Overweight or obese (BMI > 25) after menopause?",
        ["No", "Yes"]
    )
    obesity_score = 1 if obesity == "Yes" else 0

    late_menopause = st.radio(
        "Late menopause (after age 55)?",
        ["No", "Yes", "Not Applicable"]
    )
    late_score = 1 if late_menopause == "Yes" else 0

# ---- Calculate Risk ----
if st.button("🔍 Calculate Risk Score"):

    total_score = age_score + family_score + hormone_score + dense_score + \
                  biopsy_score + alcohol_score + obesity_score + late_score

    max_score = 3 + 3 + 2 + 2 + 3 + 2 + 1 + 1  # = 17
    risk_pct = (total_score / max_score) * 100

    if risk_pct < 25:
        risk_level = "Low Risk"
        risk_color = "green"
        advice = "Maintain regular annual checkups and self-examination."
    elif risk_pct < 50:
        risk_level = "Moderate Risk"
        risk_color = "orange"
        advice = "Recommend annual mammogram. Lifestyle changes advised."
    elif risk_pct < 75:
        risk_level = "High Risk"
        risk_color = "red"
        advice = "Refer to oncologist. Consider genetic testing (BRCA1/BRCA2)."
    else:
        risk_level = "Very High Risk"
        risk_color = "darkred"
        advice = "Urgent oncologist referral. Enhanced screening protocol required."

    # Gauge Chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"Risk Score: {risk_level}"},
        gauge={
            "axis": {"range": [0, max_score]},
            "bar": {"color": risk_color},
            "steps": [
                {"range": [0, 4], "color": "lightgreen"},
                {"range": [4, 9], "color": "yellow"},
                {"range": [9, 13], "color": "orange"},
                {"range": [13, 17], "color": "red"},
            ],
            "threshold": {"line": {"color": "black", "width": 4}, "thickness": 0.75, "value": total_score}
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    # Summary Table
    factor_data = {
        "Risk Factor": ["Age", "Family History", "Hormone Therapy", "Dense Breast",
                        "Previous Biopsy", "Alcohol Use", "Obesity", "Late Menopause"],
        "Score": [age_score, family_score, hormone_score, dense_score,
                  biopsy_score, alcohol_score, obesity_score, late_score],
        "Max": [3, 3, 2, 2, 3, 2, 1, 1]
    }

    df = pd.DataFrame(factor_data)
    st.dataframe(df, use_container_width=True)

    st.subheader("Assessment Result")
    if risk_level in ["High Risk", "Very High Risk"]:
        st.error(f"🔴 {risk_level} — Score: {total_score}/{max_score} ({risk_pct:.0f}%)")
    elif risk_level == "Moderate Risk":
        st.warning(f"🟡 {risk_level} — Score: {total_score}/{max_score} ({risk_pct:.0f}%)")
    else:
        st.success(f"🟢 {risk_level} — Score: {total_score}/{max_score} ({risk_pct:.0f}%)")

    st.info(f"**Medical Advice:** {advice}")

    # Save to DB
    if patient_id:
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO risk_assessment(
                patient_id, age_factor, family_history, hormone_therapy,
                dense_breast, previous_biopsy, alcohol_use, obesity,
                late_menopause, risk_score, risk_level
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, (
            patient_id, age_score, family_score, hormone_score,
            dense_score, biopsy_score, alcohol_score, obesity_score,
            late_score, total_score, risk_level
        ))
        conn.commit()
        conn.close()
        log_audit("RISK_ASSESSMENT", "doctor", f"Patient {patient_id} risk assessed: {risk_level}")
        st.success("Risk assessment saved to patient record!")

# ---- View Past Assessments ----
st.markdown("---")
st.subheader("📋 View Past Risk Assessments")

view_pid = st.text_input("Enter Patient ID to view past assessments:")
if st.button("Load Assessments"):
    conn = connect()
    df = pd.read_sql_query(
        "SELECT risk_score, risk_level, created FROM risk_assessment WHERE patient_id=? ORDER BY created DESC",
        conn, params=(view_pid,)
    )
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No risk assessments found for this patient.")