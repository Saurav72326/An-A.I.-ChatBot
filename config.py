import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise EnvironmentError(
        "API_KEY not found."
    )

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "gemini-flash-latest"
)

EMBEDDING_MODEL = "models/gemini-embedding-001"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///chatbot_memory.db"
)

PDF_PATH = os.getenv("PDF_PATH", "")
