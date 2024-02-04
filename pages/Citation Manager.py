import streamlit as st
import helpers.sidebar
from pyzotero import zotero
import requests


helpers.sidebar.show()

def search_papers(search_term):
    url = f'https://api.crossref.org/works?query={search_term}'
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
        authors = selected_paper['author'] if 'author' in selected_paper else 'Authors not available'
        
        st.subheader(title)
        st.write(f'DOI: {doi}')
        st.write('Authors:')
        st.write(', '.join([f"{author['given']} {author['family']}" for author in authors if 'given' in author and 'family' in author]))

st.title('Welcome to Citation Manager!')
search_term = st.text_input('Enter a keyword or title to search for papers:')

if search_term:
    # Create a unique session key for each search term
    session_key = f'session_{search_term}'
    if session_key not in st.session_state:
        st.session_state[session_key] = {'papers': None, 'selected_title': None, 'selected_paper': None}
    
    # Fetch papers if not already fetched or if the search term has changed
    if st.session_state[session_key]['papers'] is None or search_term != st.session_state.get('last_search', ''):
        with st.spinner(f'Searching for papers related to "{search_term}"...'):
            papers = search_papers(search_term)
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
            index=paper_titles.index(st.session_state[session_key]['selected_title']),
            key=f'dropdown_{session_key}',
        )
        
        # Update selected paper and display its metadata
        if selected_title != st.session_state[session_key]['selected_title']:
            st.session_state[session_key]['selected_title'] = selected_title
            st.session_state[session_key]['selected_paper'] = next(paper for paper in st.session_state[session_key]['papers'] if paper['title'][0] == selected_title)
        
        display_paper_info(st.session_state[session_key]['selected_paper'])
else:
    st.info('Enter a search term to begin.')