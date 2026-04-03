# pages/25_Research_Benchmark.py  ← REPLACE your existing file with this

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from auth.guard import check_login
from utils.sidebar import render_sidebar
from utils.benchmark_data import BENCHMARK_TABLE, PUBLICATIONS_TIMELINE, SYSTEM_CONTRIBUTIONS

check_login()
lang = render_sidebar()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.pub-highlight {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.08));
    border: 2px solid rgba(99,102,241,0.4);
    border-radius: 16px;
    padding: 28px 32px;
    margin: 16px 0 24px 0;
}
.journal-card {
    background: linear-gradient(145deg, #0f172a, #1e293b);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 10px;
}
.contrib-item {
    background: rgba(99,102,241,0.08);
    border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 10px 16px;
    margin: 6px 0;
    color: #e2e8f0;
    font-size: 14px;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #f8fafc;
    margin: 28px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.stApp { background: #060b18; }
section[data-testid="stSidebar"] {
    background: #0a0f1e !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
</style>
""", unsafe_allow_html=True)

st.title("📚 Research Benchmark — IEEE / Scopus Comparison")
st.write("Compare our system against published literature. Use this page to build your research paper.")

# ── 1. Suggested Abstract ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">📄 Suggested Abstract (IEEE Format)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pub-highlight">
<p style="color:#94a3b8; font-size:13px; font-weight:600; letter-spacing:1px; margin-bottom:10px">
ABSTRACT — COPY THIS FOR YOUR PAPER
</p>
<p style="color:#cbd5e1; line-height:1.9; font-size:14px">
<b>Abstract—</b>
Breast cancer is the most prevalent cancer among women globally, accounting for 27.7% of all
female cancers in India with approximately 2,00,000 new cases annually. Early and accurate
detection is critical for improving patient outcomes, where 5-year survival rates differ drastically
between early-stage (95%) and late-stage (26%) detection. This paper presents <b>Onco AI</b>, a
comprehensive AI-powered clinical decision support system for breast cancer detection using
breast ultrasound images. The proposed system employs a custom Convolutional Neural Network
(CNN) and VGG19 transfer learning model trained on the publicly available BUSI dataset
(780 images, 3 classes: Benign, Malignant, Normal) achieving <b>93% accuracy, 94% precision,
93% recall, and 0.93 F1-score</b>. The system integrates Gradient-weighted Class Activation
Mapping (GradCAM) for explainable AI (XAI), providing clinicians with visual heatmap evidence
of the model's decision regions. Unlike previous works that present only classification models,
this system delivers a complete end-to-end clinical workflow including: an 8-factor breast cancer
risk assessment engine with quantitative scoring, multi-language UI support in five Indian regional
languages (English, Hindi, Telugu, Tamil, Kannada), an AI-powered medical symptom chatbot for
patient pre-screening, telemedicine consultation scheduling with auto-generated meeting links,
digital patient consent management, population-level epidemiology analytics, multi-model
second-opinion comparison (CNN vs VGG19), complete system audit trail for medical compliance,
and automated professional PDF report generation with QR-code verification. The system is
deployed as a Streamlit web application accessible on standard hospital hardware without
specialized infrastructure. Comparative analysis shows our system achieves superior accuracy
over previously published CNN-based and transfer-learning methods on the BUSI dataset while
addressing key barriers to AI adoption in clinical settings: explainability, regional language
accessibility, and complete clinical workflow integration.
</p>
<p style="color:#818cf8; font-size:13px; margin-top:14px">
<b>Index Terms—</b> Breast cancer detection, convolutional neural network, deep learning,
GradCAM, explainable AI, ultrasound image classification, BUSI dataset, clinical decision
support system, multi-language medical AI, telemedicine, transfer learning, VGG19, risk
assessment, computer-aided diagnosis.
</p>
</div>
""", unsafe_allow_html=True)

# ── 2. Comparison Table ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Comparison with Published Methods</div>', unsafe_allow_html=True)
st.info("🔵 The highlighted row is **our system**. Use this table directly in your paper's Results section.")

df_bench = pd.DataFrame(BENCHMARK_TABLE)

# Color our row differently
def highlight_row(row):
    if row["Our System"] == "YES - OURS":
        return ["background-color: rgba(99,102,241,0.25); font-weight: bold; color: white"] * len(row)
    return ["color: #94a3b8"] * len(row)

st.dataframe(
    df_bench,
    use_container_width=True,
    hide_index=True
)

# ── 3. Accuracy Chart ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Accuracy Comparison Chart</div>', unsafe_allow_html=True)

methods = []
accuracies = []
bar_colors = []

for r in BENCHMARK_TABLE:
    name = r["Author/Year"].replace(", 20", "\n20")
    methods.append(name)
    accuracies.append(float(r["Accuracy"].replace("%", "")))
    bar_colors.append("#6366f1" if r["Our System"] == "YES - OURS" else "#334155")

fig = go.Figure(go.Bar(
    x=methods,
    y=accuracies,
    marker_color=bar_colors,
    text=[f"{a}%" for a in accuracies],
    textposition="outside",
    textfont=dict(color="white", size=12)
))
fig.update_layout(
    title="Accuracy Comparison: Our System vs Published Literature",
    xaxis_title="Method / Author",
    yaxis_title="Accuracy (%)",
    yaxis_range=[78, 100],
    paper_bgcolor="#0f172a",
    plot_bgcolor="#1e293b",
    font_color="white",
    font_size=12,
    height=420,
    showlegend=False
)
fig.add_annotation(
    x="Proposed System\n(2026)",
    y=93,
    text="⭐ Our System",
    showarrow=True,
    arrowhead=2,
    arrowcolor="#6366f1",
    font=dict(color="#818cf8", size=12),
    ay=-40
)
st.plotly_chart(fig, use_container_width=True)

# ── 4. Novel Contributions ────────────────────────────────────────────────────
st.markdown('<div class="section-title">🏆 Novel Contributions (Your Paper\'s Novelty Claims)</div>', unsafe_allow_html=True)
st.warning("👆 These are the points that make your paper **publishable**. Include these in your Introduction and Conclusion sections.")

for c in SYSTEM_CONTRIBUTIONS:
    st.markdown(f'<div class="contrib-item">{c}</div>', unsafe_allow_html=True)

# ── 5. Timeline ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Research Progress Timeline</div>', unsafe_allow_html=True)

for row in PUBLICATIONS_TIMELINE:
    if "2026" in row["Year"]:
        st.success(f"⭐ **{row['Year']}** — {row['Milestone']}")
    elif int(row["Year"]) >= 2022:
        st.info(f"**{row['Year']}** — {row['Milestone']}")
    else:
        st.write(f"**{row['Year']}** — {row['Milestone']}")

# ── 6. Suggested Journals ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">📰 Recommended Journals for Submission (2026)</div>', unsafe_allow_html=True)

journals = [
    {
        "Journal": "IEEE Access",
        "Indexing": "Scopus + IEEE Xplore",
        "Impact Factor": "3.9",
        "Review Time": "4–8 weeks",
        "Fee": "~$1,995 (waiver available)",
        "Recommendation": "⭐ Best first choice — fast, reputable"
    },
    {
        "Journal": "Computers in Biology and Medicine (Elsevier)",
        "Indexing": "Scopus + SCI",
        "Impact Factor": "7.7",
        "Review Time": "8–12 weeks",
        "Fee": "Open Access optional",
        "Recommendation": "Best for high-impact publication"
    },
    {
        "Journal": "Applied Sciences — MDPI (Special Issue: AI in Healthcare)",
        "Indexing": "Scopus + ESCI",
        "Impact Factor": "2.7",
        "Review Time": "4–6 weeks",
        "Fee": "~$2,200 (discounts available)",
        "Recommendation": "Good for student first papers"
    },
    {
        "Journal": "Expert Systems with Applications (Elsevier)",
        "Indexing": "Scopus + SCI",
        "Impact Factor": "8.5",
        "Review Time": "8–12 weeks",
        "Fee": "Open Access optional",
        "Recommendation": "High prestige — needs strong results"
    },
    {
        "Journal": "Journal of Medical Systems (Springer)",
        "Indexing": "Scopus + SCI",
        "Impact Factor": "3.7",
        "Review Time": "6–10 weeks",
        "Fee": "Open Access optional",
        "Recommendation": "Good for clinical AI systems"
    },
]

for j in journals:
    col1, col2, col3, col4 = st.columns([3, 1.5, 1, 2])
    col1.write(f"**{j['Journal']}**")
    col2.write(f"IF: {j['Impact Factor']}")
    col3.write(j['Review Time'])
    col4.write(j['Recommendation'])
    st.markdown('<hr style="border-color:rgba(255,255,255,0.05);margin:4px 0">', unsafe_allow_html=True)

# ── 7. Publication Tips ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">💡 Step-by-Step Publication Guide</div>', unsafe_allow_html=True)

tips = [
    ("Step 1: Choose Journal", "Submit to **IEEE Access** first — fastest review, open access, highly respected. If rejected, try Computers in Biology and Medicine."),
    ("Step 2: Paper Structure", "Abstract → Introduction → Related Work → Methodology → Results → Discussion → Conclusion → References (minimum 30 refs from 2019–2026)"),
    ("Step 3: Highlight Novelty", "Clearly state: 'Unlike existing works, our system provides (1) multi-language support, (2) end-to-end clinical workflow, (3) GradCAM XAI, (4) telemedicine integration...'"),
    ("Step 4: Results Section", "Use the comparison table above. Show accuracy, precision, recall, F1. Include confusion matrix image from models/confusion_matrix.png"),
    ("Step 5: Get Doctor Feedback", "Ask 2–3 doctors to rate the system usability (1–5 scale). Include this as a 'Clinical Evaluation' section — rare in student papers, very impressive to reviewers."),
    ("Step 6: Ethics Statement", "Add: 'This study does not use real patient data. The BUSI dataset is publicly available under CC license from Cairo University (Al-Dhabyani et al., 2020).'"),
    ("Step 7: Plagiarism Check", "Use Turnitin or iThenticate before submitting. Keep similarity below 15%."),
]

for title, detail in tips:
    with st.expander(f"📌 {title}"):
        st.write(detail)

# ── 8. References ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📖 Key References to Include in Your Paper</div>', unsafe_allow_html=True)

refs = [
    "[1] W. Al-Dhabyani, M. Gomaa, H. Khaled, A. Fahmy, \"Dataset of breast ultrasound images,\" Data in Brief, vol. 28, p. 104863, 2020.",
    "[2] M. H. Yap et al., \"Automated breast ultrasound lesions detection using convolutional neural networks,\" IEEE J. Biomed. Health Inform., vol. 22, no. 4, pp. 1218–1226, 2018.",
    "[3] R. R. Selvaraju et al., \"Grad-CAM: Visual explanations from deep networks via gradient-based localization,\" Int. J. Comput. Vis., vol. 128, pp. 336–359, 2020.",
    "[4] K. Simonyan and A. Zisserman, \"Very deep convolutional networks for large-scale image recognition,\" in Proc. ICLR, 2015.",
    "[5] A. Krizhevsky, I. Sutskever, G. E. Hinton, \"ImageNet classification with deep convolutional neural networks,\" in Proc. NeurIPS, 2012.",
    "[6] D. A. Zebari et al., \"Systematic review of computing approaches for breast cancer detection based computer aided diagnosis,\" IEEE Access, vol. 8, pp. 39501–39520, 2020.",
    "[7] WHO, \"Global Cancer Statistics 2022,\" CA: A Cancer Journal for Clinicians, vol. 74, no. 3, pp. 229–263, 2024.",
    "[8] ICMR, \"National Cancer Registry Programme Report,\" Indian Council of Medical Research, 2023.",
]

for ref in refs:
    st.markdown(f'<div class="contrib-item" style="font-size:13px;border-color:#334155">{ref}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.success("✅ This page gives you everything needed for a complete IEEE/Scopus research paper submission.")
