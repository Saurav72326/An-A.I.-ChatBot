import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise EnvironmentError(
        "API_KEY not found. Create a .env file (see .env.example) with your "
        "Google Generative AI API key."
    )

# Chat / reasoning model
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Embedding model used for RAG
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

# Where chat history is persisted
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///chatbot_memory.db")

# Optional PDF to index for retrieval-augmented answers
PDF_PATH = os.getenv("PDF_PATH", "")
