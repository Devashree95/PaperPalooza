import streamlit as st
from dotenv import load_dotenv
import helpers.sidebar
import asyncio

import helpers.chatbot.util as util
import helpers.chatbot.prompts as prompts

st.set_page_config(
    page_title="Paperpalooza Chatbot",
    page_icon="💬"
)

load_dotenv()

helpers.sidebar.show()

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
if prompt := st.chat_input("Ask a programming question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    asyncio.run(chat(st.session_state.messages))
