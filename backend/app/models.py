# models.py


from app.services import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, DateTime, JSON,Text
from sqlalchemy.orm import relationship

class Event(Base):
    __tablename__ = "events"
    # Use UUID as the primary key type for better scalability and uniqueness across distributed systems
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # Limit title length to 255 characters, which is a common practice for short text fields
    title = Column(String(255), nullable=False, index=True)
    # Use Text for potentially long descriptions, PostgreSQL has efficient handling for large text fields
    description = Column(Text, nullable=True)
    # Ensure start_date and end_date are not nullable to enforce data integrity
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

class User(Base):
    """
    ### Represents a user in the system

    Attributes:
    - `id (str)`: The unique identifier of the user (from Auth0)
    - `username (str)`: The username or email of the user
    - `conversations (relationship)`: Relationship between user and conversation
    - `created_at (datetime)`: The date and time the user was created
    - `modified_at (datetime)`: The date and time the user was last modified
    """
    __tablename__ = "users"

    id = Column(String, nullable=False, index=True)
    sub = Column(String, primary_key=True, unique=True)
    # Relationship between user and conversation
    conversations = relationship("Conversation", back_populates="user")
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"sub={self.sub}, "
            f")>"
        )


class Agent(Base):
    """
    ### Represents an agent in the system

    Attributes:
    - `id (str)`: The unique identifier of the agent
    - `context (str)`: The context for the agent
    - `first_message (str)`: The first message the AI agent will send
    - `response_shape (JSON)`: The expected shape for each agent's interaction with a user (for programmatic communication)
    - `instructions (str)`: Instructions for the AI agent
    - `created_at (datetime)`: The date and time the agent was created
    - `modified_at (datetime)`: The date and time the agent was last modified
    """
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    context = Column(String, nullable=False)
    first_message = Column(String, nullable=False)
    response_shape = Column(String,   nullable=False)
    instructions = Column(String, nullable=False)
    # relationship between agent and conversation
    created_at = Column(DateTime,  default=datetime.now)
    modified_at = Column(DateTime,  default=datetime.now)

    def __repr__(self):
        """
        Returns a string representation of the agent
        """
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"context={self.context}, "
            f"first_message={self.first_message}, "
            f"response_shape={self.response_shape}, "
            f"instructions={self.instructions}, "
            f")>"
        )

class Conversation(Base):
    """
    ### Represents a conversation in the system

    Attributes:
    - `id (str)`: The unique identifier of the conversation
    - `messages (relationship)`: Relationship between conversation and messages
    - `created_at (datetime)`: The date and time the conversation was created
    - `modified_at (datetime)`: The date and time the conversation was last modified
    """
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    # relation between conversation and message
    user_sub = Column(String, ForeignKey("users.sub"))
    # Relationship between conversation and user
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    created_at = Column(DateTime,  default=datetime.now)
    modified_at = Column(DateTime,  default=datetime.now)

    def __repr__(self):
        """
        Returns a string representation of the conversation
        """
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"user_sub={self.user_sub}, "
            f")>"
        )

class Message(Base):
    """
    ### Represents a message in the system

    Attributes:
    - `id (str)`: The unique identifier of the message
    - `conversation_id (str)`: The ID of the conversation associated with the message
    - `conversation (relationship)`: Relationship between message and conversation
    - `user_message (str)`: The message from the user
    - `agent_message (str)`: The message from the agent
    - `created_at (datetime)`: The date and time the message was created
    - `modified_at (datetime)`: The date and time the message was last modified
    """

    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    # A message belongs to a conversation
    conversation_id = Column(String, ForeignKey("conversations.id"))
    # relationship between message and conversation
    conversation = relationship("Conversation", back_populates="messages")
    user_message = Column(String, nullable=False)
    agent_message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        """
        Returns a string representation of the message
        """
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"conversation_id={self.conversation_id}, "
            f"user_message={self.user_message}, "
            f"agent_message={self.agent_message}, "
            f")>"
        )