import uuid
import os

from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.chat_message_histories import ChatMessageHistory

from src.constants.constants import PDF_AGENT_PROMPT_TEMPLATE, QUERY_REFINEMENT_PROMPT_TEMPLATE
from src.db.chroma_db import save_to_chroma

load_dotenv()

if os.getenv("OPENAI_API_KEY") is not None:
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            PDF_AGENT_PROMPT_TEMPLATE
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "Based on the above context, answer the following question: {question}"),
    ]
)

query_refinement_prompt = ChatPromptTemplate.from_template(QUERY_REFINEMENT_PROMPT_TEMPLATE)

#Models
LLM_MODEL_NAME = os.getenv("OLLAMA_LLM_MODEL")
EMBEDDING_MODEL_NAME = os.getenv("OLLAMA_EMBED_MODEL")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBED_MODEL")

class PDFAgent:
    def __init__(self, local_agent: bool, use_refinement: bool = False):
        self.vector_db = None
        self.embedding_model = None
        self.llm_model = None
        self.refinement_llm_model = None
        self.runnable_with_history = None
        self.task_description = None
        self.local_agent = local_agent
        self.use_refinement = use_refinement
        self.sessions_history = {}

        self.set_up_models()

        if use_refinement:
            self.set_up_refinement_model()




    def set_up_refinement_model(self):
        if self.local_agent:
            self.refinement_llm_model = OllamaLLM(
                model=LLM_MODEL_NAME
            )
        else:
            self.refinement_llm_model = ChatOpenAI(
                model=LLM_MODEL_NAME
            )

    def set_up_models(self):



        if self.local_agent:
            self.llm_model = OllamaLLM(
                model=LLM_MODEL_NAME
            )
            embedding_model = OllamaEmbeddings(
                model=EMBEDDING_MODEL_NAME
            )
            self.embedding_model = embedding_model

        else:
            self.llm_model = ChatOpenAI(
                model="gpt-3.5-turbo-0125",
                temperature=0
            )
            embedding_model = OpenAIEmbeddings(
                model=OPENAI_EMBEDDING_MODEL
            )
            self.embedding_model = embedding_model

        runnable = prompt | self.llm_model


        self.runnable_with_history = RunnableWithMessageHistory(
            runnable,
            self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )




    def set_up_vector_db(self, chunks: list[Document]):
        """
        Set up the vector database
        Args:
            chunks (list[Document]): list of chunks
        """

        self.vector_db = save_to_chroma(chunks, self.embedding_model)

        if self.local_agent:
            # Create a local embedding model and set up the vector database
            embedding_model = OllamaEmbeddings(
                model="nomic-embed-text:latest"
            )

            self.embedding_model = embedding_model


            # Set up the LLM model

            self.llm_model = OllamaLLM(
                model="llama3.2:latest"
            )

            runnable = prompt | self.llm_model

            self.runnable_with_history = RunnableWithMessageHistory(
                runnable,
                self.get_session_history,
                input_messages_key="question",
                history_messages_key="history",
            )




    def query(self, question: str, session_id: str):


        """
        Query the agent
        Args:
            question (str): question
            session_id (str): session
        Returns:
            list[Document]: list of documents
        """
        history: ChatMessageHistory = self.get_session_history(session_id)

        history.add_user_message(question)

        docs = self.vector_db.similarity_search_with_score(question)

        context = "\n\n---\n\n".join([doc.page_content for doc, _score in docs])

        if self.local_agent:
            response = self.runnable_with_history.invoke(
                {
                    "context": context,
                    "question": question,
                    "task_description": self.task_description,
                },
                config={"configurable": {"session_id": session_id}},
            )
        else:
            response = self.runnable_with_history.invoke(
                {
                    "context": context,
                    "question": question,
                    "task_description": self.task_description,
                },
                config={"configurable": {"session_id": session_id}}
            )

            response = response.content

        history.add_ai_message(response)

        resources = [f"{doc.metadata.get('source')} (Page {doc.metadata.get('page')})" for doc, _score in docs]

        formatted_response = f"Response: {response}\nSources:{resources}"

        return response, resources

    def configure_session(self):
        # Generate a session ID with UUID
        session_id = str(uuid.uuid4())

        if session_id not in self.sessions_history:
            self.sessions_history[session_id] = ChatMessageHistory()

        return session_id

    def get_session_history(self, session_id)->ChatMessageHistory:
        return self.sessions_history[session_id]

    def verify_session_history_exists(self, session_id):
        return session_id in self.sessions_history