

# Lead Collecting Agent

![Agent Architecture](agent_orchestration.png)

This project is now organized as a small Python package under `lead_agent`.

## Structure

- `lead_agent/`
  - `graph.py`: builds and compiles the LangGraph chatbot flow
  - `nodes.py`: intent classification, RAG, chat, and lead capture node handlers
  - `rag.py`: document indexing and retriever setup
  - `llm.py`: LLM initialization and environment validation
  - `tools.py`: mock lead capture tool
  - `config.py`: environment constants and configuration helpers
  - `utils.py`: persistence helpers for SQLite checkpointing
  - `prompt.py`: the assistant system prompt

- `streamlit_app.py`: Streamlit UI entrypoint using the package
- `requirements.txt`: dependency list

## Usage

1. Create a `.env` with `GOOGLE_API_KEY` set.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit UI:
   ```bash
   streamlit run streamlit_app.py
   ```

## Improvements

- Centralized logging with `logging`
- Stronger configuration and environment validation
- Clear module boundaries for agent logic, RAG retrieval, and prompt setup
- Root entrypoints now import from `lead_agent`
"# LeadCaptureAIAgent" 
