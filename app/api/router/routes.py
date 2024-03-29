import os
from typing import List

from RagLLM.LangChainIntergrations.langchainlayer import LangChainService
from RagLLM.PGvector.models import DocumentResponse
from RagLLM.PGvector.store import AsnyPgVector
from RagLLM.PGvector.store_factory import get_vector_store
from RagLLM.Processing.langchain_processing import load_conversation_history
from RagLLM.Raptor.dyamic_raptor import TextClusterSummarizer
from RagLLM.database import agent_schemas as schemas
from RagLLM.database import db, crud, agent_schemas
from RagLLM.database.user_schemas import UserCreate
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi import Depends
from langchain.globals import set_debug
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models.anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings

from appfrwk.config import get_config
from appfrwk.logging_config import get_logger

set_debug(True)
config = get_config()
log = get_logger(__name__)

# Router information
router = APIRouter(
    prefix="/RAG",
    tags=["RAG"],
    responses={404: {"description": "Not found"}},
)

_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
history = []
template = """Answer the question based only on the following context:
   {context}

   Question: {question}
   """

try:

    OPENAI_API_KEY = config.OPENAI_API_KEY
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    mode = "async"
    pgvector_store = get_vector_store(
        connection_string=f"{config.DATABASE_URL2}",
        embeddings=embeddings,
        collection_name=f"{config.collection_name}",
        mode=mode,
    )
    db.connect()

except ValueError as e:
    raise HTTPException(status_code=500, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


def add_routes(app):
    app.include_router(router)





async def save_temp_file(upload_file: UploadFile, directory: str = "/tmp") -> str:
    try:
        file_path = os.path.join(directory, upload_file.filename)
        with open(file_path, "wb") as file_object:
            content = await upload_file.read()
            file_object.write(content)
        return file_path
    finally:
        await upload_file.close()


@router.post("/add-documents-upload")
async def add_documents_upload_raptor(pdf_file: UploadFile = File(...), max_iteration: int = 5):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    try:
        # Save the uploaded file temporarily
        temp_file_path = await save_temp_file(pdf_file)

        # Proceed with your processing using the file path
        # For example, let's say your summarizer needs a file path
        model = ChatAnthropic(temperature=0, anthropic_api_key=config.anthropic_api_key,
                              model_name="claude-3-opus-20240229")
        summarizer = TextClusterSummarizer(token_limit=16000, data_directory=temp_file_path,
                                           max_iterations=max_iteration)
        final_output = summarizer.run()

        # Add documents to pgvector_store as before
        ids = await pgvector_store.aadd_documents(final_output)

        # Cleanup: remove the temporary file after use
        os.remove(temp_file_path)

        return {"message": "Documents added successfully", "ids": ids}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-all-ids/")
async def get_all_ids():
    try:
        if isinstance(pgvector_store, AsnyPgVector):
            ids = await pgvector_store.get_all_ids()
        else:
            ids = pgvector_store.get_all_ids()

        return ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







@router.post("/get-documents-by-ids/", response_model=list[DocumentResponse])
async def get_documents_by_ids(ids: list[str]):
    try:
        if isinstance(pgvector_store, AsnyPgVector):
            existing_ids = await pgvector_store.get_all_ids()
            documents = await pgvector_store.get_documents_by_ids(ids)
        else:
            existing_ids = pgvector_store.get_all_ids()
            documents = pgvector_store.get_documents_by_ids(ids)

        if not all(id in existing_ids for id in ids):
            raise HTTPException(status_code=404, detail="One or more IDs not found")

        return documents
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-documents-internet")
async def add_documents_internet_raptor(pdf_filename: str, max_iteration: int):
    summarizer = TextClusterSummarizer(token_limit=16000, data_directory=pdf_filename, max_iterations=max_iteration)

    final_output = summarizer.run()

    ids = (
        await pgvector_store.aadd_documents(final_output)
    )

    return {"message": "Documents added successfully", "ids": ids}


@router.post("/create-conversation", response_model=schemas.Conversation)
async def create_conversation(conversation: schemas.ConversationCreate,
                              db_session=Depends(db.get_db)) -> schemas.Conversation:
    """ Create conversation """

    try:

        user_sub = conversation.user_sub
        user = await crud.get_user_by_sub(db_session, user_sub)
        if not user:
            log.info(f"Sub not found, creating user")
            user = await crud.create_user(db_session, UserCreate(sub=user_sub))
        log.info(f"User retrieved")
        log.info(f"Creating conversation")
        db_conversation = await crud.create_conversation(db_session, conversation)
        log.info(f"Conversation created")
        return db_conversation
    except Exception as e:
        log.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/rag_chain_chat/")
async def quick_response(message: schemas.UserMessage, db_session=Depends(db.get_db)):
    Service = LangChainService(model_name=config.SERVICE_MODEL, template=template)

    try:
        conversation = await crud.get_conversation(db_session, message.conversation_id)
        log.info(f"User Message: {message.message}")

    except Exception as e:
        log.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    try:
        chathistory = load_conversation_history(conversation, Service)
        log.info(f"current chat history {Service.get_message_history()}")

        result = Service.rag_chain.invoke(
            {
                "question": message.message,
                "chat_history": Service.get_message_history(),
            }
        )

        db_messages = agent_schemas.MessageCreate(
            user_message=message.message, agent_message=result, conversation_id=conversation.id)
        await crud.create_conversation_message(db_session, message=db_messages, conversation_id=conversation.id)
        return result
    except Exception as e:
        log.error(f"error code 500 {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent_rag_chain_chat/")
async def agent_response(message: schemas.UserMessage, db_session=Depends(db.get_db)):
    Service = LangChainService(model_name=config.SERVICE_MODEL, template=template)

    try:
        conversation = await crud.get_conversation(db_session, message.conversation_id)
        log.info(f"User Message: {message.message}")

    except Exception as e:
        log.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    try:
        chathistory = load_conversation_history(conversation, Service)
        log.info(f"current chat history {Service.get_message_history()}")

        result = Service.agent_executor.invoke(
            {
                "input": message.message,
                "chat_history": Service.get_message_history(),
            }
        )

        db_messages = agent_schemas.MessageCreate(
            user_message=message.message, agent_message=result["output"], conversation_id=conversation.id)
        await crud.create_conversation_message(db_session, message=db_messages, conversation_id=conversation.id)

        return result["output"]
    except Exception as e:
        log.error(f"error code 500 {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag_chain_with_source/")
async def rag_chain_with_source_response(message: str):
    Service = LangChainService(model_name=config.SERVICE_MODEL, template=template)

    try:

        result = Service.rag_chain_with_source.invoke(

            message

        )

        return result
    except Exception as e:
        log.error(f"error code 500 {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-conversations", response_model=List[schemas.Conversation])
async def get_user_conversations(user_sub: str, db_session=Depends(db.get_db)) -> List[schemas.Conversation]:
    """
    Get all conversations for an agent by id
    """
    try:
        log.info(f"Getting all conversations for user sub: {user_sub}")
        db_conversations = await crud.get_user_conversations(db_session, user_sub)
        return db_conversations
    except Exception as e:
        log.error(f"Error retrieving conversations for user_sub: {user_sub}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/get-conversation-messages", response_model=List[schemas.MessageCreate])
async def get_conversation_messages(conversation_id: str, db_session=Depends(db.get_db)) -> List[schemas.MessageCreate]:
    """
    Get all messages for a conversation by id
    """
    try:
        log.info(
            f"Getting all messages for conversation id: {conversation_id}")
        db_messages = await crud.get_conversation_messages(db_session, conversation_id)
        return db_messages
    except Exception as e:
        log.error(
            f"Error retrieving messages for conversation id: {conversation_id}")
        log.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
