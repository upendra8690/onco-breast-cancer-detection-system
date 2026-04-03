# pages/14_Symptoms_Checker.py
import streamlit as st
import pandas as pd
from auth.guard import check_login
from database.database import connect, log_audit
from utils.language import get_text
from utils.symptoms_data import SYMPTOMS_DATA, EARLY_DETECTION_INFO

check_login()

lang = st.session_state.get("app_language", "English")
data = SYMPTOMS_DATA.get("English")  # Base data always English; UI in selected language

st.title(f"🔍 {get_text('symptoms_checker', lang)}")

st.markdown(f"""
> **{data['description']}**
""")

st.warning(data['emergency_note'])

# ---- Symptom Checklist ----
st.subheader("Select symptoms you are experiencing:")

selected_symptoms = []
symptom_score = 0

for s in data["symptoms"]:
    col1, col2, col3 = st.columns([3, 1, 2])
    checked = col1.checkbox(s["name"])
    severity_color = "🔴" if s["severity"] == "High" else "🟡"
    col2.write(f"{severity_color} {s['severity']}")
    col3.write(s["description"][:60] + "...")

    if checked:
        selected_symptoms.append(s["name"])
        symptom_score += 2 if s["severity"] == "High" else 1

# ---- Symptom Assessment Result ----
if st.button("🔎 Assess Symptoms"):

    if len(selected_symptoms) == 0:
        st.info("No symptoms selected. You appear to have no current symptoms.")
    else:
        st.subheader("Assessment Result")

        if symptom_score >= 6:
            st.error(f"⚠️ HIGH CONCERN — {len(selected_symptoms)} symptoms selected. Please see a doctor IMMEDIATELY.")
        elif symptom_score >= 3:
            st.warning(f"🟡 MODERATE CONCERN — {len(selected_symptoms)} symptoms selected. Please schedule a doctor visit within 1 week.")
        else:
            st.info(f"🟢 LOW CONCERN — {len(selected_symptoms)} mild symptom(s). Monitor closely and see a doctor if it persists.")

        st.subheader("Your Selected Symptoms:")
        for s_name in selected_symptoms:
            match = [s for s in data["symptoms"] if s["name"] == s_name]
            if match:
                s = match[0]
                icon = "🔴" if s["severity"] == "High" else "🟡"
                st.write(f"{icon} **{s['name']}** — {s['description']}")
                st.caption(f"Recommended Action: {s['action']}")

        # Save to DB
        patient_id = st.text_input("Enter Patient ID to save this symptoms log (optional):")
        if st.button("💾 Save Symptoms Log") and patient_id:
            conn = connect()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO symptoms_log(patient_id, symptoms, notes) VALUES(?,?,?)",
                (patient_id, ", ".join(selected_symptoms), f"Score: {symptom_score}")
            )
            conn.commit()
            conn.close()
            log_audit("SYMPTOMS_LOG", "user", f"Patient {patient_id} symptoms logged")
            st.success("Symptoms saved successfully!")

# ---- Early Detection Info ----
st.markdown("---")
st.subheader("🏥 Early Detection Methods")

info = EARLY_DETECTION_INFO.get("English", [])
cols = st.columns(2)
for i, item in enumerate(info):
    with cols[i % 2]:
        st.info(f"{item['icon']} **{item['title']}**\n\n{item['description']}")

# ---- Risk Statistics ----
st.markdown("---")
st.subheader("📊 Breast Cancer Statistics (India)")

stat_data = {
    "Statistic": [
        "New cases per year (India)",
        "1 in every X women affected",
        "5-year survival rate (early detection)",
        "5-year survival rate (late detection)",
        "Age group most affected",
        "% of all female cancers"
    ],
    "Value": [
        "~2,00,000",
        "28",
        "95%",
        "26%",
        "30-60 years",
        "27.7%"
    ]
}
st.table(pd.DataFrame(stat_data))