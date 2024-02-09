import streamlit as st

import helpers.sidebar

st.set_page_config(
	page_title="PaperPalooza",
	page_icon="📄",
	layout="wide"
)

helpers.sidebar.show()

st.markdown("Welcome to Paperpalooza!")
