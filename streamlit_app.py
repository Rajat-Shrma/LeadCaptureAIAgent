import streamlit as st
import uuid
from langchain_core.messages import HumanMessage, AIMessage

from lead_agent.graph import build_chatbot

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = build_chatbot()

st.title("AutoStream AI Assistant")

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(msg)

user_input = st.chat_input("Ask something...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.chat_history.append(("user", user_input))

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    response = st.session_state.chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )

    last_msg = response["messages"][-1]
    if isinstance(last_msg, AIMessage):
        if getattr(last_msg, "tool_calls", None):
            bot_reply = "[Calling tool...]"
        else:
            bot_reply = last_msg.content
    else:
        bot_reply = str(last_msg)

    st.chat_message("assistant").write(bot_reply)
    st.session_state.chat_history.append(("assistant", bot_reply))
