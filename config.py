import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress repetitive SDK deprecation warnings for cleaner UI logs
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")
DATA_DIR = BASE_DIR / "data"

class ChromaDefaultEmbeddings:
    """
    LangChain compatible embedding wrapper around Chroma's local ONNX MiniLM engine.
    Runs 100% locally and offline without consuming any API tokens or requiring network calls.
    """
    def __init__(self):
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        self.ef = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.ef(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.ef([text])[0]


def get_api_keys():
    """Return dictionary of available API keys."""
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return {
        "gemini": os.getenv("GEMINI_API_KEY", "").strip(),
        "groq": os.getenv("GROQ_API_KEY", "").strip(),
        "openai": os.getenv("OPENAI_API_KEY", "").strip(),
    }

def get_default_provider():
    return os.getenv("DEFAULT_LLM_PROVIDER", "gemini").lower()

def get_llm(provider: str = None, model: str = None, temperature: float = 0.2):
    """
    Factory function returning the LangChain ChatModel instance
    based on the requested provider (Gemini, Groq, OpenAI).
    """
    keys = get_api_keys()
    chosen_provider = (provider or get_default_provider()).lower()

    if chosen_provider == "gemini":
        api_key = keys["gemini"]
        if not api_key or "your_" in api_key:
            raise ValueError(
                "Gemini API Key is missing! Please paste your key in the .env file or Streamlit sidebar."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI
        model_name = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature
        )

    elif chosen_provider == "groq":
        api_key = keys["groq"]
        if not api_key or "your_" in api_key:
            raise ValueError(
                "Groq API Key is missing! Please paste your key in the .env file or Streamlit sidebar."
            )
        from langchain_groq import ChatGroq
        model_name = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        return ChatGroq(
            model_name=model_name,
            groq_api_key=api_key,
            temperature=temperature
        )

    elif chosen_provider == "openai":
        api_key = keys["openai"]
        if not api_key or "your_" in api_key:
            raise ValueError(
                "OpenAI API Key is missing! Please paste your key in the .env file or Streamlit sidebar."
            )
        from langchain_openai import ChatOpenAI
        model_name = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            temperature=temperature
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {chosen_provider}. Choose 'gemini', 'groq', or 'openai'.")

def get_embeddings():
    """
    Returns high-speed local ONNX MiniLM embeddings (LangChain compliant).
    Ensures zero-token, zero-latency vector similarity search in ChromaDB.
    """
    return ChromaDefaultEmbeddings()
