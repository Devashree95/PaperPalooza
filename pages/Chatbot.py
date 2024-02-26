import time
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import helpers.sidebar
import asyncio

st.set_page_config(
    page_title="Paperpalooza Chatbot",
    page_icon="💬"
)

load_dotenv()

helpers.sidebar.show()

st.write("Get instant answers to your (not too) specific coding questions.")


API_URL = os.getenv("HF_CHAT_API_ENDPOINT")
headers = {"Authorization": "Bearer " + os.getenv("HF_ACCESS_TOKEN")}

messages = []

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def get_response(payload):
    output = query(payload)
    while 'error' in output and output['error'] == 'Model is currently loading':
        print('The model is loading, please wait...')
        estimated_time = output.get('estimated_time', 10)  # Default to 10 seconds if no time provided
        time.sleep(min(estimated_time, 30))  # Wait for the estimated time but not more than 30 seconds
        output = query(payload)  # Retry to get the response
    
    return output

system_prompt = """
You are a friendly and knowledgeable assistant. Always provide respectful and concise answers. Try to keep the responses short and to the point.
"""

# Ensure the session state is initialized
if "messages" not in st.session_state:
    initial_message = [{"role": "system",
                         "content": system_prompt}]
    st.session_state.messages = initial_message

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
        message_placeholder = "Thinking..." # st.empty()

        query_payload = {"inputs": system_prompt+messages[-1]['content'],
                  "parameters": {"max_new_tokens": 250}}
        response = get_response(query_payload)
        messages.append({"role": "assistant", "content": response[0]['generated_text']})
        st.session_state.messages = messages
        st.markdown(response[0]['generated_text'])
    return messages


if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    asyncio.run(chat(st.session_state.messages))
    # with st.chat_message("user"):
    #     st.markdown(prompt)
    # query_payload = {"inputs": system_prompt+prompt,
    #              "parameters": {"max_new_tokens": 250}}
    # # messages.append(get_response(query_payload))
    # response = get_response(query_payload) #json.loads(get_response(query_payload))
    # with st.chat_message("assistant"):
    #     st.markdown(response[0]['generated_text'])
