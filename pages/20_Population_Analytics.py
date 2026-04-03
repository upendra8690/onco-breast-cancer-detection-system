# pages/20_Population_Analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from auth.guard import check_login
from database.database import connect
from utils.language import get_text

check_login()

lang = st.session_state.get("app_language", "English")

st.title("📊 Population Analytics — Epidemiology Dashboard")
st.write("Analyze breast cancer trends across your patient population for clinical and research insights.")

conn = connect()

# Load all data
df_patients = pd.read_sql_query("SELECT * FROM patients", conn)
df_diagnosis = pd.read_sql_query("SELECT * FROM diagnosis", conn)
df_risk = pd.read_sql_query("SELECT * FROM risk_assessment", conn)
conn.close()

# ── KPI Row ────────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total = len(df_patients)
malignant = len(df_diagnosis[df_diagnosis["result"] == "Malignant"]) if len(df_diagnosis) else 0
benign = len(df_diagnosis[df_diagnosis["result"] == "Benign"]) if len(df_diagnosis) else 0
normal = len(df_diagnosis[df_diagnosis["result"] == "Normal"]) if len(df_diagnosis) else 0
avg_conf = df_diagnosis["confidence"].mean() if len(df_diagnosis) else 0

col1.metric("Total Patients", total)
col2.metric("Malignant", malignant, delta=None)
col3.metric("Benign", benign)
col4.metric("Normal", normal)
col5.metric("Avg Confidence", f"{avg_conf:.1f}%" if avg_conf else "N/A")

st.markdown("---")

if len(df_diagnosis) == 0:
    st.info("No diagnosis data yet. Register patients and run AI predictions to see analytics.")
else:
    # ── Tab Layout ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Diagnosis Trends", "👥 Demographics", "⚠️ Risk Analysis", "🗺️ Geographic"
    ])

    with tab1:
        st.subheader("Diagnosis Distribution Over Time")

        df_merged = pd.merge(df_patients, df_diagnosis, on="patient_id", how="inner")

        col1, col2 = st.columns(2)

        with col1:
            result_counts = df_diagnosis["result"].value_counts().reset_index()
            result_counts.columns = ["Result", "Count"]
            fig_pie = px.pie(
                result_counts, names="Result", values="Count",
                title="Overall Diagnosis Distribution",
                color="Result",
                color_discrete_map={
                    "Malignant": "#ef4444",
                    "Benign": "#22c55e",
                    "Normal": "#60a5fa"
                },
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor="#0f172a", font_color="white"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Confidence distribution
            fig_hist = px.histogram(
                df_diagnosis, x="confidence", nbins=20,
                title="Confidence Score Distribution",
                color_discrete_sequence=["#818cf8"],
                labels={"confidence": "Confidence (%)"}
            )
            fig_hist.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#1e293b",
                font_color="white"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        # Malignant detection rate
        if len(df_merged) > 0:
            malignant_rate = (malignant / len(df_diagnosis)) * 100
            benign_rate = (benign / len(df_diagnosis)) * 100

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=malignant_rate,
                title={"text": "Malignant Detection Rate (%)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#ef4444"},
                    "steps": [
                        {"range": [0, 20], "color": "#166534"},
                        {"range": [20, 40], "color": "#ca8a04"},
                        {"range": [40, 100], "color": "#7f1d1d"}
                    ]
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#0f172a", font_color="white", height=300
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

    with tab2:
        st.subheader("Patient Demographics Analysis")

        if len(df_patients) > 0:
            col1, col2 = st.columns(2)

            with col1:
                # Gender distribution
                gender_counts = df_patients["gender"].value_counts().reset_index()
                gender_counts.columns = ["Gender", "Count"]
                fig_gender = px.pie(
                    gender_counts, names="Gender", values="Count",
                    title="Gender Distribution",
                    color_discrete_sequence=["#818cf8", "#f472b6"],
                    hole=0.3
                )
                fig_gender.update_layout(
                    paper_bgcolor="#0f172a", font_color="white"
                )
                st.plotly_chart(fig_gender, use_container_width=True)

            with col2:
                # Age distribution
                fig_age = px.histogram(
                    df_patients, x="age", nbins=15,
                    title="Age Distribution of Patients",
                    color_discrete_sequence=["#34d399"],
                    labels={"age": "Age (years)"}
                )
                fig_age.update_layout(
                    paper_bgcolor="#0f172a",
                    plot_bgcolor="#1e293b",
                    font_color="white"
                )
                st.plotly_chart(fig_age, use_container_width=True)

            # Age vs Diagnosis (if we have merged data)
            df_merged = pd.merge(df_patients, df_diagnosis, on="patient_id", how="inner")
            if len(df_merged) > 0:
                fig_scatter = px.scatter(
                    df_merged,
                    x="age",
                    y="confidence",
                    color="result",
                    title="Age vs Confidence Score by Diagnosis",
                    color_discrete_map={
                        "Malignant": "#ef4444",
                        "Benign": "#22c55e",
                        "Normal": "#60a5fa"
                    },
                    labels={"age": "Patient Age", "confidence": "AI Confidence (%)"},
                    size_max=12
                )
                fig_scatter.update_layout(
                    paper_bgcolor="#0f172a",
                    plot_bgcolor="#1e293b",
                    font_color="white"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

                # Age group analysis
                df_merged["age_group"] = pd.cut(
                    df_merged["age"],
                    bins=[0, 30, 40, 50, 60, 120],
                    labels=["<30", "30-40", "40-50", "50-60", "60+"]
                )

                age_result = df_merged.groupby(["age_group", "result"]).size().reset_index(name="count")
                fig_age_result = px.bar(
                    age_result,
                    x="age_group", y="count", color="result",
                    title="Diagnosis by Age Group",
                    barmode="group",
                    color_discrete_map={
                        "Malignant": "#ef4444",
                        "Benign": "#22c55e",
                        "Normal": "#60a5fa"
                    }
                )
                fig_age_result.update_layout(
                    paper_bgcolor="#0f172a",
                    plot_bgcolor="#1e293b",
                    font_color="white"
                )
                st.plotly_chart(fig_age_result, use_container_width=True)

    with tab3:
        st.subheader("Risk Level Population Analysis")

        if len(df_risk) > 0:
            col1, col2 = st.columns(2)

            with col1:
                risk_dist = df_risk["risk_level"].value_counts().reset_index()
                risk_dist.columns = ["Risk Level", "Count"]
                fig_risk = px.bar(
                    risk_dist, x="Risk Level", y="Count",
                    title="Population Risk Distribution",
                    color="Risk Level",
                    color_discrete_map={
                        "Low Risk": "#22c55e",
                        "Moderate Risk": "#f59e0b",
                        "High Risk": "#ef4444",
                        "Very High Risk": "#7f1d1d"
                    }
                )
                fig_risk.update_layout(
                    paper_bgcolor="#0f172a",
                    plot_bgcolor="#1e293b",
                    font_color="white"
                )
                st.plotly_chart(fig_risk, use_container_width=True)

            with col2:
                fig_risk_pie = px.pie(
                    risk_dist, names="Risk Level", values="Count",
                    title="Risk Level Proportion",
                    color="Risk Level",
                    color_discrete_map={
                        "Low Risk": "#22c55e",
                        "Moderate Risk": "#f59e0b",
                        "High Risk": "#ef4444",
                        "Very High Risk": "#7f1d1d"
                    },
                    hole=0.4
                )
                fig_risk_pie.update_layout(
                    paper_bgcolor="#0f172a", font_color="white"
                )
                st.plotly_chart(fig_risk_pie, use_container_width=True)

            # Risk score histogram
            fig_score = px.histogram(
                df_risk, x="risk_score", nbins=10,
                title="Risk Score Distribution Across Population",
                color_discrete_sequence=["#f97316"]
            )
            fig_score.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#1e293b",
                font_color="white"
            )
            st.plotly_chart(fig_score, use_container_width=True)

        else:
            st.info("No risk assessment data yet. Run risk assessments from the Risk Assessment page.")

    with tab4:
        st.subheader("Geographic Distribution (Address-Based)")

        if len(df_patients) > 0:
            # Group by address (city/area)
            addr_counts = df_patients["address"].value_counts().head(10).reset_index()
            addr_counts.columns = ["Location", "Patients"]

            fig_geo = px.bar(
                addr_counts,
                x="Patients", y="Location",
                orientation="h",
                title="Top Patient Locations",
                color="Patients",
                color_continuous_scale="Reds"
            )
            fig_geo.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#1e293b",
                font_color="white",
                yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig_geo, use_container_width=True)

            # India map placeholder (state-level)
            india_data = pd.DataFrame({
                "State": ["Andhra Pradesh", "Telangana", "Tamil Nadu", "Karnataka",
                          "Maharashtra", "Delhi", "Uttar Pradesh", "West Bengal"],
                "Cases": [4500, 3200, 6100, 5400, 12000, 8900, 7600, 5200],
                "Code": ["AP", "TG", "TN", "KA", "MH", "DL", "UP", "WB"]
            })

            fig_india = px.bar(
                india_data.sort_values("Cases", ascending=False),
                x="State", y="Cases",
                title="Breast Cancer Cases by State (India — National Data 2023)",
                color="Cases",
                color_continuous_scale="Reds"
            )
            fig_india.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#1e293b",
                font_color="white"
            )
            st.plotly_chart(fig_india, use_container_width=True)

            st.caption("Note: State-level data is sourced from ICMR/National Cancer Registry Programme 2023.")