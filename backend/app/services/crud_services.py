"""
This module contains the CRUD (Create, Read, Update, Delete) operations for the database.
"""

from app.schema import ConversationCreate, MessageCreate, UserMessage,UserCreate,UserBase
from app.models import Agent, Conversation, Message, User
from sqlalchemy import sql
from sqlalchemy.orm import joinedload

from uuid import uuid4

# =========================
# CRUD operations for User
# =========================

async def create_user(db, user: UserCreate)-> "User":
    """
    Create a user in the database
    """
    query = (
        sql.insert(User)
        .values(
            id=str(uuid4()),
            sub=user.sub
        )
        .returning(*User.__table__.c)
    )
    user = await db.execute(query)
    await db.commit()
    return user.first()

async def get_user(db, id: str)-> "User":
    """
    Gets user from the database by its id
    """
    query = sql.select(User).where(User.id == id).options(
        joinedload(User.conversations))
    result = await db.execute(query)
    user = result.scalars().first()
    return user

async def get_user_by_sub(db, sub: str)-> "User":
    """
    Gets user from the database by its sub
    """
    query = sql.select(User).where(User.sub == sub).options(
        joinedload(User.conversations))
    result = await db.execute(query)
    user = result.scalars().first()
    return user

async def get_users(db)-> list["User"]:
    """
    Gets all users from the database
    """
    query = sql.select(User).options(joinedload(User.conversations))
    result = await db.execute(query)
    users = result.scalars().unique().all()
    return users

async def update_user(db, id: str, **kwargs)-> "User":
    """
    Updates a user in the database
    """
    query = (
        sql.update(User)
        .where(User.id == id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
        .returning(*User.__table__.c)
    )
    user = await db.execute(query)
    await db.commit()
    return user.first()

async def delete_user(db, id: str)-> bool:
    """
    Deletes a user from the database
    """
    query = sql.delete(User).where(User.id == id)
    await db.execute(query)
    await db.commit()
    return True



# =========================
# CRUD operations for Conversation
# =========================


async def create_conversation(db, conversation: ConversationCreate)-> "Conversation":
    """
    Create a conversation in the database
    """
    query = (
        sql.insert(Conversation)
        .values(
            id=str(uuid4()),
            user_sub=conversation.user_sub
        )
        .returning(*Conversation.__table__.c)
    )
    conversation = await db.execute(query)
    await db.commit()
    return conversation.first()


async def get_conversation(db, id: str)-> "Conversation":
    """
    Gets conversation from the database by its id
    """
    query = sql.select(Conversation).where(
        Conversation.id == id).options(joinedload(Conversation.user),  joinedload(Conversation.messages))
    result = await db.execute(query)
    conversation = result.scalars().first()
    return conversation

async def get_user_conversations(db, user_sub: str)-> list["Conversation"]:
    """
    Gets all conversations from a user
    """
    query = (
        sql.select(Conversation)
        .join(Message, Conversation.id == Message.conversation_id)
        .where(Conversation.user_sub == user_sub)
        .group_by(Conversation.id)
        .having(sql.func.count(Message.id) > 0)
    )
    result = await db.execute(query)
    conversations = result.scalars().unique().all()
    return conversations




async def update_conversation(db, id: str, **kwargs)-> "Conversation":
    """
    Updates a conversation in the database
    """
    query = (
        sql.update(Conversation)
        .where(Conversation.id == id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
        .returning(*Conversation.__table__.c)
    )
    conversation = await db.execute(query)
    await db.commit()
    return conversation.first()


async def delete_conversation(db, id: str)-> bool:
    """
    Deletes a conversation from the database
    """
    query = sql.delete(Conversation).where(Conversation.id == id)
    await db.execute(query)
    await db.commit()
    return True

# =========================
# CRUD operations for Message
# =========================


async def create_conversation_message(db, message: MessageCreate, conversation_id: str)-> "Message":
    """
    Create a message in the database
    """
    query = (
        sql.insert(Message)
        .values(
            id=str(uuid4()),
            conversation_id=conversation_id,
            user_message=message.user_message,
            agent_message=message.agent_message
        )
        .returning(*Message.__table__.c)
    )
    message = await db.execute(query)
    await db.commit()
    return message.first()


async def get_message(db, id: str)-> "Message":
    query = sql.select(Message).where(Message.id == id)
    result = await db.execute(query)
    message = result.scalars().first()
    return message


async def get_messages(db)-> list["Message"]:
    """
    Gets all messages from the database
    """
    query = sql.select(Message)
    result = await db.execute(query)
    messages = result.scalars().unique().all()
    return messages


async def get_conversation_messages(db, conversation_id: str)-> list["Message"]:
    """
    Gets all messages from a conversation
    """
    query = sql.select(Message).where(
        Message.conversation_id == conversation_id)
    result = await db.execute(query)
    messages = result.scalars().unique().all()
    return messages


async def update_message(db, id: str, **kwargs)-> "Message":
    """
    Updates a message in the database
    """
    query = (
        sql.update(Message)
        .where(Message.id == id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
        .returning(*Message.__table__.c)
    )
    message = await db.execute(query)
    await db.commit()
    return message.first()


async def delete_message(db, id: str)-> bool:
    """
    Deletes a message from the database
    """
    query = sql.delete(Message).where(Message.id == id)
    await db.execute(query)
    await db.commit()
    return True
