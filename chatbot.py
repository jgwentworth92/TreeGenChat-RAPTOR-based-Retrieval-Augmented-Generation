from fastapi import requests
from openai import OpenAI
import requests
from typing import Dict, List
import streamlit as st


def send_message(conversation_id: str, message: str) -> Dict:
    try:
        payload = {"conversation_id": conversation_id, "message": message}
        response = requests.post("http://localhost:8000/RAG/rag_chain_chat", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return {"response": "Error"}


def send_message_agent(conversation_id: str, message: str) -> Dict:
    try:
        payload = {"conversation_id": conversation_id, "message": message}
        response = requests.post("http://localhost:8000/RAG/agent_rag_chain_chat", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return {"response": "Error"}


def create_conversation(user_sub: str) -> str:
    new_conversation = requests.post(
        "http://localhost:8000/RAG/create-conversation",
        json={
            "user_sub": user_sub
        }
    ).json()
    return new_conversation['id']


def get_conversations(user_id: str) -> List[str]:
    try:
        response = requests.get(
            "http://localhost:8000/RAG/user-conversations", params={"user_sub": user_id})
        response.raise_for_status()

        # Parse JSON response and extract only the conversation IDs
        conversations_data = response.json()
        conversation_ids = [conversation['id'] for conversation in conversations_data]

        return conversation_ids
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return []


def get_messages(conversation_id: str) -> List[Dict]:
    try:
        response = requests.get(
            "http://localhost:8000/RAG/get-conversation-messages", params={"conversation_id": conversation_id})

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error occurred: {err}")
        return []


def display_conversation_messages(selected_conversation: str) -> List[Dict]:
    st.write(f"**Selected Conversation**: {selected_conversation}")

    messages = get_messages(selected_conversation)

    for message in messages:
        with st.chat_message("user"):
            st.write(message["user_message"])
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
