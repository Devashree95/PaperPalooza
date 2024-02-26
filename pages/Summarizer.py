import streamlit as st
import requests
import os
import helpers.sidebar
from PIL import Image
import base64
from transformers import pipeline

st.set_page_config(
	page_title="ETD Summarizer",
	page_icon="📄",
	layout="wide"
)

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


#api_token = ""
#API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
#headers = {"Authorization": f"Bearer{api_token}"}

#def query(payload):
#    response = requests.post(API_URL, headers=headers, json=payload)
#    return response.json()

@st.cache_resource(show_spinner=False)
def load_summarizer():
    model = pipeline("summarization",  model="facebook/bart-large-cnn", framework="pt")
    return model


def generate_chunks(inp_str):
    max_chunk = 500
    inp_str = inp_str.replace('.', '.<eos>')
    inp_str = inp_str.replace('?', '?<eos>')
    inp_str = inp_str.replace('!', '!<eos>')
    
    sentences = inp_str.split('<eos>')
    current_chunk = 0 
    chunks = []
    for sentence in sentences:
        if len(chunks) == current_chunk + 1: 
            if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            chunks.append(sentence.split(' '))

    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])
    return chunks


summarizer = load_summarizer()
st.title("Text Summarizer")
st.write(" ")

st.markdown("Welcome to Text Summarizer!")
st.write(" ")
sentence = st.text_area('Please paste your text below :', height=250)
button = st.button("Summarize")
st.write(" ")
st.write(" ")
st.write("Summary:")

max = st.sidebar.slider('Select max', 50, 500, step=10, value=200)
min = st.sidebar.slider('Select min', 10, 450, step=10, value=100)

with st.spinner("Generating Summary..."):
    if button and sentence:
        chunks = generate_chunks(sentence)
        res = summarizer(chunks,
                         max_length=max, 
                         min_length=min)
        text = ' '.join([summ['summary_text'] for summ in res])
        # st.write(result[0]['summary_text'])
        st.write(text)