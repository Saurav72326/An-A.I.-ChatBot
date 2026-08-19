import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import tool

from config import API_KEY, EMBEDDING_MODEL, PDF_PATH


_retriever = None


def build_retriever(pdf_path=None, k=4):

    global _retriever

    path = pdf_path or PDF_PATH

    if not path or not os.path.exists(path):
        print("PDF file not found:", path)
        return None

    print("Loading PDF:", path)

    loader = PyPDFLoader(path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    splits = splitter.split_documents(documents)

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

    print("PDF processed successfully.")

    return _retriever


def format_docs(docs):

    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


@tool
def search_document(query: str) -> str:
    """Search the currently uploaded PDF document for information relevant to the user's question."""

    global _retriever

    if _retriever is None:
        return (
            "No PDF document is currently loaded. "
            "Please upload a PDF first."
        )

    results = _retriever.invoke(query)

    if not results:
        return "No relevant information was found in the uploaded PDF."

    return format_docs(results)
