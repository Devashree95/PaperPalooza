import streamlit as st
import fitz  # PyMuPDF for PDF processing
import requests
import time
import base64
import helpers.sidebar
import os
import uuid
from psycopg2 import IntegrityError
from helpers import connection as conn
from datetime import datetime
from PIL import Image

#load_dotenv()

connection = conn.pgsql_connect()
cur = connection.cursor()


logo = "./images/profile_3135715.png"
image = Image.open(logo)

# Function to convert image to Base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpeg;base64,{data}"

#helpers.sidebar.show()
image_base64 = get_image_as_base64(logo)

st.markdown(f"""
			<a href="/" style="color:white;text-decoration: none;">
				<div style="display:table;margin-top:-15 rem;margin-left:0%; display: flex;">
			  		<img src="{image_base64}" alt="PaperPalooza Logo" style="width:50px;height:40px;margin-left:750px; flex:2;" </img>
					<span style="padding:10px; flex:2;">{st.session_state.username}</span>
				</div>
			</a>
			<br>
				""", unsafe_allow_html=True)

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

def get_user_type():
    select_query = f"select type from user_details where email= '{st.session_state.username}'"
    cur.execute(select_query)
    return cur.fetchall()[0][0]

user_type = get_user_type()

def get_email_list():
    if user_type == 'advisor':
        select_query = f"select student_email, advisor_email from advisor_student where advisor_email= '{st.session_state.username}'"
        cur.execute(select_query)
        return cur.fetchall()[0]
    else:
        select_query = f"select advisor_email, student_email from advisor_student where student_email= '{st.session_state.username}'"
        cur.execute(select_query)
        return cur.fetchall()[0]

def post_comment(comment_text):
    """
    Save the comment to a database.
    - comment_text: the text of the comment
    - parent_id: the ID of the parent comment if it's a reply, None if it's a top-level comment
    """
    com_id = uuid.uuid4()
    date_saved_on = today = datetime.today().date()
    app = 'grammar'

    insert_query = f"INSERT INTO comments VALUES ('{com_id}', '{st.session_state.username}', '{comment_text}', '{date_saved_on}', '{app}' )"
        
    cur.execute(insert_query)
    connection.commit()
    
    return "comment_id"

def get_comments(parent_id=None):
    """
    Retrieve comments from the database.
    - parent_id: specify to get replies to a specific comment, None to get top-level comments
    Returns a list of comments, where each comment is a dict with keys 'id', 'text', and 'replies'.
    """
    emails = get_email_list()
    # Convert tuple to a list for easier manipulation if needed
    email_list = list(emails)

    # Dynamic SQL query creation based on the number of emails
    placeholders = ', '.join(['%s'] * len(email_list))
    select_query = f"select cm.*, a.first_name from comments cm join (select first_name, email from user_details) as a on cm.user_email = a.email where email in ({placeholders}) and app = 'grammar'"
    cur.execute(select_query ,email_list)
    
    return cur.fetchall()

def display_comments_section():
    # Fetch top-level comments
    comments = get_comments()
    col1, col2 = st.columns([8, 2])
    # Display each citation
    for comment in comments:
        comment_key = comment[0]
        user_info = f"<span style='color: #F8F8FF;'>User: {comment[1]}</span>"
        comment_text = f"<span style='color: #F8F8FF;'>Comment: {comment[2]}</span>"
        
        with col1:
            st.write(f'👨‍💼User: {comment[1]}')
            st.write(f'📜 Comment: {comment[2]}')
            st.markdown("---")
        with col2:
            st.write(' ')  # Spacer
            st.write(' ')
            if st.button("Delete", key=f"delete_{comment_key}"):
                delete_comment(comment_key)
                st.experimental_rerun()
            st.markdown("---")


def delete_comment(comment_key):
    try:
        delete_query = f"DELETE FROM comments WHERE comment_id = '{comment_key}'"
        cur.execute(delete_query)
        connection.commit()
        st.success("Comment deleted successfully!")
    except Exception as e:
        st.error(f"Failed to delete comment: {e}")
        connection.rollback()


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
    api_key = os.getenv("GPT_API_KEY")  # Replace with your actual API key
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

with st.expander("See Comments"):
    # Display existing comments
    display_comments_section()
    
    # Increment the key to reset the input box after posting a comment
    new_comment_key = f"new_comment_{st.session_state.input_key}"
    new_comment = st.text_input("Leave a comment:", key=new_comment_key)
    
    if st.button("Post Comment", key=f"post_new_comment_{st.session_state.input_key}"):
        post_comment_id = post_comment(new_comment)
        if post_comment_id:
            st.success("Comment posted successfully!")
            # Increment the key to reset the input box
            st.session_state.input_key += 1
            st.experimental_rerun()
        else:
            st.error("Failed to post comment.")