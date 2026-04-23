import os
from pathlib import Path
from dotenv import load_dotenv

from .exceptions import CustomException
from .logger import logger

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DB_NAME = "chatbot.db"
CHROMA_DIR = ROOT / "chroma_db"


def get_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    #api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("Missing required environment variable: GOOGLE_API_KEY")
        raise CustomException("GOOGLE_API_KEY is not set.")
    return api_key
