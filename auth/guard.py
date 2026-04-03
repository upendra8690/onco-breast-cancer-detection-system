# auth/guard.py  ← REPLACE
import streamlit as st

def check_login():
    """Check if doctor/admin is logged in."""
    if not st.session_state.get("logged_in"):
        st.warning("Please login first")
        st.switch_page("pages/00_Login.py")
    # If patient tries to access doctor page, redirect them
    if st.session_state.get("user_type") == "patient":
        st.warning("Patients please use the Patient Portal.")
        st.switch_page("pages/29_Patient_Portal.py")
