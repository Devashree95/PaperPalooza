import streamlit as st
import requests
import os
import helpers.sidebar
from PIL import Image
import base64
from dotenv import load_dotenv
import time
load_dotenv()
import fitz
import openai
from nltk.tokenize import sent_tokenize
from io import StringIO
import uuid
from psycopg2 import IntegrityError
from helpers import connection as conn
from datetime import datetime


st.set_page_config(
	page_title="Text Summarizer",
	page_icon="📄"
)

#helpers.sidebar.show()

# Streamlit UI setup

connection = conn.pgsql_connect()
cur = connection.cursor()

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
    
set_background_from_local_file('./images/summarizer_background.png')

def get_user_type():
    select_query = f"select type from user_details where email= '{st.session_state.username}'"
    cur.execute(select_query)
    return cur.fetchall()[0][0]

user_type = get_user_type()

def get_email_list():
    if user_type == 'advisor':
        select_query = f"select student_email, advisor_email from advisor_student where advisor_email= '{st.session_state.username}'"
        cur.execute(select_query)
        res = cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return ''
    else:
        select_query = f"select advisor_email, student_email from advisor_student where student_email= '{st.session_state.username}'"
        cur.execute(select_query)
        res = cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return ''
        
def post_comment(comment_text):
    """
    Save the comment to a database.
    - comment_text: the text of the comment
    - parent_id: the ID of the parent comment if it's a reply, None if it's a top-level comment
    """
    com_id = uuid.uuid4()
    date_saved_on = today = datetime.today().date()
    app = 'summarizer'

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
    if emails == '':
        return ''
    # Convert tuple to a list for easier manipulation if needed
    email_list = list(emails)

    # Dynamic SQL query creation based on the number of emails
    placeholders = ', '.join(['%s'] * len(email_list))
    select_query = f"select cm.*, a.first_name from comments cm join (select first_name, email from user_details) as a on cm.user_email = a.email where email in ({placeholders}) and app = 'summarizer'"
    cur.execute(select_query ,email_list)
    
    return cur.fetchall()

def display_comments_section():
    # Fetch top-level comments
    comments = get_comments()
    if comments == '':
        st.write("No Comments to display")
        return
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
                st.rerun()
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


logo = "./images/profile_3135715.png"
image = Image.open(logo)

# Function to convert image to Base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpeg;base64,{data}"
	
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


openai.api_key = os.getenv('OPENAI_API_KEY')

st.title("Text Summarizer") 

def read_pdf(file):
    context = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf_file:
        num_pages = pdf_file.page_count
        for page_num in range(num_pages):
                page = pdf_file[page_num]
                page_text = page.get_text()
                context += page_text
    return context

def split_text(text, chunk_size=5000):
  chunks = []
  current_chunk = StringIO()
  current_size = 0
  sentences = sent_tokenize(text)
  for sentence in sentences:
    sentence_size = len(sentence)
    if sentence_size > chunk_size:
      while sentence_size > chunk_size:
        chunk = sentence[:chunk_size]
        chunks.append(chunk)
        sentence = sentence[chunk_size:]
        sentence_size -= chunk_size
        current_chunk = StringIO()
        current_size = 0
    if current_size + sentence_size < chunk_size:
      current_chunk.write(sentence)
      current_size += sentence_size
    else:
      chunks.append(current_chunk.getvalue())
      current_chunk = StringIO()
      current_size = 0
      current_chunk.write(sentence)
      current_size = sentence_size
  if current_chunk.getvalue():
     chunks.append(current_chunk.getvalue())
  return chunks
  

def gpt3_completion(prompt, model='gpt-3.5-turbo', temp=0.5, top_p=0.3, tokens=1000):
    #st.write("Calling GPT-3 API...")
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    try:
        response = openai.chat.completions.create(
       messages=[
        {
            "role": "system",
            "content": prompt,
        }
            ],
        model=model,
        temperature=temp,
        top_p=top_p,
        max_tokens=tokens,
        stop=None
        )
        #st.write("API Response:", response)
        summary_text = response.choices[0].message.content.strip()
        #st.write("Summary:", summary_text)
        return summary_text
    except Exception as oops:
        st.error(f"GPT-3 error: {oops}")
        return f"GPT-3 error: {oops}"


def summarize(doc):
  with st.spinner(text="Summarizing..."):
    chunks = split_text(doc)
    #st.write("Chunks:",chunks)
    summaries = []
    for chunk in chunks:
        prompt = "Please summarize the following document in 2 sentences: \n"
        summary = gpt3_completion(prompt + chunk)
        if summary.startswith("GPT-3 error:"):
            continue
        summaries.append(summary)
    return ' '.join(summaries)

document = st.file_uploader("Choose a PDF file", type=["pdf"])
#st.write(document)

if st.button("Summarize File"):
    if not document:
        st.warning("Please upload pdf")
    else:
        docs = read_pdf(document)
        summary_text = summarize(docs)
        st.write("Summary:  \n", summary_text)

def text_input(text):
    api_url = "https://api.openai.com/v1/chat/completions"
    api_key = openai.api_key 
    headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Please summarize the following text input in atleast 150 words:\n"},
                {"role": "user", "content": text},
            ],
        }
    
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        suggestions = result.get("choices", [])[0].get("message", {}).get("content", "").strip()
        return suggestions
    else:
        print(response.text)  # For debugging purposes
        return ["There was an error summarizing the text."]
  
text = st.text_area("Enter text to summarize:", height=250)
if st.button("Summarize Text"):
        if not text:
            st.warning("Please input text")
        else:
            with st.spinner(text="Summarizing..."):
                suggestions = text_input(text)
                st.write("Summary:  \n", suggestions)
     
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
            st.rerun()
        else:
            st.error("Failed to post comment.")