import logging
from operator import itemgetter

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import get_buffer_string
from langchain_core.prompts import MessagesPlaceholder

from app.config import get_config
from app.factories.pgvector_store_factory import get_vector_store
from app.utils.common import combine_documents, format_documents

config = get_config()


class LangChainService:
    def __init__(self, template: str, model_name=None, verbose=True, streaming=True,
                 retriever_options=None, contextualize_q_system_prompt=None, qa_system_prompt=None,
                 chat_history_template=None, llm=None, custom_vector_db=None):

        self.model_name = model_name or config.SERVICE_MODEL
        self.verbose = verbose
        self.streaming = streaming
        self.template = template
        self.openai_api_key = config.OPENAI_API_KEY

        # Validate critical configurations
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing in the configuration")

        self._initialize_prompts(contextualize_q_system_prompt, qa_system_prompt, chat_history_template)
        if not retriever_options:
            self.retriever_options = {"search_kwargs": {"k": 10}}
        else:
            self.retriever_options = retriever_options
        # Initialize components
        self.custom_vector_db = custom_vector_db

        # Initialize OpenAI client if llm is not provided
        self.llm = self._initialize_openai_client() if llm is None else llm

        self._initialize_memory_and_parser()
        self._initialize_retriever_and_templates()
        self._initialize_chains()

    def _initialize_openai_client(self):
        return ChatOpenAI(
            model_name=self.model_name,
            temperature=config.SERVICE_TEMPERATURE,
            max_tokens=config.SERVICE_MAX_TOKENS,
            streaming=self.streaming,
            verbose=self.verbose,
            openai_api_key=self.openai_api_key,
            model_kwargs={"frequency_penalty": config.SERVICE_FREQUENCY_PENALTY,
                          "presence_penalty": config.SERVICE_PRESENCE_PENALTY}
        )

    def _initialize_prompts(self, contextualize_q_system_prompt, qa_system_prompt, chat_history_template):
        self.contextualize_q_system_prompt = contextualize_q_system_prompt or \
                                             """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just reformulate it if needed and otherwise return it as is."""

        self.qa_system_prompt = qa_system_prompt or \
                                """You are an assistant for question-answering tasks. \
            Use the following pieces of retrieved context to answer the question. \
            If you don't know the answer, just say that you don't know. \
            Use three sentences maximum and keep the answer concise.\
            {context}"""

        self.chat_history_template = chat_history_template or \
                                     """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language. \
            Chat History: \
            {chat_history} \
            Follow Up Input: {question} \
            Standalone question:"""

    def _initialize_rag_chain_with_source(self):
        """Create the RAG chain with source."""

        prompt = hub.pull("rlm/rag-prompt")
        rag_chain_from_docs = (
                RunnablePassthrough.assign(context=(lambda x: format_documents(x["context"])))
                | prompt
                | self.llm
                | StrOutputParser()
        )

        self.rag_chain_with_source = RunnableParallel(
            {"context": self.retriever, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)

    def _initialize_chains(self):
        """Simplify method calls for initializing various chains."""
        self._initialize_conversational_qa_chain()
        self._initialize_contextualize_q_chain()
        self._initialize_rag_chain()
        self._initialize_rag_chain_with_source()
        self._initialize_conversational_react_agent()

    def _initialize_memory_and_parser(self):
        """Initialize memory management and output parser."""
        self.history = ChatMessageHistory()
        self.memory = ConversationBufferMemory(chat_memory=self.history, return_messages=config.DEBUG)
        self.str_output_parser = StrOutputParser()

    def _initialize_retriever_and_templates(self):
        """Initialize the retriever and templates for conversational retrieval."""
        if self.custom_vector_db is not None:
            # Use the provided custom vector database as the retriever
            self.retriever = self.custom_vector_db.as_retriever(**self.retriever_options)
        else:
            # Default to pgvector store if no custom vector database is provided
            embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            self.pgvector_store = get_vector_store(
                connection_string=config.DATABASE_URL2,
                embeddings=embeddings,
                collection_name=config.collection_name,
                mode="async",
            )
            self.retriever = self.pgvector_store.as_retriever(**self.retriever_options)

        self._initialize_templates()

    def _initialize_templates(self):
        """Centralized template initialization."""

        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        self.CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(self.chat_history_template)
        self.ANSWER_PROMPT = ChatPromptTemplate.from_template(self.template)
        self.DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

    # Additional methods for chain initializations...
    def _initialize_conversational_qa_chain(self):
        """Create the conversational QA chain with the retriever."""

        _inputs = RunnableParallel(
            standalone_question=RunnablePassthrough.assign(
                chat_history=lambda x: get_buffer_string(x["chat_history"])
            )
                                | self.CONDENSE_QUESTION_PROMPT
                                | self.llm
                                | StrOutputParser(),
        )
        _context = {
            "context": itemgetter("standalone_question") | self.retriever | combine_documents,
            "question": lambda x: x["standalone_question"],
        }
        self.conversational_qa_chain = _inputs | _context | self.ANSWER_PROMPT | self.llm | StrOutputParser()

    def _initialize_contextualize_q_chain(self):

        self.contextualize_q_chain = self.contextualize_q_prompt | self.llm | StrOutputParser()

    def _initialize_rag_chain(self):
        def contextualized_question(input: dict):
            if input.get("chat_history"):
                logging.info("chat history is present")
                return self.contextualize_q_chain
            else:
                logging.info("chat history is not present")
                return input["question"]

        self.rag_chain = (
                RunnablePassthrough.assign(
                    context=contextualized_question | self.retriever | combine_documents
                )
                | self.qa_prompt
                | self.llm | StrOutputParser()
        )

    def get_message_history(self):
        """Return the message history."""
        return self.history.messages

    def add_user_message(self, message):
        """Add a user message to the history."""
        self.history.add_user_message(message)

    def add_ai_message(self, message):
        """Add an AI-generated message to the history."""
        self.history.add_ai_message(message)

    def _initialize_conversational_react_agent(self):

        tool = create_retriever_tool(
            self.retriever,
            "search_academic_resources",
            "Enables the searching of a specialized vector database filled with academic materials, including research papers and books. This tool is designed for deep dives into scholarly content, offering users direct access to a wealth of knowledge across various disciplines. Whether you're looking for the latest findings in a specific field or historical texts that lay the foundation for current theories, this tool streamlines the process, ensuring you can find the information you need without prior knowledge of the database's contents."
        )
        prompt = hub.pull("hwchase17/react-chat")
        tools = [tool]
        agent = create_react_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
