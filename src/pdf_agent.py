import uuid
import os

from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_community.chat_models import ChatOpenAI
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.chat_message_histories import ChatMessageHistory

from src.db.chroma_db import save_to_chroma




pdf_agent_prompt_template = """ 
Your task is to {task_description}. Please respond strictly based on the provided context. 
If the question does not relate to the context, respond with: "I cannot answer this question as it is not related to 
your task." For questions that are relevant, provide concise answers using only the information present in the context.
If the information is present in the context, include all the relevant details in your response. 

You also have access to the chat history. Your responses should be user-friendly, taking into account both the 
context and the chat history. Ensure your answers are direct and free of irrelevant information.
Important: You must to respond in Markdown format.

{context}

Example:
Human message: ¿Qué tipo de negocios pueden aplicar para el Crédito para Moto de Trabajo?
AI response: 
¡Hola! Este crédito está diseñado especialmente para microempresarios y trabajadores independientes. Si tienes un 
negocio como una tienda, ventas por catálogo, peluquería, servicio de manicura, agricultura o cualquier otro que 
necesite mejorar su movilidad para optimizar tus actividades comerciales, ¡este crédito es para ti! ¿Te gustaría saber 
más sobre cómo funciona?
---

Based on the above context, answer the following question: {question}
"""


os.environ["OPENAI_API_KEY"] = "env"


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            pdf_agent_prompt_template
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "Based on the above context, answer the following question: {question}"),
    ]
)

class PDFAgent:
    def __init__(self, local_agent: bool,):
        self.vector_db = None
        self.embedding_model = None
        self.llm_model = None
        self.runnable_with_history = None
        self.task_description = None
        self.local_agent = local_agent
        self.sessions_history = {}

        if local_agent:
            self.set_up_models()

    def set_up_models(self):

        embedding_model = OllamaEmbeddings(
            model="nomic-embed-text:latest"
        )
        self.embedding_model = embedding_model

        if self.local_agent:
            self.llm_model = OllamaLLM(
                model="llama3.2:latest"
            )
        else:
            self.llm_model = ChatOpenAI(
                model="gpt-3.5-turbo:latest"

            )

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
        """
        if self.local_agent:
            # Create a local embedding model and set up the vector database
            embedding_model = OllamaEmbeddings(
                model="nomic-embed-text:latest"
            )

            self.embedding_model = embedding_model

            self.vector_db = save_to_chroma(chunks, embedding_model)

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
        """



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

        print(docs)

        context = "\n\n---\n\n".join([doc.page_content for doc, _score in docs])

        response = self.runnable_with_history.invoke(
            {
                "context": context,
                "question": question,
                "task_description": self.task_description,
            },
            config={"configurable": {"session_id": session_id}},
        )

        history.add_ai_message(response)

        resources = [f"{doc.metadata.get('source')} (Page {doc.metadata.get('page')})" for doc, _score in docs]

        formatted_response = f"Response: {response}\nSources:{resources}"

        return formatted_response

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