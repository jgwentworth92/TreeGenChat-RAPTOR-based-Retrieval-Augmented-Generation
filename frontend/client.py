from typing import Dict, List

import requests
from streamlit.runtime.uploaded_file_manager import UploadedFile

SERVER_URL = "http://fast-api-service:8000/RAG"


def get_fastapi_status(server_url: str = "http://fast-api-service:8000"):
    """Access FastAPI /docs endpoint to check if server is running"""
    try:
        response = requests.get(f"{server_url}/docs")
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False


# Assuming SERVER_URL is defined elsewhere in your code.


def post_store_arxiv(arxiv_ids: str, server_url: str = SERVER_URL, max_iteration: int = 5):
    try:
        pdf_url = arxiv_ids[0]
        # Prepare the JSON data to send in the request body
        data = {
            "pdf_filename": pdf_url,
            "max_iteration": max_iteration
        }
        print(data)
        # Construct the endpoint URL (without query parameters)
        full_url = f"{server_url}/add-documents-internet"
        # Make the POST request with JSON data
        response = requests.post(full_url, json=data)
        response.raise_for_status()  # This will raise an exception for HTTP error responses
        return response.json()
    except requests.exceptions.RequestException as err:
        # Handle request errors (e.g., network issues, server not responding)
        return {"response": "Error", "detail": str(err)}


def post_store_pdfs(pdf_file) -> Dict:
    """Send POST request to FastAPI /store_pdfs endpoint"""
    files = {'pdf_file': (pdf_file.name, pdf_file, 'application/pdf')}
    data = {'max_iteration': 5}  # Example, adjust as needed
    response = requests.post(f"{SERVER_URL}/add-documents-upload", files=files, data=data)
    response.raise_for_status()
    return response.json()


def get_rag_summary(
        rag_query: str,


):
    """Send GET request to FastAPI /rag_summary endpoint"""
    payload = {
   "question": rag_query
    }
    response = requests.post(f"{SERVER_URL}/rag_chain_with_source", json=payload)
    response.raise_for_status()
    return response


def send_message(conversation_id: str, message: str) -> Dict:
    try:
        payload = {"conversation_id": conversation_id, "message": message}
        response = requests.post(f"{SERVER_URL}/rag_chain_chat", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"response": "Error"}


def get_all_documents_file_name():
    """Send GET request to FastAPI /documents endpoint"""
    response = requests.get(f"{SERVER_URL}/documents")
    return response


def get_conversations(user_id: str) -> List[str]:
    try:
        response = requests.get(
            f"{SERVER_URL}/user-conversations", params={"user_sub": user_id})
        response.raise_for_status()

        # Parse JSON response and extract only the conversation IDs
        conversations_data = response.json()
        conversation_ids = [conversation['id'] for conversation in conversations_data]

        return conversation_ids
    except requests.exceptions.RequestException as err:
        return []


def create_conversation(user_sub: str) -> str:
    new_conversation = requests.post(
        f"{SERVER_URL}/create-conversation",
        json={
            "user_sub": user_sub
        }
    ).json()
    return new_conversation['id']


def get_messages(conversation_id: str) -> List[Dict]:
    try:
        response = requests.get(
            f"{SERVER_URL}/get-conversation-messages", params={"conversation_id": conversation_id})

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return []
