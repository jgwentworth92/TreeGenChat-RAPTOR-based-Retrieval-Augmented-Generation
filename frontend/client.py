from typing import Dict, List

import requests
from streamlit.runtime.uploaded_file_manager import UploadedFile

SERVER_URL = "http://fastapi:8000/RAG"

import requests
from typing import List, Dict

SERVER_URL = "http://fastapi:8000/RAG"


def get_auth_token(server_url: str, username: str, password: str) -> str:
    """Request an authentication token from the FastAPI server."""
    try:
        auth_url = f"{server_url}/token"
        response = requests.post(auth_url, data={"username": username, "password": password})
        response.raise_for_status()
        token_details = response.json()
        return token_details["access_token"]
    except requests.exceptions.RequestException as err:
        print(f"Error obtaining auth token: {err}")
        return ""


def get_fastapi_status( server_url: str = "http://fastapi:8000"):
    """Access FastAPI /docs endpoint to check if server is running, with authentication."""

    try:
        response = requests.get(f"{server_url}/docs")
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False


def post_store_arxiv(arxiv_ids: List[str], token: str, server_url: str = SERVER_URL, max_iteration: int = 5, ):
    """Store arXiv PDFs, with authentication."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        pdf_url = arxiv_ids[0]
        data = {"pdf_filename": pdf_url, "max_iteration": max_iteration}
        full_url = f"{server_url}/add-documents-internet"
        response = requests.post(full_url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"response": "Error", "detail": str(err)}


def post_store_pdfs(pdf_file, token: str, server_url: str = SERVER_URL, ):
    """Send PDFs to store, with authentication."""
    headers = {"Authorization": f"Bearer {token}"}
    files = {'pdf_file': (pdf_file.name, pdf_file, 'application/pdf')}
    data = {'max_iteration': 5}
    response = requests.post(f"{server_url}/add-documents-upload", files=files, data=data, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"response": "Error", "detail": str(err)}


def get_rag_summary(rag_query: str, token: str, server_url: str = SERVER_URL):
    """Get RAG summary, with authentication."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"question": rag_query}
    response = requests.post(f"{server_url}/rag_chain_with_source", json=payload, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"response": "Error", "detail": str(err)}


def send_message(conversation_id: str, message: str, token: str, server_url: str = SERVER_URL):
    """Send a message, with authentication."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"conversation_id": conversation_id, "message": message}
    response = requests.post(f"{server_url}/rag_chain_chat", json=payload, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"response": "Error", "detail": str(err)}


def get_all_documents_file_name(token: str, server_url: str = SERVER_URL):
    """Get all documents file names, with authentication."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{server_url}/documents", headers=headers)
    try:
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"response": "Error", "detail": str(err)}


def get_conversations( user_id: str,token: str, server_url: str = SERVER_URL) -> List[str]:
    """Get user conversations, with authentication."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{server_url}/user-conversations", params={"user_sub": user_id}, headers=headers)
        response.raise_for_status()
        conversations_data = response.json()
        return [conversation['id'] for conversation in conversations_data]
    except requests.exceptions.RequestException as err:
        return []


def create_conversation( user_sub: str, token: str,server_url: str = SERVER_URL) -> str:
    """Create a conversation, with authentication."""
    headers = {"Authorization": f"Bearer {token}"}
    new_conversation = requests.post(
        f"{server_url}/create-conversation",
        json={"user_sub": user_sub},
        headers=headers
    ).json()
    return new_conversation['id']


def get_messages( conversation_id: str,token: str ,server_url: str = SERVER_URL) -> List[Dict]:
    """Get conversation messages, with authentication."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{server_url}/get-conversation-messages", params={"conversation_id": conversation_id},
                                headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return []
