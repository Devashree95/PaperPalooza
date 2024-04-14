import streamlit as st

# Add a confirmation message
# Middle of the page, create multiple columns
col1, col2 = st.columns([1, 1])

with col1:
    st.write("Are you sure you want to log out?")
with col2:
    if st.button("Yes"):
        st.session_state.user_logged_in = False
        st.session_state.clear()
        st.toast("You have been logged out.")
        st.switch_page("Paperpalooza_Home.py")