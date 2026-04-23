import logging
from pathlib import Path


# Define log directory relative to this file's parent parent (project root)
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def get_logger(name: str = "lead_agent") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Ensure logs directory exists
        LOG_DIR.mkdir(exist_ok=True, parents=True)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler
        log_file = LOG_DIR / "lead_agent.log"
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)
    return logger


logger = get_logger()
