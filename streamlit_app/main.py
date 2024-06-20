import streamlit as st
import yaml
from llm_bot import dummy_bot #contains logic for bot's response
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()
AZURE_ENDPOINT_KEY = os.environ['AZURE_ENDPOINT_KEY']

# Read config yaml file
with open('./streamlit_app/config.yml', 'r') as file:
    config = yaml.safe_load(file)
#print(config)
title = config['streamlit']['title']
avatar = {
    'user': None,
    'assistant': config['streamlit']['avatar']
}

# Set page config
st.set_page_config(
    page_title=config['streamlit']['tab_title'], 
    page_icon=config['streamlit']['page_icon'], 
    )

# Set sidebar
st.sidebar.title("About")
st.sidebar.info(config['streamlit']['about'])

# Set logo
st.image(config['streamlit']['logo'], width=50)

# Set page title
st.title(title)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [] 
    st.session_state.messages.append({
        "role": "assistant", 
        "content": config['streamlit']['assistant_intro_message']
        })

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=avatar[message["role"]]):
        st.markdown(message["content"])


# React to user input
if prompt := st.chat_input("Send a message"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Define the request URI and body
    # (old endpoint) requestURI = 'https://aoaibot.westus.inference.ml.azure.com/score' 
    requestURI = 'https://finalintelligentbot-endpoint.eastus.inference.ml.azure.com/score' #new endpoint

    requestBody = {
        'chat_history': [],
        'chat_input': prompt
    }

    # Define the headers
    headers = {
        'Authorization': f'Bearer {AZURE_ENDPOINT_KEY}',
        'Content-Type': 'application/json'
    }

    # Make the request
    response = requests.post(requestURI, headers=headers, data=json.dumps(requestBody))

    print("Response status:", response.status_code)

    if response.ok:
        parsedResponseBody = response.json()
        with st.chat_message("assistant", avatar=config['streamlit']['avatar']):
            st.markdown(parsedResponseBody['chat_output'])
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": parsedResponseBody['chat_output']})
    else:
        print("Request failed with status", response.status_code)


    
