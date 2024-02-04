import streamlit as st

import helpers.sidebar

st.set_page_config(
	page_title="PaperPalooza",
	page_icon="📄",
	layout="wide"
)

helpers.sidebar.show()

st.markdown("Welcome to ETD Experimenter!")
st.write("This UI is designed to help you run classification and summarization experiments on the ETD corpus.")

st.write("Please select tasks (classification or summarization) from the sidebar to begin...")