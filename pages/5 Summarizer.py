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


st.set_page_config(
	page_title="Text Summarizer",
	page_icon="📄",
	layout="wide"
)

#helpers.sidebar.show()

# Streamlit UI setup

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
     