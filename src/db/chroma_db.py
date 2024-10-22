import os
import shutil

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


CHROMA_PATH = "chroma"
def save_to_chroma(chunks: list[Document],embedding_model):
    """
    Save chunks to the chroma database
    Args:
        chunks (list[Document]): list of chunks
        embedding_model: embedding model
    """
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(
        chunks,
        persist_directory=CHROMA_PATH,
        embedding=embedding_model
    )
    # Persist the database
    print(f"Saved chunks to {CHROMA_PATH}")

    return db

def load_from_chroma():
    """
    Load the chroma database
    Returns:
        Chroma: chroma database
    """

    embedding_model = OllamaEmbeddings(
        model="nomic-embed-text:latest"
    )
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_model
    )
    return db


