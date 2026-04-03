# pages/21_AI_Chatbot.py
import streamlit as st
from auth.guard import check_login
from utils.language import get_text

check_login()

st.markdown("""
<style>
.chat-container {
    background: linear-gradient(145deg, #0f172a, #1e293b);
    border-radius: 20px;
    padding: 24px;
    min-height: 400px;
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 16px;
}
.user-msg {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0 8px 20%;
    font-size: 14px;
    line-height: 1.5;
}
.bot-msg {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    color: #e2e8f0;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 8px 20% 8px 0;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid rgba(255,255,255,0.08);
}
.bot-icon { color: #60a5fa; font-weight: 700; margin-bottom: 4px; }
.urgent-msg { border-left: 3px solid #ef4444 !important; }
</style>
""", unsafe_allow_html=True)

lang = st.session_state.get("app_language", "English")

st.title("💬 AI Medical Chatbot — Breast Cancer Guidance")
st.write("Ask me about breast cancer symptoms, risk factors, imaging, or treatment information.")
st.warning("⚠️ This chatbot provides general health information only. Always consult a doctor for medical advice.")

# ─── Chatbot Knowledge Base ─────────────────────────────────────────────────────
KNOWLEDGE_BASE = {
    "lump": {
        "keywords": ["lump", "mass", "bump", "knot", "swelling", "hard"],
        "response": """🔴 **A new breast lump is the most common sign of breast cancer.**

**What to do:**
- See a doctor within 24–48 hours — do not wait
- Note: Is it soft or hard? Painful or painless? Moving or fixed?
- Hard, painless, irregular lumps are more concerning than soft, moveable ones

**Important:** Most lumps are NOT cancerous — but all should be evaluated professionally.
        """,
        "urgency": "high"
    },
    "pain": {
        "keywords": ["pain", "ache", "sore", "tender", "hurt", "burning"],
        "response": """🟡 **Breast pain (mastalgia) is common and usually NOT cancer.**

**Possible causes:**
- Hormonal changes (most common)
- Caffeine sensitivity
- Fibrocystic breast changes
- Muscle strain

**When to worry:** Persistent pain only in one specific spot, combined with a lump or skin changes — see a doctor within 1 week.
        """,
        "urgency": "medium"
    },
    "nipple": {
        "keywords": ["nipple", "discharge", "fluid", "bleeding", "inverted", "inward"],
        "response": """🔴 **Nipple changes can be an important warning sign.**

**Concerning signs:**
- Bloody or clear discharge without squeezing
- Nipple suddenly turning inward (inversion)
- Redness or scaling on the nipple
- Persistent itching of the nipple

**Action:** Schedule a doctor visit within 1 week. Imaging (ultrasound/mammogram) may be needed.
        """,
        "urgency": "high"
    },
    "skin": {
        "keywords": ["skin", "dimple", "redness", "rash", "orange", "peel", "texture", "puckering"],
        "response": """🔴 **Skin changes on the breast are a serious warning sign.**

**Inflammatory breast cancer signs:**
- Orange peel texture (peau d'orange)
- Redness covering large area of breast
- Skin dimpling or puckering
- Warm, swollen breast

**Action:** This type of cancer is aggressive. See a doctor or emergency room TODAY.
        """,
        "urgency": "high"
    },
    "risk": {
        "keywords": ["risk", "chance", "probability", "likely", "hereditary", "genetic", "family", "brca"],
        "response": """📊 **Breast Cancer Risk Factors:**

**High Risk Factors:**
- BRCA1/BRCA2 gene mutation — 50-85% lifetime risk
- Mother/sister/daughter with breast cancer
- Previous breast cancer diagnosis
- Dense breast tissue

**Moderate Risk:**
- Age over 40
- Hormone replacement therapy (HRT)
- Late menopause (after 55)
- Never having children

**Protective Factors:**
- Early pregnancy
- Breastfeeding
- Regular exercise
- Maintaining healthy weight

Use our **Risk Assessment** page for your personalized risk score!
        """,
        "urgency": "low"
    },
    "mammogram": {
        "keywords": ["mammogram", "screening", "xray", "x-ray", "test", "imaging", "scan", "ultrasound", "mri"],
        "response": """🏥 **Breast Cancer Screening Guide:**

| Test | Age Group | Frequency |
|------|-----------|-----------|
| Self-exam | 20+ | Monthly |
| Clinical exam | 20-39 | Every 3 years |
| Clinical exam | 40+ | Annually |
| Mammogram | 40-74 | Annually |
| Ultrasound | Dense tissue | As advised |
| MRI | High risk | Annually |

**Our AI system uses breast ultrasound** — the same images are analyzed by our CNN model to classify Benign, Malignant, or Normal tissue.

Visit our **Imaging Guide** page to learn how ultrasound images are taken!
        """,
        "urgency": "low"
    },
    "treatment": {
        "keywords": ["treatment", "surgery", "chemo", "chemotherapy", "radiation", "mastectomy", "lumpectomy", "cure"],
        "response": """💊 **Breast Cancer Treatment Overview:**

**Stage-Based Treatment:**
- **Stage 0–1 (Early):** Lumpectomy + radiation. 99% 5-year survival rate.
- **Stage 2:** Surgery + chemotherapy ± radiation. 85-90% survival rate.
- **Stage 3:** Chemotherapy before/after surgery. 70-80% survival rate.
- **Stage 4 (Advanced):** Targeted therapy, hormone therapy, immunotherapy.

**Types of Surgery:**
- Lumpectomy — removes tumor + small margin
- Mastectomy — removes entire breast

**Modern targeted therapies** (HER2+, ER+) have dramatically improved outcomes since 2015.

Always discuss treatment with an oncologist — treatment depends on cancer type, stage, and individual factors.
        """,
        "urgency": "low"
    },
    "busi": {
        "keywords": ["busi", "dataset", "data", "model", "cnn", "accuracy", "vgg", "ai"],
        "response": """🤖 **About Our AI Model:**

**Dataset:** BUSI (Breast Ultrasound Images)
- 780 images, 3 classes: Benign (437), Malignant (210), Normal (133)
- Source: Cairo University, 2020
- Image size: 224×224 pixels

**Model Performance:**
| Metric | Score |
|--------|-------|
| Accuracy | 93% |
| Precision | 94% |
| Recall | 93% |
| F1 Score | 93% |

**Explainability:** Grad-CAM visualization shows exactly which areas of the image the AI focused on.

This system is designed for **clinical decision support** — always confirmed by a qualified doctor.
        """,
        "urgency": "low"
    }
}


def get_bot_response(user_input):
    """Simple rule-based NLU for medical chatbot."""
    text = user_input.lower()

    for key, entry in KNOWLEDGE_BASE.items():
        for kw in entry["keywords"]:
            if kw in text:
                return entry["response"], entry["urgency"]

    # Greeting
    if any(w in text for w in ["hello", "hi", "hey", "namaste", "help"]):
        return """👋 **Hello! I'm the Onco AI Medical Chatbot.**

I can help you with information about:
- 🔍 Breast cancer **symptoms** (lump, nipple changes, skin changes)
- ⚠️ **Risk factors** and family history  
- 🏥 **Screening** (mammogram, ultrasound, self-exam)
- 🤖 Our **AI model** and how it works
- 💊 **Treatment** options overview

Just type your question in plain language!

Example: *"I found a lump in my breast, what should I do?"*
        """, "low"

    if any(w in text for w in ["thank", "thanks", "ok", "okay", "bye"]):
        return """You're welcome! 🌸

Remember: **Early detection saves lives.** 

If you have any concerning symptoms, please consult a doctor. Use our **Symptoms Checker** and **Risk Assessment** pages for a detailed evaluation.

Take care! 💙""", "low"

    # Default fallback
    return """I understand you have a concern about **breast health**.

I can specifically help with:
- **Symptoms**: Ask me about lumps, nipple discharge, skin changes, pain
- **Risk factors**: Ask about family history, age, genetics
- **Screening**: Ask about mammograms, ultrasound, self-exams
- **Our AI model**: Ask about CNN, accuracy, GradCAM

Could you rephrase your question? For example:
*"What does a breast lump feel like?"* or *"When should I get a mammogram?"*

For immediate medical concerns, please call a doctor or visit our **Symptoms Checker** page.
    """, "low"


# ─── Chat Interface ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "content": """👋 **Welcome to the Onco AI Medical Chatbot!**

I provide information about breast cancer symptoms, risk factors, screening, and our AI system.

**Quick questions you can ask:**
- "I found a lump — what should I do?"
- "What are the risk factors for breast cancer?"
- "When should I get a mammogram?"
- "How does the AI model work?"

⚠️ *This chatbot provides health information only — always consult a real doctor.*
        """, "urgency": "low"}
    ]

# Display chat history
chat_html = '<div class="chat-container">'
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        chat_html += f'<div class="user-msg">👤 {msg["content"]}</div>'
    else:
        urgency_class = "urgent-msg" if msg.get("urgency") == "high" else ""
        chat_html += f'<div class="bot-msg {urgency_class}"><div class="bot-icon">🤖 Onco AI</div>{msg["content"]}</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# Input
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_msg = st.text_input(
        "Type your question...",
        placeholder="e.g. I found a lump in my breast, what should I do?",
        label_visibility="collapsed",
        key="chat_input"
    )
with col_btn:
    send = st.button("Send 💬", use_container_width=True)

# Quick action buttons
st.markdown("**Quick Topics:**")
q_cols = st.columns(5)
quick_questions = [
    "I have a breast lump",
    "What are risk factors?",
    "When to get mammogram?",
    "I have nipple discharge",
    "How does the AI work?"
]

for i, (col, q) in enumerate(zip(q_cols, quick_questions)):
    if col.button(q, key=f"q_{i}"):
        response, urgency = get_bot_response(q)
        st.session_state.chat_history.append({"role": "user", "content": q})
        st.session_state.chat_history.append({"role": "bot", "content": response, "urgency": urgency})
        st.rerun()

if send and user_msg:
    response, urgency = get_bot_response(user_msg)
    st.session_state.chat_history.append({"role": "user", "content": user_msg})
    st.session_state.chat_history.append({"role": "bot", "content": response, "urgency": urgency})
    st.rerun()

if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()