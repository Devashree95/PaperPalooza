import streamlit as st
import fitz  # PyMuPDF for PDF processing
import requests
import time
import base64
import helpers.sidebar

helpers.sidebar.show()

def get_base64_of_file(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode()
    
def set_background_from_local_file(path):
    base64_string = get_base64_of_file(path)
    # CSS to utilize the Base64 encoded string as a background
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{base64_string}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
set_background_from_local_file('./images/grammar_background.png')


# Initialize session state for tracking dismissed suggestions
if 'dismissed_suggestions' not in st.session_state:
    st.session_state.dismissed_suggestions = set()

# Function to extract text from PDF
def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# Updated function to check grammar using GPT-4 API and the chat endpoint
def check_grammar(text):
    api_url = "https://api.openai.com/v1/chat/completions"
    api_key = "insert_api_key_here"  # Replace with your actual API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a highly skilled English teacher. Correct any grammar mistakes."},
            {"role": "user", "content": text},
        ],
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        suggestions = result.get("choices", [])[0].get("message", {}).get("content", "").strip()
        return suggestions.split('\n')
    else:
        print(response.text)  # For debugging purposes
        return ["There was an error processing the grammar check."]

# Function to handle dismissal of a suggestion
def dismiss_suggestion(uid):
    st.session_state.dismissed_suggestions.add(uid)
    # Force a rerun to update the UI
    st.experimental_rerun()

# Streamlit UI setup
st.title("Grammar Checker")

input_method = st.radio("Select Input Method:", ("Write Text", "Upload PDF File"))
text = ""
if input_method == "Write Text":
    text = st.text_area("Enter text to check:", height=250)
elif input_method == "Upload PDF File":
    pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if pdf_file is not None:
        text = extract_text_from_pdf(pdf_file)

if st.button("Correct Grammar"):
    if not text:
        st.warning("Please input text or upload a PDF file.")
    else:
        suggestions = check_grammar(text)
        if suggestions:
            for index, suggestion in enumerate(suggestions):
                # Generate a unique identifier for each suggestion
                uid = f"suggestion-{index}-{time.time()}"
                if uid not in st.session_state.dismissed_suggestions:
                    with st.container():
                        # st.write("Here's the correct grammar: \n\n" +  suggestion)
                        st.write(suggestion)
                        st.button("Dismiss", key=uid, on_click=dismiss_suggestion, args=(uid,))
        else:
            st.info("No grammar mistakes detected.")
