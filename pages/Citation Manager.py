import streamlit as st
import helpers.sidebar
import requests
import streamlit.components.v1 as components


helpers.sidebar.show()

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
        authors = selected_paper['author'] if 'author' in selected_paper else 'Authors not available'
        publisher = selected_paper['publisher'] if 'publisher' in selected_paper else ''
        
        st.subheader(title)
        st.write(f'DOI: {doi}')
        st.write('Authors:')
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

    
    if document_type == 'Journal Article':
        if citation_format == 'APA':
            # Format the citation in APA style 
            citation = f"{' and '.join([author['family'] + ', ' + author['given'][0] + '. ' for author in authors])} ({selected_paper['issued']['date-parts'][0][0]}). {title}. {container_title[0]}, {volume}, {page}. https://doi.org/{doi}"
        elif citation_format == 'MLA':
            # Format the citation in MLA style (placeholder)
            citation = f"{' and '.join([author['family'] +', '+ author['given']  for author in authors])}. \"{title}.\" {container_title[0]}, vol.{volume}, {publisher}, {selected_paper['issued']['date-parts'][0][0]}, pp. {page}. {source}, https://doi.org/{doi}"
        elif citation_format == 'Chicago':
            citation = f"{' and '.join([author['family'] +', '+ author['given']  for author in authors])}. \"{title}.\" {container_title[0]} {volume} ({selected_paper['issued']['date-parts'][0][0]}): {page}. https://doi.org/{doi}"
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
            citation = f"{formatted_editors} ({selected_paper['issued']['date-parts'][0][0]}). {title}. {publisher}. {url}"
        elif citation_format == 'MLA':
            # Format the citation in MLA style (placeholder)
            citation = f"{editors[0]['family']} ,{editors[0]['given']}, et al. {title}. {publisher}, {selected_paper['issued']['date-parts'][0][0]}, {url} "
        elif citation_format == 'Chicago':
            # Format the citation in Chicago style (placeholder)
             citation = f"{formatted_editors}  {title}. {publisher}, {selected_paper['issued']['date-parts'][0][0]}. {url}"
        else:
            citation = "Citation format not supported."
    else:
        if citation_format == 'APA':
            # Format the citation in APA style (placeholder)
            citation = f"{', '.join([author['family'] for author in authors])} ({selected_paper['issued']['date-parts'][0][0]}). {title}. doi:{doi}"
        elif citation_format == 'MLA':
            # Format the citation in MLA style (placeholder)
            citation = f"{', '.join([author['family'] for author in authors])}. \"{title}.\" doi:{doi}"
        elif citation_format == 'Chicago':
            # Format the citation in Chicago style (placeholder)
            citation = f"{', '.join([author['family'] for author in authors])}, {title}. doi:{doi}"
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
            index=paper_titles.index(st.session_state[session_key]['selected_title']),
            key=f'dropdown_{session_key}',
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
else:
    st.info('Enter a search term to begin.')