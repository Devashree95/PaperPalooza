import streamlit as st
from dotenv import load_dotenv
import helpers.sidebar
import asyncio

import helpers.chatbot.util as util
import helpers.chatbot.prompts as prompts
from PIL import Image
import base64

st.set_page_config(
    page_title="Paperpalooza Chatbot",
    page_icon="💬"
)

load_dotenv()

#helpers.sidebar.show()

logo = "./images/paperpalooza.png"
image = Image.open(logo)

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


st.write("Get instant answers to your (not too) specific coding questions.")


# Ensure the session state is initialized
if "messages" not in st.session_state:
    initial_messages = [{"role": "system",
                         "content": prompts.quick_chat_system_prompt()}]
    st.session_state.messages = initial_messages

# Print all messages in the session state
for message in [m for m in st.session_state.messages if m["role"] != "system"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat with the LLM, and update the messages list with the response.
# Handles the chat UI and partial responses along the way.
async def chat(messages):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        messages = await util.run_conversation(messages, message_placeholder)
        st.session_state.messages = messages
    return messages


# React to the user prompt
if prompt := st.chat_input("Ask your research related question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    asyncio.run(chat(st.session_state.messages))
