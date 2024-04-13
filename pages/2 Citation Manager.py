import streamlit as st
import helpers.sidebar
import requests
import streamlit.components.v1 as components
from datetime import datetime
from PIL import Image
import base64
from helpers import connection as conn
from psycopg2 import IntegrityError
import uuid

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

def get_user_id(email):
    select_query = f"select user_id from user_details where email= '{email}'"
    cur.execute(select_query)
    return cur.fetchall()[0][0]

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
    app = 'citation'

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
    select_query = f"select cm.*, a.first_name from comments cm join (select first_name, email from user_details) as a on cm.user_email = a.email where email in ({placeholders}) and app = 'citation'"
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

def save_citation_to_db(user_id,title,date_saved_on, doc_type, format, citation):
    try:
        # Assuming your table is named 'citations' and has at least two columns: 'document_id' and 'citation_text'
        insert_query = f"INSERT INTO citations (user_id, title, date_saved_on, doc_type, format, citation) VALUES ('{user_id}', '{title}', '{date_saved_on}', '{doc_type}', '{format}', '{citation}' )"
        
        cur.execute(insert_query)
        connection.commit()
        st.success("Citation saved successfully!")
    except IntegrityError as e:
        # Rollback the transaction so you can execute another command
        connection.rollback()
        # Check if the error message is about a duplicate key
        if "duplicate key value violates unique constraint" in str(e):
            st.warning("This citation already exists.")
        else:
            st.error(f"Failed to save citation: {e}")
    except Exception as e:
        st.error(f"Failed to save citation: {e}")
        connection.rollback()

def get_citations(userid, start_date, end_date):
    select_query = f"select title, citation from citations where user_id= '{userid}' and date_saved_on >= '{start_date}' and date_saved_on <= '{end_date}'"
    cur.execute(select_query)
    citations = cur.fetchall()
    return citations

def delete_citation(title):
    try:
        delete_query = f"DELETE FROM citations WHERE title = '{title}'"
        cur.execute(delete_query)
        connection.commit()
        st.success("Citation deleted successfully!")
    except Exception as e:
        st.error(f"Failed to delete citation: {e}")
        connection.rollback()
    
set_background_from_local_file('./images/dark_background.png')


st.markdown(f"""
			<a href="/" style="color:white;text-decoration: none;">
				<div style="display:table;margin-top:-15 rem;margin-left:0%; display: flex;">
			  		<img src="{image_base64}" alt="PaperPalooza Logo" style="width:50px;height:40px;margin-left:750px; flex:2;" </img>
					<span style="padding:10px; flex:2;">{st.session_state.username}</span>
				</div>
			</a>
			<br>
				""", unsafe_allow_html=True)

def search_papers(search_term, document_type):
    if document_type == 'Book':
        url = f'https://api.crossref.org/works?query={search_term}&filter=type:book'
    elif document_type == 'Journal Article':
        url = f'https://api.crossref.org/works?query={search_term}&filter=type:journal-article'
    elif document_type == 'Report':
        url = f'https://api.crossref.org/works?query={search_term}&filter=type:report'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['message']['items']
    else:
        st.error(f'Failed to retrieve data: {response.status_code}')
        return []
    
def display_paper_info(selected_paper):
    if selected_paper:
        title = selected_paper['title'][0] if 'title' in selected_paper and selected_paper['title'] else 'Title not available'
        doi = selected_paper['DOI'] if 'DOI' in selected_paper else 'DOI not available'
        authors = selected_paper['author'] if 'author' in selected_paper else (selected_paper['editor'] if 'editor' in selected_paper else 'Author info not available')
        publisher = selected_paper['publisher'] if 'publisher' in selected_paper else ''
        
        st.subheader(title)
        st.write(f'DOI: {doi}')
        st.write('Authors:')
        if authors == 'Author info not available':
            st.write(authors)
        else:
            st.write(', '.join([f"{author['given']} {author['family']}" for author in authors if 'given' in author and 'family' in author]))

def format_citation(selected_paper, citation_format, document_type):
    if not selected_paper:  
        return "No paper selected."
    
    # Extract information from selected_paper
    # Journal Article
    title = selected_paper['title'][0] if 'title' in selected_paper and selected_paper['title'] else ''
    authors = selected_paper['author'] if 'author' in selected_paper else ''
    doi = selected_paper['DOI'] if 'DOI' in selected_paper else ''
    container_title = selected_paper['container-title'] if 'container-title' in selected_paper else ''
    publisher = selected_paper['publisher'] if 'publisher' in selected_paper else ''
    volume = selected_paper['volume'] if 'volume' in selected_paper else ''
    page = selected_paper['page'] if 'page' in selected_paper else ''
    source = selected_paper['source'] if 'source' in selected_paper else ''
    publisher_location = selected_paper['publisher-location'] if 'publisher-location' in selected_paper else ''

    if authors == '':
            formatted_authors = " "

    if len(authors) > 0:
        if authors == '':
            formatted_authors = " "
        elif len(authors) == 1:
            formatted_authors = f"{authors[0]['family']}, {authors[0]['given']}."
        elif len(authors) == 2:
            formatted_authors = f"{authors[0]['family']}, {authors[0]['given']} and {authors[1]['family']}, {authors[1]['given']}."
        else:
            formatted_authors = ', '.join([f"{author['family']}, {author['given']}." for author in authors[:-1]]) + f", and {authors[-1]['family']}, {authors[-1]['given']}."

    
    if document_type == 'Journal Article':
        if citation_format == 'APA':
            # Format the citation in APA style 
            if authors == '':
                formatted_authors = " "
            elif len(authors) == 1:
                formatted_authors = f"{authors[0]['family']}, {authors[0]['given'][0]}."
            elif len(authors) == 2:
                formatted_authors = f"{authors[0]['family']}, {authors[0]['given'][0]} & {authors[1]['family']}, {authors[1]['given'][0]}."
            else:
                formatted_authors = ', '.join([f"{author['family']}, {author['given'][0]}." for author in authors[:-1]]) + f", & {authors[-1]['family']}, {authors[-1]['given'][0]}."

            if authors == "":
                citation = f"{title}. ({selected_paper['issued']['date-parts'][0][0]}). {container_title[0]}, {volume}, {page}. https://doi.org/{doi}."
            else:
                citation = f"{formatted_authors} ({selected_paper['issued']['date-parts'][0][0]}). {title}. {container_title[0]}, {volume}, {page}. https://doi.org/{doi}."
        elif citation_format == 'MLA':
            # Format the citation in MLA style (placeholder)
            citation = f"{formatted_authors} \"{title}.\" {container_title[0]}, vol.{volume}, {publisher}, {selected_paper['issued']['date-parts'][0][0]}, pp. {page}. {source}, https://doi.org/{doi}."
        elif citation_format == 'Chicago':
            citation = f"{formatted_authors} \"{title}.\" {container_title[0]} {volume} ({selected_paper['issued']['date-parts'][0][0]}): {page}. https://doi.org/{doi}."
        else:
            citation = "Citation format not supported."
    elif document_type == 'Book':
        # Book
        editors = selected_paper['editor'] if 'editor' in selected_paper else ''
        if len(editors) == 1:
            formatted_editors = f"{editors[0]['family']}, {editors[0]['given']}."
        elif len(editors) == 2:
            formatted_editors = f"{editors[0]['family']}, {editors[0]['given']} and {editors[1]['family']}, {editors[1]['given']}."
        else:
            formatted_editors = ', '.join([f"{editor['family']}, {editor['given']}." for editor in editors[:-1]]) + f", and {editors[-1]['family']}, {editors[-1]['given']}."

        
        url = selected_paper['resource']['primary']['URL'] if 'resource' in selected_paper else ''
    
        if citation_format == 'APA':
            editors = selected_paper['editor'] if 'editor' in selected_paper else ''
            if len(editors) == 1:
                formatted_editors = f"{editors[0]['family']}, {editors[0]['given'][0]}."
            elif len(editors) == 2:
                formatted_editors = f"{editors[0]['family']}, {editors[0]['given'][0]} & {editors[1]['family']}, {editors[1]['given'][0]}."
            else:
                formatted_editors = ', '.join([f"{editor['family']}, {editor['given'][0]}." for editor in editors[:-1]]) + f", & {editors[-1]['family']}, {editors[-1]['given'][0]}."

            # Format the citation in APA style (placeholder)
            citation = f"{formatted_editors} ({selected_paper['issued']['date-parts'][0][0]}). {title}. {publisher}. {url}."
        elif citation_format == 'MLA':
            # Format the citation in MLA style (placeholder)
            citation = f"{editors[0]['family']} ,{editors[0]['given']}, et al. {title}. {publisher}, {selected_paper['issued']['date-parts'][0][0]}, {url}."
        elif citation_format == 'Chicago':
            # Format the citation in Chicago style (placeholder)
             citation = f"{formatted_editors}  {title}. {publisher}, {selected_paper['issued']['date-parts'][0][0]}. {url}."
        else:
            citation = "Citation format not supported."
    else:
        url = selected_paper['resource']['primary']['URL'] if 'resource' in selected_paper else ''
        if citation_format == 'APA':
            # Format the citation in APA style
            date_list= selected_paper['issued']['date-parts'][0]
            date_obj = datetime(year=date_list[0], month=date_list[1], day=date_list[2])
            today_date = datetime.now()

            # Format the date
            formatted_today_date = today_date.strftime("%B %d, %Y")

            # Format the datetime object to the desired string format
            formatted_date = date_obj.strftime("%Y, %B %d")
            citation = f"{', '.join([author['family'] for author in authors])}. ({formatted_date}). {title}. {publisher}. Retrieved {formatted_today_date}, from {url}."
        elif citation_format == 'MLA':
            # Format the citation in MLA style
            date_list= selected_paper['issued']['date-parts'][0]
            date_obj = datetime(year=date_list[0], month=date_list[1], day=date_list[2])
            formatted_date = date_obj.strftime("%d %b. %Y")

            citation = f"{authors[0]['family']}, {authors[0]['given']}. {title}, {publisher}, {formatted_date}, {url[7:]}."
        elif citation_format == 'Chicago':
            # Format the citation in Chicago style
            date_list= selected_paper['issued']['date-parts'][0]
            date_obj = datetime(year=date_list[0], month=date_list[1], day=date_list[2])
            formatted_date = date_obj.strftime("%B %d, %Y")
            citation = f"{authors[0]['family']}, {authors[0]['given']}. \"{title}.\" {publisher_location}: {publisher}, {formatted_date}. {url}."
        else:
            citation = "Citation format not supported."
    
    return citation

def display_formatted_citation(formatted_citation):
    # Custom HTML and JavaScript to style the citation box and handle the copy-to-clipboard functionality
    citation_box_html = f"""
    <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; position: relative; margin: 15px 0;
    background-color: gray;">
        <span id="citation-text" style="margin-right: 30px; color: white; padding: 10px;">{formatted_citation}</span>
        <button onclick="copyToClipboard()" style="position: absolute; right: 0px; left: 655px; top: 6px; cursor: pointer; font-size: 20px; border: none; background: none;">
            📋
        </button>
    </div>
    <script>
        function copyToClipboard() {{
            const text = document.getElementById('citation-text').innerText;
            navigator.clipboard.writeText(text).then(function() {{
                alert('Copying to clipboard was successful!');
            }}, function(err) {{
                alert('Could not copy text: ', err);
            }});
        }}
    </script>
    """
    components.html(citation_box_html, height=100)


st.title('Welcome to Citation Manager!')

document_type = st.selectbox(
    'Select the type of document:',
    ['Journal Article', 'Report', 'Book'],
    key='document_type'
)

search_term = st.text_input('Enter a keyword or title to search for papers:')

if search_term:
    # Create a unique session key for each search term
    session_key = f'session_{document_type}_{search_term}'
    if session_key not in st.session_state:
        st.session_state[session_key] = {'papers': None, 'selected_title': None, 'selected_paper': None}
    
    # Fetch papers if not already fetched or if the search term has changed
    if st.session_state[session_key]['papers'] is None or search_term != st.session_state.get('last_search', ''):
       with st.spinner(f'Searching for {document_type.lower()}s related to "{search_term}"...'):
            papers = search_papers(search_term, document_type)
            st.session_state[session_key]['papers'] = papers
            st.session_state['last_search'] = search_term
            if papers:
                st.session_state[session_key]['selected_title'] = papers[0]['title'][0] if 'title' in papers[0] and papers[0]['title'] else 'Title not available'
                st.session_state[session_key]['selected_paper'] = papers[0]

    if st.session_state[session_key]['papers']:
        paper_titles = [paper['title'][0] if 'title' in paper and paper['title'] else 'Title not available' for paper in st.session_state[session_key]['papers']]
        
        # Dropdown for selecting a paper
        selected_title = st.selectbox(
            'Select a paper:',
            paper_titles,
            key=f'dropdown',
        )
        
        citation_format = st.selectbox(
        'Select citation format:',
        ['APA', 'MLA', 'Chicago'],
        key=f'citation_format_{session_key}'
        )

        # Update selected paper and display its metadata
        if selected_title != st.session_state[session_key]['selected_title']:
            st.session_state[session_key]['selected_title'] = selected_title
            st.session_state[session_key]['selected_paper'] = next(paper for paper in st.session_state[session_key]['papers'] if paper['title'][0] == selected_title)
        
        display_paper_info(st.session_state[session_key]['selected_paper'])
        # Get the formatted citation
        formatted_citation = format_citation(st.session_state[session_key]['selected_paper'], citation_format, document_type)
    
        # Display the formatted citation
        st.subheader('Formatted Citation:')
        #st.write(formatted_citation)
        display_formatted_citation(formatted_citation)

        if st.button('Save Citation'):
            # Here, we use DOI as a unique identifier for the document. Adjust as needed.
            user_id = get_user_id(st.session_state['username'])
            title = st.session_state[session_key]['selected_paper'].get('title', 'N/A')[0]
            citation = formatted_citation
            date_saved_on = today = datetime.today().date()
            doc_type = document_type
            format = citation_format
            save_citation_to_db(user_id, title, date_saved_on, doc_type, format, citation)
else:
    st.info('Enter a search term to begin.')

st.subheader("Citation History:")
st.write('Filter by Date:')
today = datetime.today().date()
col1, col2 = st.columns([4, 4])
with col1:
    start_date = st.date_input('Start date', today)
with col2:
    end_date = st.date_input('End date', today)
user_id = get_user_id(st.session_state['username'])
citations = get_citations(user_id, start_date, end_date)
if citations:
    for title, citation_text in citations:
        col1, col2 = st.columns([8, 2])
        # Display each citation
        with col1:
            st.markdown(f"**{title}**")
            st.write(citation_text)
        with col2:
            if st.button("Delete", key=f"delete_{title}"):
                delete_citation(title)
                st.experimental_rerun()
        st.markdown("---")
else:
    st.write('No Citation History available.')

if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

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

