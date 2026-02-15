# Latest Dependencies & Setup Guide

## Requirements.txt (2025 Latest Versions)

```txt
# =============================================================================
# API MODERNIZATION - REQUIREMENTS
# =============================================================================

# -----------------------------------------------------------------------------
# Core Python
# -----------------------------------------------------------------------------
python-dotenv>=1.0.0

# -----------------------------------------------------------------------------
# Code Parsing (Tree-sitter)
# -----------------------------------------------------------------------------
tree-sitter>=0.21.0
tree-sitter-java>=0.21.0

# -----------------------------------------------------------------------------
# Graph Processing
# -----------------------------------------------------------------------------
networkx>=3.2

# -----------------------------------------------------------------------------
# LangChain Ecosystem (Latest Stable - Jan 2025)
# -----------------------------------------------------------------------------
langchain>=0.3.13
langchain-core>=0.3.28
langchain-community>=0.3.13
langchain-text-splitters>=0.3.4

# LangChain Google Integration
langchain-google-genai>=2.0.8

# LangGraph for Agents
langgraph>=0.2.63
langgraph-checkpoint>=2.0.8

# -----------------------------------------------------------------------------
# Vector Store & Embeddings
# -----------------------------------------------------------------------------
faiss-cpu>=1.9.0

# HuggingFace Embeddings (fallback)
sentence-transformers>=3.3.1
torch>=2.0.0  # CPU version, add +cu118 for CUDA

# -----------------------------------------------------------------------------
# Google AI
# -----------------------------------------------------------------------------
google-generativeai>=0.8.3

# -----------------------------------------------------------------------------
# Data Validation
# -----------------------------------------------------------------------------
pydantic>=2.10.0

# -----------------------------------------------------------------------------
# Web UI (Optional)
# -----------------------------------------------------------------------------
streamlit>=1.41.0

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
gitpython>=3.1.43
```

---

## Environment Variables

Create a `.env` file:

```bash
# Google AI API Key (required)
GOOGLE_API_KEY=your-api-key-here

# Alternative key names (the code checks all of these)
# CODEBASE_GEMINI_KEY=your-api-key-here
# GOOGLE_GENAI_API_KEY=your-api-key-here

# Optional: Specify model
CODEBASE_GEMINI_MODEL=gemini-2.0-flash
```

---

## Installation

### Option 1: pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Poetry

```bash
poetry init
poetry add langchain langchain-core langchain-community langchain-google-genai
poetry add langgraph faiss-cpu sentence-transformers
poetry add tree-sitter tree-sitter-java networkx pydantic
poetry add streamlit python-dotenv gitpython
```

### Option 3: Conda

```bash
conda create -n api-mod python=3.11
conda activate api-mod
pip install -r requirements.txt
```

---

## Version Compatibility Notes

### LangChain 0.3.x Breaking Changes

1. **Import Changes**:
```python
# OLD (0.2.x)
from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS

# NEW (0.3.x)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
```

2. **Agent Creation**:
```python
# OLD (0.2.x)
from langchain.agents import initialize_agent, AgentType
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# NEW (0.3.x) - Using LangGraph
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(model, tools)
```

3. **Retriever Tool**:
```python
# OLD
from langchain.agents import create_retriever_tool

# NEW (same import but from different package)
from langchain.tools.retriever import create_retriever_tool
```

4. **Structured Output**:
```python
# OLD (manual parsing)
response = llm.invoke(prompt)
result = json.loads(response.content)

# NEW (Pydantic integration)
structured_llm = llm.with_structured_output(MyPydanticModel)
result = structured_llm.invoke(prompt)  # Returns MyPydanticModel instance
```

### LangGraph 0.2.x Patterns

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

# Create agent with memory
memory = MemorySaver()
agent = create_react_agent(model, tools, checkpointer=memory)

# Invoke with thread for conversation history
config = {"configurable": {"thread_id": "session-1"}}
response = agent.invoke(
    {"messages": [HumanMessage(content="Analyze my API")]},
    config
)
```

---

## Google Gemini Models (2025)

| Model | Use Case | Notes |
|-------|----------|-------|
| `gemini-2.0-flash` | Fast responses, coding | Recommended for agents |
| `gemini-2.5-flash-lite` | Lightweight tasks | Lower cost |
| `gemini-1.5-pro` | Complex reasoning | Higher quality |
| `models/gemini-embedding-001` | Embeddings | 768/1536/3072 dims |
| `models/text-embedding-004` | Latest embeddings | Better quality |

### Usage

```python
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Chat model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    task_type="retrieval_document"
)
```

---

## Troubleshooting

### FAISS Installation Issues

```bash
# If faiss-cpu fails, try:
pip install faiss-cpu --no-cache-dir

# For Apple Silicon (M1/M2/M3):
pip install faiss-cpu

# For GPU support:
pip install faiss-gpu
```

### Tree-sitter Compilation

```bash
# If tree-sitter-java fails:
pip install --upgrade pip setuptools wheel
pip install tree-sitter tree-sitter-java
```

### Google API Quota

If you hit Gemini API quota limits:
1. Use local embeddings as fallback
2. Implement request rate limiting
3. Consider Gemini API billing

```python
# Force local embeddings
manager = VectorStoreManager(use_local=True)
```

---

## Quick Test

```python
# test_setup.py
import os
from dotenv import load_dotenv

load_dotenv()

# Test LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
response = llm.invoke("Say hello")
print(f"LLM: {response.content}")

# Test Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector = embeddings.embed_query("test")
print(f"Embedding dims: {len(vector)}")

# Test FAISS
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
docs = [Document(page_content="Hello world")]
vs = FAISS.from_documents(docs, embeddings)
results = vs.similarity_search("hello", k=1)
print(f"FAISS: {results[0].page_content}")

# Test Tree-sitter
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
parser = Parser()
parser.set_language(Language(tsjava.language(), 'java'))
print("Tree-sitter: OK")

print("\n✅ All components working!")
```

Run:
```bash
python test_setup.py
```
