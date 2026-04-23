import sqlite3
from pathlib import Path
from typing import Union
import sys
from langgraph.checkpoint.sqlite import SqliteSaver

from .config import DB_NAME, ROOT
from .exceptions import CustomException
from .logger import logger


def get_sqlite_checkpointer(db_path: Union[str, Path] = DB_NAME) -> SqliteSaver:
    path = Path(db_path)
    if not path.is_absolute():
        path = ROOT / path

    try:
        logger.info("Opening SQLite database at %s", path)
        conn = sqlite3.connect(database=str(path), check_same_thread=False)
        return SqliteSaver(conn=conn)
    except Exception as e:
        logger.exception("Failed to open SQLite database %s", path)
        raise CustomException(e,sys)
