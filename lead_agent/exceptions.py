import sys
from logger import logging


def get_error_message(error_message, error_details: sys):
    """Build a detailed error message with file name and line from exception traceback."""
    _, _, exc_tb = error_details.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = (
        f"Error occurred at line number [{line_number}] of file [{file_name}]. "
        f"Error says: [{error_message}]"
    )
    return error_message


class CustomException(Exception):
    """Custom exception that records traceback file and line information."""

    def __init__(self, error_message, error_details: sys):
        super().__init__(error_message)
        self.error_message = get_error_message(error_message, error_details)

    def __str__(self):
        return self.error_message


if __name__ == "__main__":
    logging.info("logging class working")
    try:
        1 / 0
    except Exception as e:
        raise CustomException("CustomException Class Working!", sys)
