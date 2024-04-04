import logging.config
import os
import base64
from typing import List
from app import models
from app.config import get_config
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
import validators  # Make sure to install this package
from urllib.parse import urlparse, urlunparse
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import format_document


from app.schema import Link
config = get_config()
# Load environment variables from .env file for security and configuration.

def setup_logging():
    """
    Sets up logging for the application using a configuration file.
    This ensures standardized logging across the entire application.
    """
    # Construct the path to 'logging.conf', assuming it's in the project's root.
    logging_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logging.conf')
    # Normalize the path to handle any '..' correctly.
    normalized_path = os.path.normpath(logging_config_path)
    # Apply the logging configuration.
    logging.config.fileConfig(normalized_path, disable_existing_loggers=False)

def authenticate_user(username: str, password: str):
    """
    Placeholder for user authentication logic.
    In a real application, replace this with actual authentication against a user database.
    """
    # Simple check against constants for demonstration.
    if username == config.ADMIN_USER and password == config.ADMIN_PASSWORD:
        return {"username": username}
    # Log a warning if authentication fails.
    logging.warning(f"Authentication failed for user: {username}")
    return None

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def validate_and_sanitize_url(url_str):
    """
    Validates a given URL string and returns a sanitized version if valid.
    Returns None if the URL is invalid, ensuring only safe URLs are processed.
    """
    if validators.url(url_str):
        parsed_url = urlparse(url_str)
        sanitized_url = urlunparse(parsed_url)
        return sanitized_url
    else:
        logging.error(f"Invalid URL provided: {url_str}")
        return None

# Assuming this function already exists and returns a user object if credentials are valid
def verify_refresh_token(refresh_token: str):
    # Placeholder for refresh token verification logic
    # You should validate the refresh token's signature and its expiration
    # Also check if the token has been revoked or is still valid
    try:
        payload = jwt.decode(refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        # Implement additional checks here, such as token revocation or session validity
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
def encode_url_to_filename(url):
    """
    Encodes a URL into a base64 string safe for filenames, after validating and sanitizing.
    Removes padding to ensure filename compatibility.
    """
    sanitized_url = validate_and_sanitize_url(str(url))
    if sanitized_url is None:
        raise ValueError("Provided URL is invalid and cannot be encoded.")
    encoded_bytes = base64.urlsafe_b64encode(sanitized_url.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8').rstrip('=')
    return encoded_str

def decode_filename_to_url(encoded_str: str) -> str:
    """
    Decodes a base64 encoded string back into a URL, adding padding if necessary.
    This reverses the process done by `encode_url_to_filename`.
    """
    padding_needed = 4 - (len(encoded_str) % 4)
    if padding_needed:
        encoded_str += "=" * padding_needed
    decoded_bytes = base64.urlsafe_b64decode(encoded_str)
    return decoded_bytes.decode('utf-8')

def generate_links(action: str, qr_filename: str, base_api_url: str, download_url: str) -> List[Link]:
    links = []
    if action in ["list", "create"]:
        links.append(Link(rel="view", href=download_url, action="GET", type="image/png"))
    if action in ["list", "create", "delete"]:
        delete_url = f"{base_api_url}/qr-codes/{qr_filename}"
        links.append(Link(rel="delete", href=delete_url, action="DELETE", type="application/json"))
    return links

def generate_event_links(event_id: int) -> List[Link]:
    return [
        Link(rel="self", href=f"{config.SERVER_BASE_URL}/events/{event_id}", action="GET", type="application/json"),
        Link(rel="edit", href=f"{config.SERVER_BASE_URL}/events/{event_id}", action="PUT", type="application/json"),
        Link(rel="delete", href=f"{config.SERVER_BASE_URL}/events/{event_id}", action="DELETE", type="application/json")
    ]

def generate_pagination_links(page: int, per_page: int, total_pages: int, base_url: str = "/events/") -> List[Link]:
    links = []
    links.append(Link(rel="first", href=f"{config.SERVER_BASE_URL}{base_url}?page=1&per_page={per_page}", action="GET", type="application/json"))
    links.append(Link(rel="last", href=f"{config.SERVER_BASE_URL}{base_url}?page={total_pages}&per_page={per_page}", action="GET", type="application/json"))
    
    if page > 1:
        links.append(Link(rel="prev", href=f"{config.SERVER_BASE_URL}{base_url}?page={page - 1}&per_page={per_page}", action="GET", type="application/json"))
    if page < total_pages:
        links.append(Link(rel="next", href=f"{config.SERVER_BASE_URL}{base_url}?page={page + 1}&per_page={per_page}", action="GET", type="application/json"))
    
    return links
def format_documents(docs):
    """Formats a list of documents for processing."""
    return "\n\n".join(doc.page_content for doc in docs)


def combine_documents(
        docs, document_separator="\n\n"
):
    document_prompt = PromptTemplate.from_template(template="{page_content}")
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)



def sort_message_history(conversation: models.Conversation) -> List[models.Message]:
    """
    Sorts the message history for the conversation by created_at timestamp in ascending order.

    Args:
        conversation (schemas.Conversation): The conversation to sort the message history for.
    """
    message_history = conversation.messages
    message_history.sort(key=lambda x: x.created_at, reverse=False)
    return message_history


def load_conversation_history(conversation: models.Conversation, service):
    """
    Loads the conversation history into the LangChainService, ensuring that chat_history
    is always a list.

    Args:
        conversation: The conversation model from the database.
        service: The LangChainService instance.
    """
    try:

        if conversation and conversation.messages:
            logging.info("conversation has messages")
            # Load existing conversation messages
            for msg in sort_message_history(conversation):
                service.add_user_message(msg.user_message)
                service.add_ai_message(msg.agent_message)
        else:
            logging.info("new conversation")
            service.add_ai_message("hi how may i help you")

        # Now chat_history is guaranteed to be a list, though it could be empty
        # Here, instead of directly adding messages to the service, you would
        # appropriately pass `chat_history` where required, ensuring it's never None

    except Exception as e:
        logging.error(f"Error loading conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")