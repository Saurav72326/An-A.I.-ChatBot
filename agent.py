from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from config import API_KEY, LLM_MODEL
from tools import BASIC_TOOLS
from rag import search_document

SYSTEM_PROMPT = (
    "You are a helpful, intelligent AI assistant. You can answer general "
    "questions, perform simple calculations using your tools, and search a "
    "loaded reference document when relevant. Use the conversation history "
    "for context, be concise, and if you don't know something, say so "
    "honestly rather than guessing."
)


def build_agent():
    llm = ChatGoogleGenerativeAI(
    google_api_key=API_KEY,
    model="gemini-2.0-flash"
)
    tools = BASIC_TOOLS + [search_document]
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
    return agent
