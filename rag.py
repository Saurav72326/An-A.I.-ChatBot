import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import tool

from config import API_KEY, EMBEDDING_MODEL


_retriever = None


def build_retriever(pdf_path: str, k: int = 4):

    global _retriever

    if not pdf_path or not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    print("Using embedding model:", EMBEDDING_MODEL)

    loader = PyPDFLoader(pdf_path)

    docs = loader.load()

    if not docs:
        raise ValueError("Could not extract text from the PDF.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    splits = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=API_KEY
    )

    vector_store = FAISS.from_documents(
        splits,
        embeddings
    )

    _retriever = vector_store.as_retriever(
        search_kwargs={"k": k}
    )

    return _retriever


def format_docs(docs):

    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


@tool
def search_document(query: str) -> str:
    """Search the currently uploaded PDF document."""

    if _retriever is None:
        return "No PDF document has been uploaded yet."

    results = _retriever.invoke(query)

    if not results:
        return "No relevant information was found in the PDF."

    return format_docs(results)
