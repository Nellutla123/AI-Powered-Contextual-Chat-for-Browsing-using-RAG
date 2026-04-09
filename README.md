# Chrome RAG Plugin

A browser-based RAG (Retrieval-Augmented Generation) system that allows you to chat with any webpage you are currently viewing. It uses a FastAPI backend with LangChain and ChromaDB for local vector storage, and an OpenRouter-powered LLM for answering questions.

## Project Structure

- `backend/`: FastAPI server that handles text ingestion and vector search.
- `extension/`: Chrome extension files (manifest, background, content scripts, and UI).

## Features

- **Context-Aware Chat**: Ingests text from the active tab and provides answers based on that content.
- **Local Vector Store**: Saves document embeddings locally for fast retrieval.
- **OpenRouter Integration**: Uses powerful LLMs via OpenRouter for generating responses.

## Setup Instructions

### 1. Backend Setup

1.  Navigate to the `backend/` directory.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment Variables:
    Create a `.env` file in the `backend/` directory with the following:
    ```env
    OPENROUTER_API_KEY=your_api_key_here
    ```
5.  Run the Backend Server:
    ```bash
    python main.py
    ```
    The server will start at `http://localhost:8000`.

### 2. Extension Setup

1.  Open Chrome and navigate to `chrome://extensions/`.
2.  Enable **Developer mode** in the top right corner.
3.  Click on **Load unpacked**.
4.  Select the `extension/` folder in this project directory.

## Usage

1.  Open any webpage you want to chat with.
2.  Click on the **Chrome RAG Plugin** icon in your extension bar.
3.  The plugin will automatically ingest the page content (or you can trigger it).
4.  Start asking questions about the page!

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (Chrome Extension V3)
- **Backend**: Python, FastAPI
- **RAG Stack**: LangChain, ChromaDB / Pinecone
- **LLM**: Gemini 3 Flash / Llama 3 (via OpenRouter)
