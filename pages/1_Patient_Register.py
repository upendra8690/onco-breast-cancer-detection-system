# pages/1_Patient_Register.py

import streamlit as st
import re
from auth.guard import check_login
from database.database import connect, log_audit, get_ist_time
from utils.sidebar import render_sidebar
from utils.language import get_text

check_login()
lang = render_sidebar()

# ===== CUSTOM CSS FOR ICON INPUT LOOK =====
st.markdown("""
<style>
.input-box {
    display: flex;
    align-items: center;
    background-color: #1e1e1e;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.input-box span {
    font-size: 20px;
    margin-right: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title(f"👤 {get_text('patient_register', lang)}")

# ===== INPUTS WITH ICON STYLE =====
st.markdown('<div class="input-box"><span>🆔</span></div>', unsafe_allow_html=True)
patient_id = st.text_input(get_text("patient_id", lang))

st.markdown('<div class="input-box"><span>👤</span></div>', unsafe_allow_html=True)
name = st.text_input(get_text("patient_name", lang))

st.markdown('<div class="input-box"><span>🎂</span></div>', unsafe_allow_html=True)
age = st.number_input(get_text("age", lang), min_value=0, max_value=120)

# ===== GENDER (MODERN STYLE) =====
st.markdown("### 🚻 Gender")
gender = st.radio(
    "",
    ["👨 Male", "👩 Female", "⚧ Other"],
    horizontal=True
)

# Clean value for DB
gender_clean = gender.split(" ")[1]

# ===== PHONE WITH MANY COUNTRIES =====
st.markdown("### 📱 Phone Number")

country_codes = [
    "+91 🇮🇳 India",
    "+1 🇺🇸 USA",
    "+44 🇬🇧 UK",
    "+971 🇦🇪 UAE",
    "+61 🇦🇺 Australia",
    "+81 🇯🇵 Japan",
    "+49 🇩🇪 Germany",
    "+33 🇫🇷 France",
    "+86 🇨🇳 China",
    "+7 🇷🇺 Russia",
    "+880 🇧🇩 Bangladesh",
    "+94 🇱🇰 Sri Lanka",
    "+977 🇳🇵 Nepal",
    "+92 🇵🇰 Pakistan",
    "+234 🇳🇬 Nigeria",
    "+27 🇿🇦 South Africa"
]

col1, col2 = st.columns([1, 3])

with col1:
    country = st.selectbox("", country_codes)

with col2:
    phone = st.text_input("Enter phone number")

# Extract only code
country_code = country.split(" ")[0]
full_phone = f"{country_code} {phone}"

# ===== ADDRESS =====
st.markdown('<div class="input-box"><span>🏠</span></div>', unsafe_allow_html=True)
address = st.text_area(get_text("address", lang))

# ===== VALIDATION =====
def is_valid_phone(p):
    return re.fullmatch(r"\d{7,15}", p)

# ===== REGISTER =====
if st.button(get_text("register_btn", lang), type="primary"):

    if not patient_id or not name:
        st.warning("⚠️ Please fill Patient ID and Name")
    
    elif not phone:
        st.warning("⚠️ Enter phone number")

    elif not is_valid_phone(phone):
        st.warning("⚠️ Phone must be 7–15 digits only")

    else:
        conn = connect()
        cur  = conn.cursor()

        cur.execute(
            "INSERT INTO patients(patient_id,name,age,gender,phone,address,created) VALUES(?,?,?,?,?,?,?)",
            (patient_id, name, age, gender_clean, full_phone, address, get_ist_time())
        )

        conn.commit()
        conn.close()

        log_audit("PATIENT_REGISTER", "staff", f"Patient {patient_id} ({name}) registered")

        st.success("✅ Patient Registered Successfully!")