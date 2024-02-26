import streamlit as st
import requests
import feedparser
import helpers.sidebar
from datetime import datetime
from urllib.parse import quote
import streamlit.components.v1 as components
from PIL import Image
import base64

helpers.sidebar.show()

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
					<span style="padding:10px; flex:2;">Username</span>
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

def fetch_papers(search_query, start=0, max_results=10):
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=all:{quote(search_query)}&start={start}&max_results={max_results}"
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
            'published': f"Published: {published_date}",
            'pdf_link': entry.links[1].href,
            'arxiv_link': entry.id
        })
    is_last_page = len(papers) < 10  # Adjust according to your max_results
    return papers, is_last_page

def update_results():
    # Make sure to clamp the page number to 0 to avoid negative values
    st.session_state.page_number = max(0, st.session_state.page_number)
    response_text = fetch_papers(st.session_state.search_query, start=st.session_state.page_number)
    st.session_state.papers, st.session_state.is_last_page = parse_response(response_text)


with st.form(key='search_form'):
    search_query = st.text_input('Search Research Papers', '')
    search_button = st.form_submit_button(label='🔍')

if search_button and search_query:
    st.session_state.search_query = search_query
    st.session_state.page_number = 0  # Reset to first page with new search
    update_results()

col1, col2, col3 = st.columns([1, 1, 5])

with col1:
    # Enable 'Previous' only if page_number is greater than 0
    if st.session_state.page_number > 0:
        if st.button('Previous'):
            # Subtract from page_number and update results
            st.session_state.page_number -= 10  # Assuming 10 is your max_results value
            update_results()
    else:
        # Optionally, display a disabled 'Previous' button for better UX
        st.button('Previous', disabled=True)

with col2:
    # No change for 'Next' button logic
    if st.button('Next', disabled=st.session_state.is_last_page):
        st.session_state.page_number += 10
        update_results()

if st.session_state.papers:
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

