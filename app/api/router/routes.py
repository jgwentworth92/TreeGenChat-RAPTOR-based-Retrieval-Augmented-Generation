import hashlib
import os
from typing import List

from langchain_community.document_loaders.pdf import PyPDFLoader
from redis import Redis
from RagLLM.Raptor.dyamic_raptor import recursive_embed_cluster_summarize
from autogen import Cache
from fastapi import HTTPException, APIRouter, Depends, WebSocket
from langchain.globals import set_debug
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from semantic_text_splitter import TextSplitter
from RagLLM.AutoGenIntergrations import AutoGenService
from langchain_community.document_loaders import PyMuPDFLoader
from RagLLM.LangChainIntergrations.langchainlayer import LangChainService
from RagLLM.PGvector.models import DocumentModel, DocumentResponse
from RagLLM.PGvector.store import AsnyPgVector
from RagLLM.PGvector.store_factory import get_vector_store
from RagLLM.Processing.langchain_processing import load_conversation_history
from RagLLM.database import agent_schemas as schemas
from RagLLM.database import db, crud, agent_schemas
from RagLLM.database.user_schemas import UserCreate
from langchain_text_splitters import RecursiveCharacterTextSplitter
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


@router.post("/add-documents/")
async def add_documents(documents: list[DocumentModel]):
    try:

        pdf_text = documents[0].page_content
        splitter = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", trim_chunks=False)
        MIN_TOKENS = 100
        MAX_TOKENS = 2000

        chunks_with_model = splitter.chunks(pdf_text, chunk_capacity=(MIN_TOKENS, MAX_TOKENS))
        for i, chunk in enumerate(chunks_with_model):
            log.info(f"CHUNK WITH MODEL {i + 1}: ")
        docs = [
            Document(
                page_content=doc,
                metadata=(

                    {"digest": hashlib.md5(doc.encode()).hexdigest()}
                ),
            )
            for doc in chunks_with_model
        ]
        ids = (
            await pgvector_store.aadd_documents(docs)
        )

        return {"message": "Documents added successfully", "id": ids}

    except Exception as e:
        log.error(f"Internal error 500: {e}")
        raise HTTPException(status_code=500)


@router.post("/add-documents-internal-pdf/")
async def add_documents(pdf_name: str):
    try:
        pdf_path = os.path.join(
            os.getcwd(), "appfrwk", "config", "pdf", pdf_name)
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(

            chunk_size=500,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        docs = text_splitter.split_documents(documents)

        ids = (
            await pgvector_store.aadd_documents(docs)
        )

        return {"message": "Documents added successfully", "id": ids}

    except Exception as e:
        log.error(f"Internal error 500: {e}")
        raise HTTPException(status_code=500)


@router.post("/add-documents-agentic_chunking/")
async def add_documents_agentic_chunking(pdf_url: str):
    try:
        Service = LangChainService(model_name="gpt-3.5-turbo", template=template)
        loader = PyPDFLoader(pdf_url)
        documents = loader.load_and_split()
        id_list = []
        for docs in documents:
            paragraphs = docs.page_content.split("\n\n")

            documents_agentic_chunks = Service.get_agentic_chunks(paragraphs)
            log.info(f"You have {len(documents)} propositions")
            log.info(documents_agentic_chunks)
            ids = (
                await pgvector_store.aadd_documents(documents_agentic_chunks)
            )
            id_list.append(ids)
        return id_list

    except Exception as e:
        log.error(f"Internal error 500: {e}")
        raise HTTPException(status_code=500)


@router.post("/add-documents-internet")
async def add_documents_internet(pdf_filename: str):
    loader = PyPDFLoader(pdf_filename)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.split_documents(documents)

    ids = (
        await pgvector_store.aadd_documents(docs)
    )

    return {"message": "Documents added successfully", "id": ids}


@router.post("/add-documents-internet-raptor")
async def add_documents_internet_raptor(pdf_filename: str):
    loader = PyPDFLoader(pdf_filename)
    documents = loader.load()
    docs_texts = [d.page_content for d in documents]
    """
    chunk_size_tok = 2000
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size_tok, chunk_overlap=0
    )
    d_sorted = sorted(documents, key=lambda x: x.metadata["source"])
    d_reversed = list(reversed(d_sorted))
    concatenated_content = "\n\n\n --- \n\n\n".join(
        [doc.page_content for doc in d_reversed]
    )
    texts_split = text_splitter.split_text(concatenated_content)
    """
    leaf_texts = docs_texts
    results = recursive_embed_cluster_summarize(leaf_texts, level=1, n_levels=3)
    all_texts = leaf_texts.copy()
    id_list = []
    # Iterate through the results to extract summaries from each level and add them to all_texts
    for level in sorted(results.keys()):
        # Extract summaries from the current level's DataFrame
        summaries = results[level][1]["summaries"].tolist()
        # Extend all_texts with the summaries from the current level
        all_texts.extend(summaries)

        ids = (
            await pgvector_store.aadd_documents(all_texts)
        )
        id_list.append(ids)

    return {"message": "Documents added successfully", "ids": id_list}


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


@router.post("/autogen_rag_chain_chat/")
async def autogen_rag_response(message: schemas.UserMessage):
    config_list = [
        {
            "model": "gpt-4",
            "api_key": config.OPENAI_API_KEY,
        }
    ]

    Service = AutoGenService(config_list)
    try:

        with Cache.redis(redis_url="redis://192.168.1.186:6379/0") as cache:
            Service.user_proxy.initiate_chat(Service.assistant, message=message.message, cache=cache)

            # Accessing the chat messages from both the user_proxy and the assistant
        user_proxy_messages = Service.user_proxy.chat_messages
        assistant_messages = Service.assistant.chat_messages

        # Extracting the messages as lists
        user_proxy_messages_list = [msg['content'] for msg in user_proxy_messages[Service.assistant]]
        assistant_messages_list = [msg['content'] for msg in assistant_messages[Service.user_proxy]]

        # Returning both lists of messages
        return {"user_proxy_messages": user_proxy_messages_list, "assistant_messages": assistant_messages_list}

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


redis = Redis(host='redisDB', port=6379, db=0)


@router.on_event("startup")
def startup_event():
    redis.ping()  # Check if Redis is up and running
