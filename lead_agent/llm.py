from .config import get_api_key
from .exceptions import CustomException
from .logger import logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import sys
def create_llm(bind_tools: bool = False):
    api_key = get_api_key()
    if not api_key:
        raise CustomException("Unable to create LLM without GOOGLE_API_KEY.")

    logger.info("Initializing ChatGoogleGenerativeAI model")
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")
    #llm = ChatGroq(model='openai/gpt-oss-20b')
    if bind_tools:
        try:
            from .tools import tools

            return llm.bind_tools(tools)
        except Exception as e:
            logger.exception("Unable to bind tools to LLM")
            raise CustomException(e, sys)

    return llm
