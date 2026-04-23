from pathlib import Path
from typing import List
import sys
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .config import CHROMA_DIR
from .exceptions import CustomException
from .logger import logger


CHROMA_DIR.mkdir(exist_ok=True, parents=True)
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vectorstore = Chroma(
    collection_name="my_collection",
    embedding_function=embedding_model,
    persist_directory=str(CHROMA_DIR),
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})


def load_documents(file_path: str) -> List[Document]:
    loader = UnstructuredMarkdownLoader(file_path=file_path)
    return loader.load()


def splitting_documents(docs: List[Document]) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=25,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_documents(docs)


def index_document_to_chroma(file_path: str) -> bool:
    try:
        docs = load_documents(file_path)
        splits = splitting_documents(docs)
        vectorstore.add_documents(splits)
        logger.info("Indexed document to Chroma: %s", file_path)
        return True
    except Exception as e:
        logger.exception("Error indexing document %s", file_path)
        raise CustomException(e,sys)


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

