from pydantic import BaseModel, HttpUrl, Field, conint
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
class QRCodeRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to encode into the QR code.")
    fill_color: str = Field(default="red", description="Color of the QR code.", example="black")
    back_color: str = Field(default="white", description="Background color of the QR code.", example="yellow")
    size: conint(ge=1, le=40) = Field(default=10, description="Size of the QR code from 1 to 40.", example=20) # type: ignore

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "fill_color": "black",
                "back_color": "yellow",
                "size": 20
            }
        }

class Link(BaseModel):
    rel: str = Field(..., description="Relation type of the link.")
    href: HttpUrl = Field(..., description="The URL of the link.")
    action: str = Field(..., description="HTTP method for the action this link represents.")
    type: str = Field(default="application/json", description="Content type of the response for this link.")

    class Config:
        json_schema_extra = {
            "example": {
                "rel": "self",
                "href": "https://api.example.com/qr/123",
                "action": "GET",
                "type": "application/json"
            }
        }

class QRCodeResponse(BaseModel):
    message: str = Field(..., description="A message related to the QR code request.")
    qr_code_url: HttpUrl = Field(..., description="The URL to the generated QR code.")
    links: List[Link] = Field(default=[], description="HATEOAS links related to the QR code.")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "QR code created successfully.",
                "qr_code_url": "https://api.example.com/qr/123",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://api.example.com/qr/123",
                        "action": "GET",
                        "type": "application/json"
                    }
                ]
            }
        }

class Token(BaseModel):
    access_token: str = Field(..., description="The access token for authentication.")
    token_type: str = Field(default="bearer", description="The type of the token.")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "jhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="The username that the token represents.")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user@example.com"
            }
        }

class EventBase(BaseModel):
    title: str = Field(..., description="Title of the event.")
    description: str = Field(..., description="Description of the event.")

class EventCreate(EventBase):
    start_date: datetime = Field(..., description="Start date and time of the event.")
    end_date: datetime = Field(..., description="End date and time of the event.")

class Event(EventBase):
    id: int = Field(..., description="Unique identifier of the event.")
    start_date: datetime
    end_date: datetime
    links: List[Link] = Field(default=[], description="HATEOAS links related to this event.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Sample Event",
                "description": "This is a sample event.",
                "start_date": "2024-01-01T09:00:00",
                "end_date": "2024-01-01T17:00:00",
                "links": [
                    {
                        "rel": "self",
                        "href": "https://api.example.com/events/1",
                        "action": "GET",
                        "type": "application/json"
                    },
                    {
                        "rel": "update",
                        "href": "https://api.example.com/events/1",
                        "action": "PUT",
                        "type": "application/json"
                    },
                    {
                        "rel": "delete",
                        "href": "https://api.example.com/events/1",
                        "action": "DELETE",
                        "type": "application/json"
                    }
                ]
            }
        }

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title of the event.")
    description: Optional[str] = Field(None, description="Updated description of the event.")
    start_date: Optional[datetime] = Field(None, description="Updated start date and time of the event.")
    end_date: Optional[datetime] = Field(None, description="Updated end date and time of the event.")

    class Config:
        from_attributes = True

class Pagination(BaseModel):
    page: int = Field(..., description="Current page number.")
    per_page: int = Field(..., description="Number of items per page.")
    total_items: int = Field(..., description="Total number of items.")
    total_pages: int = Field(..., description="Total number of pages.")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 10,
                "total_items": 50,
                "total_pages": 5
            }
        }

class EventList(BaseModel):
    items: List[Event]  # Your EventResponse model
    pagination: Pagination  # Your Pagination model
    links: List[Link] = Field(..., alias='_links')  # Use alias for the external representation



    class Config:
        from_attributes = True
        populate_by_name = True

        json_schema_extra = {
            "example": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Sample Event",
                        "description": "This is a sample event.",
                        "start_date": "2024-01-01T09:00:00",
                        "end_date": "2024-01-01T17:00:00",
                        "links": [
                            {
                                "rel": "self",
                                "href": "https://api.example.com/events/1",
                                "action": "GET",
                                "type": "application/json"
                            }
                        ]
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total_items": 50,
                    "total_pages": 5
                },
                "links": [
                    {
                        "rel": "self",
                        "href": "https://api.example.com/events?page=1&per_page=10",
                        "action": "GET",
                        "type": "application/json"
                    },
                    {
                        "rel": "next",
                        "href": "https://api.example.com/events?page=2&per_page=10",
                        "action": "GET",
                        "type": "application/json"
                    },
                    {
                        "rel": "last",
                        "href": "https://api.example.com/events?page=5&per_page=10",
                        "action": "GET",
                        "type": "application/json"
                    }
                ]
            }
        }
    }
        
class RefreshTokenRequest(BaseModel):
    refresh_token: str

class MessageBase(BaseModel):
    """
    Message base schema
    """
    user_message: str
    agent_message: str
    
class UserBase(BaseModel):
    """
    Users base schema
    """
    sub: str

class UserCreate(UserBase):
    """
    Users creation schema
    """
    pass



class MessageCreate(MessageBase):
    """
    Message creation schema
    """
    pass


class Message(MessageBase):
    """
    Message schema
    """
    id: str
    conversation_id: str
    created_at: datetime = datetime.now

    class Config:
        from_attributes = True

# API Schemas


class UserMessage(BaseModel):
    """
    User message schema
    """
    conversation_id: str
    message: str


class ChatAgentResponse(BaseModel):
    """
    Chat agent response schema
    """
    conversation_id: str
    response: str
class ConversationBase(BaseModel):
    """
    Conversation base schema

    Attributes:
    - `user_sub (str)`: User sub
    """

    user_sub: str


class ConversationCreate(ConversationBase):
    """
    Conversation Creation schema
    """
    pass


class Conversation(ConversationBase):
    """
    Conversation schema
    """
    id: str
    created_at: datetime = datetime.now

    class Config:
        from_attributes = True
class DocumentResponse(BaseModel):
    page_content: str
    metadata: dict


class DocumentModel(BaseModel):
    page_content: str
    metadata: Optional[dict] = {}

    def generate_digest(self):
        hash_obj = hashlib.md5(self.page_content.encode())
        return hash_obj.hexdigest()
class DocumentInput(BaseModel):
    pdf_filename: str
    max_iteration: int

class QuickMessage(BaseModel):
    question: str
