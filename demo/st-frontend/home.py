import streamlit as st
import time
import os
import requests
from typing import Dict, List
API_URL = os.getenv("API_URL", "http://0.0.0.0:8000/agents")


def get_agent(agent_id: str) -> Dict:
    try:
        response = requests.get(API_URL + "/get-agent",
                                params={"agent_id": agent_id})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return {}


def get_agents() -> List[Dict]:
    try:
        response = requests.get(API_URL + "/get-agents")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return []


def get_conversations(agent_id: str) -> List[Dict]:
    try:
        response = requests.get(
            API_URL + "/get-conversations", params={"agent_id": agent_id})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return []


def get_messages(conversation_id: str) -> List[Dict]:
    try:
        response = requests.get(
            API_URL + "/get-conversation-messages", params={"conversation_id": conversation_id})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return []


def send_message(agent_id: str, message: str) -> Dict:
    try:
        payload = {"conversation_id": agent_id, "message": message}
        response = requests.post(API_URL + "/chat-agent", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return {"response": "Error"}


def create_agent(context: str, first_message: str, response_shape: str, instructions: str) -> None:
    new_agent = requests.post(
        API_URL + "/create-agent",
        json={
            "context": context,
            "first_message": first_message,
            "response_shape": response_shape,
            "instructions": instructions
        }
    ).json()
    st.success(f"New agent created with ID: {new_agent['id']}")


def create_predetermined_agent(agent_name: str) -> None:
    agent = requests.post(API_URL + f"/{agent_name}").json()
    st.success(f" Preconfigured Agent with ID: {agent['id']}")
    return agent['id']


def create_conversation(selected_agent: str) -> None:
    new_conversation = requests.post(
        API_URL + "/create-conversation",
        json={
            "agent_id": selected_agent
        }
    ).json()
    st.success(f"New conversation created with ID: {new_conversation['id']}")


def display_conversation_messages(selected_conversation: str, agent_first_message: str) -> List[Dict]:
    st.write(f"**Selected Conversation**: {selected_conversation}")

    messages = get_messages(selected_conversation)
    with st.chat_message("assistant"):
        st.write(agent_first_message)

    for message in messages:
        with st.chat_message("user"):
            st.write(message["user_message"])
        if message["agent_message"] == agent_first_message:
            continue
        with st.chat_message("assistant"):
            st.write(message["agent_message"])

def main():
    st.set_page_config(page_title="🤗💬 AIChat")
    st.title("Chat Interface")

    # Sidebar for conversation management
    st.sidebar.title("Conversations Management")
    user_id = st.sidebar.text_input("Enter your user ID to manage conversations:", "")

    # Initialize session state for new conversation ID and selected conversation ID
    if 'new_conversation_id' not in st.session_state:
        st.session_state['new_conversation_id'] = None
    if 'selected_conversation_id' not in st.session_state:
        st.session_state['selected_conversation_id'] = None

    if user_id:
        if st.sidebar.button("Create New Conversation"):
            new_conversation_id = create_conversation(user_id)
            st.sidebar.success(f"New conversation created: {new_conversation_id}")
            st.session_state['new_conversation_id'] = new_conversation_id
            st.session_state['selected_conversation_id'] = new_conversation_id

        existing_conversations = get_conversations(user_id)
        conversation_options = [""] + [conv for conv in existing_conversations]
        if st.session_state['new_conversation_id']:
            conversation_options.append(st.session_state['new_conversation_id'])
        # Use session_state to pre-select the conversation
        selected_conversation_id = st.sidebar.selectbox(
            "Select an existing conversation:", conversation_options, index=conversation_options.index(st.session_state['selected_conversation_id']) if st.session_state['selected_conversation_id'] in conversation_options else 0)
        st.session_state['selected_conversation_id'] = selected_conversation_id

    # Main chat interface
    st.write(
        "This is a chat interface for the selected agent and conversation. You can send messages to the agent and see its responses.")

    if st.session_state['selected_conversation_id']:
        display_conversation_messages(st.session_state['selected_conversation_id'])

        # User-provided prompt
        prompt = st.chat_input("Enter a message:")
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)
            with st.spinner("Thinking..."):
                response = send_message(st.session_state['selected_conversation_id'], prompt)
                with st.chat_message("assistant"):
                    st.write(response)
    else:
        st.write("Please enter a message.")

if __name__ == "__main__":
    main()
