import streamlit as st

st.session_state.user_logged_in = False
st.session_state.clear()
st.toast("You have been logged out.")
st.switch_page("Paperpalooza_Home.py")