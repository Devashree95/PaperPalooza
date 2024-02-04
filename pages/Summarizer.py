import streamlit as st

import helpers.sidebar

st.set_page_config(
	page_title="ETD Summarizer",
	page_icon="📄",
	layout="wide"
)

helpers.sidebar.show()

st.markdown("Welcome to ETD summarization page!")
st.write("In this page, you can run summarization experiments on the ETD corpus.")

st.write("Please select a model from the sidebar to begin.")

# Input field to get ETD ID from user
etd_id = st.text_input("Please enter an ETD ID to run the experiment on:", placeholder="Enter ETD ID here...")

st.write("OR")

# Get ETD file from user
etd_file = st.file_uploader("Please upload an ETD file to run the experiment on:")



# Sidebar
summarizer = st.sidebar.selectbox("Summarizer Model", options=['model1', 'model2', 'model3'], index=0)
