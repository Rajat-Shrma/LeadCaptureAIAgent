import json
from typing import List
import sys
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .exceptions import CustomException
from .logger import logger
from .llm import create_llm
from .prompt import BASE_SYSTEM_PROMPT
from .rag import format_docs, retriever
from .state import AgentState, RouterDecision


def classify_intent(state: AgentState) -> AgentState:
    """Detect the user's current intent and update the agent state."""
    human_texts = [
        m.content for m in state["messages"][-6:] if isinstance(m, HumanMessage)
    ]
    llm = create_llm(bind_tools=False)
    classification_prompt = [
        SystemMessage(
            content=(
                "Classify the user current intent using history of messages into exactly one of these labels:\n"
                "  greeting — small talk, hi, hello, how are you, other casual talkings\n"
                "  inquiry — questions about features, pricing, plans, policies, comparisons\n"
                "  high_intent — user wants to sign up, try, buy, or get started with or USER GIVING ITS INFO FOR PURCHASING PLAN OR SHOWING INTEREST IN PRODUCT.\n\n"
                "Respond with ONLY the label. Nothing else."
            )
        ),
        HumanMessage(content="\n".join(human_texts)),
    ]

    try:
        llm_structured_output = llm.with_structured_output(RouterDecision)
        response = llm_structured_output.invoke(classification_prompt)
        raw = response.intent.strip().lower()
        intent = (
            "high_intent"
            if "high_intent" in raw
            else "inquiry" if "inquiry" in raw else "greeting"
        )
        logger.info("Detected intent: %s", intent)
        return {**state, "intent": intent}
    except Exception as e:
        logger.exception("Intent classification failed, defaulting to greeting")
        return {**state, "intent": "greeting"}


def route_intent(state: AgentState) -> str:
    intent = state.get("intent", "greeting")
    if intent == "inquiry":
        return "rag_node"
    if intent == "high_intent":
        return "lead_node"
    return "chat_node"


def _extract_lead_from_history(messages: List, current_lead: dict) -> dict:
    human_texts = [m.content for m in messages[-6:] if isinstance(m, HumanMessage)]
    
    if not human_texts:
        return current_lead

    llm = create_llm(bind_tools=False)
    extract_prompt = [
        SystemMessage(
            content=(
                "From the conversation snippets below, extract the user's:\n"
                "  - name (full name if provided)\n"
                "  - email (valid email address)\n"
                "  - platform (YouTube, Instagram, TikTok, etc.)\n\n"
                "Return a JSON object with keys: name, email, platform.\n"
                "Use null for any value not yet provided.\n"
                "Respond ONLY with valid JSON. No explanation."
            )
        ),
        HumanMessage(content="\n".join(human_texts)),
    ]

    try:
        resp = llm.invoke(extract_prompt)
        raw = resp.content.strip()
        raw = raw.removeprefix("```json").removesuffix("```").strip()
        extracted = json.loads(raw)
        merged = {
            "name": extracted.get("name") or current_lead.get("name"),
            "email": extracted.get("email") or current_lead.get("email"),
            "platform": extracted.get("platform") or current_lead.get("platform"),
        }
        logger.info("Extracted lead fields: %s", merged)
        return merged
    except Exception as e:
        logger.exception("Lead extraction failed, preserving previous lead state")
        raise CustomException(e,sys)


def lead_node(state: AgentState) -> AgentState:
    lead = state.get("lead", {"name": None, "email": None, "platform": None})
    lead_status = (
        "Lead status:\n"
        f"- Name: {lead.get('name') or 'missing'}\n"
        f"- Email: {lead.get('email') or 'missing'}\n"
        f"- Platform: {lead.get('platform') or 'missing'}\n"
    )
    system = SystemMessage(
        content=(
            f"{lead_status}\n"
            "You are collecting user information.\n"
            "PLATFORMS ARE VIDEO SHARING PLATFORM SUCH AS YOUTUBE, TIKTOK OR INSTAGRAM ETC"
            "DO NOT call any tools.\n"
            "Only ask for missing fields.\n"
        )
    )
    llm = create_llm(bind_tools=False)
    messages_to_send = [system] + [
        m for m in state["messages"] if not isinstance(m, SystemMessage)
    ]
    response = llm.invoke(messages_to_send)
    try:
        updated_lead = _extract_lead_from_history(state["messages"], lead)
    except CustomException:
        updated_lead = lead
    return {
        **state,
        "messages": [response],
        "lead": updated_lead,
    }


def chat_node(state: AgentState) -> AgentState:
    system = SystemMessage(
        content=(
            f"{BASE_SYSTEM_PROMPT}\n\n"
            "The user is just chatting. Be warm and friendly. "
            "Naturally mention you can help with AutoStream plans if relevant."
        )
    )
    llm = create_llm(bind_tools=False)
    messages_to_send = [system] + [
        m for m in state["messages"] if not isinstance(m, SystemMessage)
    ]
    response = llm.invoke(messages_to_send)
    return {**state, "messages": [response]}


def rag_node(state: AgentState) -> AgentState:
    last_human = next(
        (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        "",
    )
    try:
        docs = retriever.invoke(last_human)
        context = format_docs(docs)
    except Exception:
        logger.exception("RAG retrieval failed, continuing without external context")
        context = ""

    logger.info("Retrieved %d characters of context.", len(context))
    system = SystemMessage(
        content=(
            f"{BASE_SYSTEM_PROMPT}\n\n" f"[RETRIEVED CONTEXT]\n{context}\n[END CONTEXT]"
        )
    )
    llm = create_llm(bind_tools=False)
    messages_to_send = [system] + [
        m for m in state["messages"] if not isinstance(m, SystemMessage)
    ]
    response = llm.invoke(messages_to_send)
    return {
        **state,
        "messages": [response],
        "rag_context": context,
    }


def tool_call(state: AgentState) -> AgentState:
    from .tools import mock_capture_lead

    lead = state["lead"]
    result = mock_capture_lead.invoke(
        {
            "name": lead["name"],
            "email": lead["email"],
            "platform": lead["platform"],
        }
    )
    return {
        **state,
        "messages": state["messages"]
        + [AIMessage(content="You're all set. We will contact you soon.")],
        "lead": result,
    }


def tool_router(state: AgentState) -> str:
    lead = state.get("lead", {})
    is_complete = all(
        [
            lead.get("name"),
            lead.get("email"),
            lead.get("platform"),
        ]
    )
    if is_complete:
        logger.info("Lead complete, calling tool")
        return "tool_call"
    logger.info("Lead incomplete, continuing collection")
    return "lead_node"
