from langgraph.graph import StateGraph, START, END

from .nodes import (
    classify_intent,
    route_intent,
    rag_node,
    lead_node,
    chat_node,
    tool_call,
    tool_router,
)
from .state import AgentState
from .utils import get_sqlite_checkpointer


def build_chatbot(checkpointer=None):
    if checkpointer is None:
        checkpointer = get_sqlite_checkpointer()

    graph = StateGraph(AgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("rag_node", rag_node)
    graph.add_node("lead_node", lead_node)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_call", tool_call)

    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_intent,
        {"rag_node": "rag_node", "lead_node": "lead_node", "chat_node": "chat_node"},
    )
    graph.add_edge("rag_node", END)
    graph.add_edge("chat_node", END)
    graph.add_conditional_edges(
        "lead_node",
        tool_router,
        {"tool_call": "tool_call", "lead_node": END},
    )
    graph.add_edge("tool_call", END)

    return graph.compile(checkpointer=checkpointer)
