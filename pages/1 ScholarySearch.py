import streamlit as st
import requests
import feedparser
import helpers.sidebar
from datetime import datetime
from urllib.parse import quote
import streamlit.components.v1 as components
from PIL import Image
import base64
from helpers import connection as conn
from psycopg2 import IntegrityError
import uuid
import re
from operator import itemgetter

#helpers.sidebar.show()

logo = "./images/profile_3135715.png"
image = Image.open(logo)

connection = conn.pgsql_connect()
cur = connection.cursor()

# Function to convert image to Base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpeg;base64,{data}"
	
image_base64 = get_image_as_base64(logo)

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
    
set_background_from_local_file('./images/chatbot_bg.png')

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
    app = 'scholarly search'

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
    select_query = f"select cm.*, a.first_name from comments cm join (select first_name, email from user_details) as a on cm.user_email = a.email where email in ({placeholders}) and app = 'scholarly search'"
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


st.markdown(f"""
			<a href="/" style="color:white;text-decoration: none;">
				<div style="display:table;margin-top:-15 rem;margin-left:0%; display: flex;">
			  		<img src="{image_base64}" alt="PaperPalooza Logo" style="width:50px;height:40px;margin-left:750px; flex:2;" </img>
					<span style="padding:10px; flex:2;">{st.session_state.username}</span>
				</div>
			</a>
			<br>
				""", unsafe_allow_html=True)

# Ensure initialization of session state variables at the start
if 'page_number' not in st.session_state:
    st.session_state['page_number'] = 0

if 'is_last_page' not in st.session_state:
    st.session_state['is_last_page'] = False

if 'papers' not in st.session_state:
    st.session_state['papers'] = []

if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ''
if 'sort_order' not in st.session_state:
    st.session_state['sort_order'] = 'ascending'  # Default sort order

# def fetch_papers(search_query, start=0, max_results=20):
#     base_url = "http://export.arxiv.org/api/query?"
#     query = f"search_query=all:{quote(search_query)}&start={start}&max_results={max_results}"
#     response = requests.get(base_url + query)
#     return response.text

def fetch_papers(search_query, start=0, max_results=20):
    # Clean search query by replacing special characters with space
    sanitized_query = re.sub(r'[^\w\s-]', ' ', search_query)
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=all:{quote(sanitized_query)}&start={start}&max_results={max_results}"
    response = requests.get(base_url + query)
    return response.text


def parse_response(response_text):
    feed = feedparser.parse(response_text)
    papers = []
    for entry in feed.entries:
        published_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
        papers.append({
            'title': entry.title,
            'authors': [author.name for author in entry.authors],
            'published': published_date,  # Simplified for sorting
            'pdf_link': entry.links[1].href,
            'arxiv_link': entry.id
        })
    is_last_page = len(papers) < 20
    return papers, is_last_page

def update_results():
    st.session_state.page_number = max(0, st.session_state.page_number)
    response_text = fetch_papers(st.session_state.search_query, start=st.session_state.page_number)
    st.session_state.papers, st.session_state.is_last_page = parse_response(response_text)

with st.form(key='search_form'):
    search_query = st.text_input('Search Research Papers', '')
    search_button = st.form_submit_button(label='🔍')

if search_button and search_query:
    st.session_state.search_query = search_query
    st.session_state.page_number = 0
    update_results()

col1, col2, col3 = st.columns([1, 1, 5])

# with col1:
#     if st.session_state.page_number > 0:
#         if st.button('Previous'):
#             st.session_state.page_number -= 20
#             update_results()
#     else:
#         st.button('Previous', disabled=True)

# with col2:
#     if st.button('Next', disabled=st.session_state.is_last_page):
#         st.session_state.page_number += 20
#         update_results()

# Toggle sort order function
def toggle_sort_order():
    if st.session_state['sort_order'] == 'ascending':
        st.session_state.papers.sort(key=itemgetter('published'), reverse=True)
        st.session_state['sort_order'] = 'descending'
    else:
        st.session_state.papers.sort(key=itemgetter('published'), reverse=False)
        st.session_state['sort_order'] = 'ascending'

# Sort by Date button with toggle functionality
if st.session_state.papers:
    sort_button_label = "Sort by Date ↓" if st.session_state['sort_order'] == 'ascending' else "Sort by Date ↑"
    if len(st.session_state.papers) > 2:
        if st.button(sort_button_label):
            toggle_sort_order()
            st.rerun()

    for paper in st.session_state.papers:
        with st.container():
            st.markdown(f"""
                <div style="border: 1px solid #ccc; border-radius: 5px; background-color: #192428; padding: 10px; margin-bottom: 5px;">
                    <b style="color: white;">{paper['title']}</b><br>
                    <span style="color: lightgrey;">{", ".join(paper['authors'])}</span><br>
                    <span style="color: lightgrey;">{paper['published']}</span><br>
                    <a href="{paper['pdf_link']}" target="_blank" style="color: #FF5733;">PDF</a> | 
                    <a href="{paper['arxiv_link']}" target="_blank" style="color: #FF5733;">Arxiv</a>
                </div>
            """, unsafe_allow_html=True)

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

st.write(' ')
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