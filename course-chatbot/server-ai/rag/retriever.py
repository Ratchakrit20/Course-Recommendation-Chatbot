from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

def get_retriever():
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding
    )

    return vectordb.as_retriever(search_kwargs={"k": 3})

def search_docs(query: str):
    retriever = get_retriever()
    docs = retriever.invoke(query)
    return docs