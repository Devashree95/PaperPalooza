import streamlit as st
import helpers.sidebar

# from helpers.Classifier_Util.classifier import run_classifier
from helpers.pdf_reader import get_text_content

st.set_page_config(
	page_title="ETD Classifier",
	page_icon="📄",
	layout="wide"
)

helpers.sidebar.show()

st.markdown("Welcome to ETD classifier page!")
st.write("In this page, you can run classification experiments on the ETD corpus.")

st.write("Please select a model from the sidebar to begin.")

st.write("Please select a range of ETD IDs to run the experiment on:")
offset_col, limit_col = st.columns(2)
with offset_col:
	offset = st.text_input("Offset", value=0)
with limit_col:
	limit = st.text_input("Limit", value=100)

st.write("### **OR**")

st.write("Please provide chapter text to run the experiment on:")
chapter_text = st.text_area("Chapter Text", placeholder="Paste chapter text here")

st.write("Classification result:")

st.write("### **OR**")

# Get ETD file from user
etd_file = st.file_uploader("Please upload an ETD file to run the experiment on:")

# To read file as string
if etd_file is not None:
    try:
        # Read PDF file
        chapter_text = get_text_content(etd_file)
        # st.write(chapter_text)
    except Exception as e:
        st.error(f'Error reading file: {e}')

st.write("##")

col1, col2, col3 , col4, col5 = st.columns(5)
with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3 :
    classify = st.button("Classify!")

# Sidebar
model_params = {
"model_name" : st.sidebar.selectbox("Classifier Model Name", options=["allenai/scibert_scivocab_uncased"], index=0),
"model_saved_state" : st.sidebar.text_input("Classifier Model Saved State File Path", placeholder="Enter file name with path"),
"model_class" : st.sidebar.selectbox("Classifier Model Class", options=["SciBERT"], index=0)
}

if classify:
    if chapter_text == "":
        st.error("Please provide chapter text to run the experiment on.")
        st.stop()
    # else:
    #     with st.spinner(text="Classifying..."):
    #         classification_list, time_taken = run_classifier(chapter_text, model_params)
    #     st.success('Done!')
    #     st.write("Classification result:")
    #     st.write(classification_list)
    #     st.write(f"Time taken to classify: {time_taken}")
