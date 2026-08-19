# AI Chatbot using LangChain and Gemini

A memory-enabled and document-aware AI chatbot built using **LangChain**, **Google Gemini**, **SQLite**, and **FAISS**.

The chatbot can have conversations, remember previous messages, perform simple mathematical calculations using tools, and search information from a PDF document using Retrieval-Augmented Generation (RAG).

## Features

* 🤖 Chat with Google Gemini
* 🧠 Conversation memory using SQLite
* ➕ Addition tool
* ✖️ Multiplication tool
* 📄 PDF document search using RAG
* 🔍 FAISS vector similarity search
* 🧩 LangChain agent with multiple tools
* 🔐 Environment variable configuration using `.env`

## Project Architecture


User
 │
 ▼
main.py
 │
 ├── Conversation Memory ──► SQLite Database
 │
 ├── LangChain Agent
 │      │
 │      ├── Gemini LLM
 │      ├── Add Tool
 │      ├── Multiply Tool
 │      └── Document Search Tool
 │
 ▼
Response


When a PDF document is configured, the document search workflow is:


PDF
 │
 ▼
PyPDFLoader
 │
 ▼
Text Chunking
 │
 ▼
Google Embeddings
 │
 ▼
FAISS Vector Store
 │
 ▼
Retriever
 │
 ▼
Relevant Document Response


## Project Structure


chatbot/
│
├── agent.py
├── config.py
├── main.py
├── memory.py
├── rag.py
├── tools.py
│
├── requirements.txt
├── .env
└── README.md


### File Description

| File        | Description                                                              |
| ----------- | ------------------------------------------------------------------------ |
| `main.py`   | Main entry point and chatbot interaction loop                            |
| `agent.py`  | Creates the LangChain agent and Gemini model                             |
| `config.py` | Loads environment variables and application configuration                |
| `memory.py` | Stores and retrieves conversation history using SQLite                   |
| `tools.py`  | Contains calculator tools such as addition and multiplication            |
| `rag.py`    | Handles PDF loading, chunking, embeddings, FAISS, and document retrieval |
| `.env`      | Stores API key, model settings, database URL, and optional PDF path      |

## Installation
Clone or download the project and move into the project directory:
cd chatbot

Create a virtual environment:
python -m venv venv

Activate it on Windows:
venv\Scripts\activate


Install the required packages:
pip install -r requirements.txt

## Environment Configuration

Create a `.env` file in the project directory.

Example:

API_KEY=your_google_gemini_api_key

LLM_MODEL=gemini-flash-latest

EMBEDDING_MODEL=models/embedding-001

DATABASE_URL=sqlite:///chatbot_memory.db

PDF_PATH=

`PDF_PATH` is optional. If it is left empty, the chatbot will continue to work, but document search will not be available.


### Example with a PDF

PDF_PATH=C:\Users\YourName\Documents\sample.pdf


## Running the Chatbot

Run the application using:
python main.py

Example:
Starting chatbot...

Chatbot ready. Type 'exit' to quit.

You: Hello

Bot: Hello! How can I help you today?

You: Add 15 and 25

Bot: 40

You: exit

Goodbye!


## Available Tools

### Add

Adds two numbers.

Example:

You: Add 10 and 20

### Multiply

Multiplies two numbers.

Example:

You: Multiply 5 and 8

The project defines these two basic LangChain tools and combines them into `BASIC_TOOLS`.

### Search Document

If a valid PDF path is provided, the chatbot:

1. Loads the PDF.
2. Splits it into smaller text chunks.
3. Creates embeddings.
4. Stores the embeddings in FAISS.
5. Retrieves relevant document sections when required.

The current implementation uses `PyPDFLoader`, `RecursiveCharacterTextSplitter`, Google embeddings, and FAISS.

## Conversation Memory

Conversation history is stored in an SQLite database.

Each message contains:

* User ID
* Message role (`user` or `assistant`)
* Message content

The chatbot retrieves recent messages and formats them as conversation history before generating a response.

## Configuration

The application configuration includes:

text
API_KEY
LLM_MODEL
EMBEDDING_MODEL
DATABASE_URL
PDF_PATH


These values are loaded from environment variables in `config.py`.

## Requirements

Install all dependencies using:
pip install -r requirements.txt

## Security

Never upload your `.env` file containing your real API key to GitHub.


Use an `.env.example` file instead:

API_KEY=your_api_key_here
LLM_MODEL=gemini-flash-latest
EMBEDDING_MODEL=models/embedding-001
DATABASE_URL=sqlite:///chatbot_memory.db
PDF_PATH=


## Technologies Used

* Python
* LangChain
* Google Gemini
* Google Generative AI
* FAISS
* SQLite
* SQLAlchemy
* PyPDF
* Python Dotenv

## Future Improvements

Possible improvements include:

* Web-based user interface using Streamlit or Flask
* Multiple user accounts
* User authentication
* Streaming responses
* Support for multiple documents
* Persistent FAISS vector database
* Chat history deletion through commands
* Better error handling for Gemini API quota limits
* Conversation summarization for long chat histories

## Author

Developed as a learning project demonstrating:

* Large Language Models
* LangChain agents
* Tool calling
* Conversation memory
* Retrieval-Augmented Generation
* Vector databases
* Document search
