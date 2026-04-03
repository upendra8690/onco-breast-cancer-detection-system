# pages/24_Export_Data.py
import streamlit as st
import pandas as pd
import io
from auth.guard import check_login
from database.database import connect, log_audit

check_login()

st.title("📤 Export Data — Excel / CSV")
st.write("Export patient records, diagnosis history, and analytics data for research and reporting.")

conn = connect()

tab1, tab2, tab3 = st.tabs(["📊 Patient Records", "🤖 Diagnosis History", "📈 Research Dataset"])

with tab1:
    st.subheader("Export Patient Records")
    df_patients = pd.read_sql_query("SELECT * FROM patients", conn)
    st.write(f"Total records: **{len(df_patients)}**")
    st.dataframe(df_patients, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        csv_data = df_patients.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            csv_data,
            "onco_patients.csv",
            "text/csv",
            use_container_width=True
        )
    with col2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_patients.to_excel(writer, index=False, sheet_name="Patients")
        st.download_button(
            "⬇️ Download as Excel",
            buffer.getvalue(),
            "onco_patients.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with tab2:
    st.subheader("Export Diagnosis History")
    df_merged = pd.read_sql_query("""
        SELECT p.patient_id, p.name, p.age, p.gender,
               d.result, d.confidence, d.created as diagnosis_date
        FROM patients p
        LEFT JOIN diagnosis d ON p.patient_id = d.patient_id
        ORDER BY d.created DESC
    """, conn)

    st.write(f"Total diagnosis records: **{len(df_merged)}**")
    st.dataframe(df_merged, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        csv2 = df_merged.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ CSV", csv2, "onco_diagnosis.csv", "text/csv", use_container_width=True)
    with col2:
        buf2 = io.BytesIO()
        with pd.ExcelWriter(buf2, engine="openpyxl") as writer:
            df_merged.to_excel(writer, index=False, sheet_name="Diagnosis")
        st.download_button(
            "⬇️ Excel", buf2.getvalue(), "onco_diagnosis.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    log_audit("DATA_EXPORT", "admin", "Diagnosis history exported")

with tab3:
    st.subheader("Research Dataset Export")
    st.info("""
    📚 This export is formatted for research papers (IEEE/Scopus).
    Includes: anonymized patient data, AI predictions, confidence scores, and risk levels.
    """)

    df_research = pd.read_sql_query("""
        SELECT 
            p.patient_id,
            p.age,
            p.gender,
            d.result as ai_diagnosis,
            d.confidence as ai_confidence,
            r.risk_level,
            r.risk_score,
            d.created as diagnosis_date
        FROM patients p
        LEFT JOIN diagnosis d ON p.patient_id = d.patient_id
        LEFT JOIN risk_assessment r ON p.patient_id = r.patient_id
        ORDER BY d.created DESC
    """, conn)

    # Anonymize (remove names)
    if "name" in df_research.columns:
        df_research = df_research.drop(columns=["name"])

    st.dataframe(df_research, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        csv3 = df_research.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ CSV (Research)", csv3, "onco_research_data.csv", "text/csv", use_container_width=True)
    with col2:
        buf3 = io.BytesIO()
        with pd.ExcelWriter(buf3, engine="openpyxl") as writer:
            df_research.to_excel(writer, index=False, sheet_name="Research Data")
            # Add model info sheet
            model_info = pd.DataFrame({
                "Property": ["Model", "Dataset", "Accuracy", "Precision", "Recall", "F1 Score"],
                "Value": ["CNN + VGG19", "BUSI", "0.93", "0.94", "0.93", "0.93"]
            })
            model_info.to_excel(writer, index=False, sheet_name="Model Info")
        st.download_button(
            "⬇️ Excel (Research)", buf3.getvalue(), "onco_research.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

conn.close()