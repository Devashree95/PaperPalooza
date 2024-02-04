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
    
st.title('Welcome to Citation Manager!')
search_term = st.text_input('Enter a keyword or title to search for papers:')

if search_term:
    # Search papers when user enters a search term
    with st.spinner(f'Searching for papers related to "{search_term}"...'):
        papers = search_papers(search_term)
        
        if papers:
            # Get titles for the dropdown
            paper_titles = [paper['title'][0] if 'title' in paper and paper['title'] else 'Title not available' for paper in papers]
            # Dropdown for selecting a paper
            selected_title = st.selectbox('Select a paper:', paper_titles)
            
            # Find the selected paper and display its metadata
            selected_paper = next(paper for paper in papers if paper['title'][0] == selected_title)
            
            if selected_paper:
                title = selected_paper['title'][0] if 'title' in selected_paper and selected_paper['title'] else 'Title not available'
                doi = selected_paper['DOI'] if 'DOI' in selected_paper else 'DOI not available'
                authors = selected_paper['author'] if 'author' in selected_paper else 'Authors not available'
                
                st.subheader(title)
                st.write(f'DOI: {doi}')
                st.write('Authors:')
                st.write(', '.join([f"{author['given']} {author['family']}" for author in authors if 'given' in author and 'family' in author]))
else:
    st.info('Enter a search term to begin.')
