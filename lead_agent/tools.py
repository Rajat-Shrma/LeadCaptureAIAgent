from langchain_core.tools import tool

from .logger import logger


@tool
def mock_capture_lead(name: str, email: str, platform: str) -> dict:
    """Mock function for lead capture tool execution."""
    logger.info(
        "Lead captured successfully: name=%s, email=%s, platform=%s",
        name,
        email,
        platform,
    )
    print(f'Lead Captured Successfully : {name}, {email}, {platform}')
    return {"status": "success"}


tools = [mock_capture_lead]
