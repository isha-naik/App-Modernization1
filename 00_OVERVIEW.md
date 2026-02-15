# API Modernization - Architecture Reference Guide

## Purpose

This documentation provides a comprehensive reference for building an **API Modernization** tool using patterns and components from the Discovery Agent project. Each document explains a feature, how it works, and how to adapt it for API modernization with the latest LangChain and LangGraph versions.

---

## Documentation Index

| Document | Component | Description |
|----------|-----------|-------------|
| [01_PARSER_MODULE.md](./01_PARSER_MODULE.md) | Parser | Tree-sitter based Java parsing, annotation extraction |
| [02_KNOWLEDGE_GRAPH.md](./02_KNOWLEDGE_GRAPH.md) | Knowledge Graph | NetworkX graph for code structure |
| [03_RAG_INFRASTRUCTURE.md](./03_RAG_INFRASTRUCTURE.md) | RAG System | FAISS vectorstore, embeddings, agents |
| [04_INFERENCE_MODULE.md](./04_INFERENCE_MODULE.md) | Inference | LLM-powered detection with structured output |
| [05_EXPERT_RAG_MIGRATION.md](./05_EXPERT_RAG_MIGRATION.md) | Expert RAG | Knowledge base indexing, AI migration |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        API MODERNIZATION SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    1. DISCOVERY LAYER                             │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │   │
│  │  │ Parser      │───>│ Knowledge   │───>│ Graph Summarizer    │  │   │
│  │  │ (tree-sitter)    │ Graph       │    │ (Pattern Detection) │  │   │
│  │  └─────────────┘    │ (NetworkX)  │    └─────────────────────┘  │   │
│  │                     └─────────────┘                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                │                                         │
│                                ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    2. ANALYSIS LAYER                              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │                     Dual RAG System                          │ │   │
│  │  │  ┌─────────────────┐        ┌────────────────────────────┐  │ │   │
│  │  │  │ Code RAG        │        │ Expert RAG                 │  │ │   │
│  │  │  │ (Codebase       │        │ (Best Practices,           │  │ │   │
│  │  │  │  Vectorstore)   │        │  Migration Guides)         │  │ │   │
│  │  │  └─────────────────┘        └────────────────────────────┘  │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  │                                │                                  │   │
│  │  ┌─────────────────────────────┼─────────────────────────────┐   │   │
│  │  │                    LLM Analysis                            │   │   │
│  │  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │   │   │
│  │  │  │ API Style     │  │ REST Maturity │  │ OpenAPI       │  │   │   │
│  │  │  │ Detector      │  │ Analyzer      │  │ Compliance    │  │   │   │
│  │  │  └───────────────┘  └───────────────┘  └───────────────┘  │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                │                                         │
│                                ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                 3. MODERNIZATION LAYER                            │   │
│  │  ┌───────────────────────────────────────────────────────────┐   │   │
│  │  │              AI Modernization Engine                       │   │   │
│  │  │  - OpenAPI Spec Generation                                 │   │   │
│  │  │  - REST Best Practices Recommendations                     │   │   │
│  │  │  - Versioning Strategy Suggestions                         │   │   │
│  │  │  - Security Pattern Analysis                               │   │   │
│  │  │  - Breaking Change Detection                               │   │   │
│  │  └───────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                │                                         │
│                                ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    4. OUTPUT LAYER                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │   │
│  │  │ OpenAPI     │  │ Migration   │  │ Modernization           │   │   │
│  │  │ Specs       │  │ Plan        │  │ Report                  │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## What to Reuse from Discovery Agent

### Direct Reuse (~40%)

| Component | Files | Why Reuse |
|-----------|-------|-----------|
| **Parser** | `generic_java_parser.py`, `relationship_extractor.py` | Already extracts annotations, methods, endpoints |
| **Knowledge Graph** | `graph.py` | Perfect structure for API relationships |
| **VectorStoreManager** | `vectorstore_manager.py` | Embedding + FAISS infrastructure |
| **RetrieverTool** | `retriever_tool.py` | Agent tool creation pattern |
| **GraphToDocuments** | `graph_to_documents.py` | Document conversion pattern |

### Adapt (~25%)

| Component | Adaptation Needed |
|-----------|-------------------|
| **FrameworkDetectorV2** | Change to APIStyleDetector |
| **GraphSummarizer** | Focus on API-specific patterns |
| **ExpertRAGManager** | New knowledge base for API standards |
| **AIMigrationEngine** | Become APIModernizationEngine |

### Build New (~35%)

| Component | Purpose |
|-----------|---------|
| **OpenAPIGenerator** | Generate OpenAPI 3.x specs from code |
| **RESTMaturityAnalyzer** | Richardson Maturity Model assessment |
| **VersioningDetector** | Detect/recommend versioning strategy |
| **SecurityPatternAnalyzer** | Auth/authz pattern detection |
| **BreakingChangeDetector** | Identify breaking API changes |

---

## Latest Dependencies (2025)

```txt
# requirements.txt

# Core
python>=3.10

# Parsing
tree-sitter>=0.21.0
tree-sitter-java>=0.21.0

# Graph
networkx>=3.2

# LangChain & LangGraph (Latest)
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0
langchain-google-genai>=2.0.0
langgraph>=0.2.0

# Embeddings & Vector Store
faiss-cpu>=1.8.0
sentence-transformers>=3.0.0

# LLM
google-generativeai>=0.8.0

# Data Validation
pydantic>=2.0.0

# Web UI (optional)
streamlit>=1.35.0

# Utilities
python-dotenv>=1.0.0
gitpython>=3.1.0
```

---

## Quick Start Template

### 1. Project Structure

```
api-modernization/
├── src/
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── java_parser.py           # From discovery-agent
│   │   └── api_extractor.py         # NEW: Enhanced API extraction
│   ├── knowledge_graph/
│   │   ├── __init__.py
│   │   └── graph.py                 # From discovery-agent (enhanced)
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── vectorstore.py           # From discovery-agent
│   │   ├── documents.py             # From discovery-agent (enhanced)
│   │   └── agents/
│   │       └── api_agent.py         # NEW: API analysis agent
│   ├── inference/
│   │   ├── __init__.py
│   │   ├── api_style_detector.py    # NEW: Adapted from framework_detector
│   │   └── maturity_analyzer.py     # NEW: REST maturity analysis
│   ├── modernization/
│   │   ├── __init__.py
│   │   ├── expert_rag.py            # From discovery-agent (adapted)
│   │   ├── openapi_generator.py     # NEW: OpenAPI spec generation
│   │   └── recommendations.py       # NEW: Modernization recommendations
│   └── utils/
│       └── __init__.py
├── api_knowledge/                    # NEW: API best practices KB
│   ├── standards/
│   │   ├── openapi_3.1.md
│   │   └── rest_best_practices.md
│   └── patterns/
│       ├── versioning.md
│       ├── error_handling.md
│       └── authentication.md
├── app.py                            # Streamlit UI
├── requirements.txt
└── README.md
```

### 2. Basic Usage Flow

```python
# 1. Parse codebase
from src.parser.java_parser import GenericJavaParser
from src.parser.api_extractor import APIExtractor
from src.knowledge_graph.graph import KnowledgeGraph

kg = KnowledgeGraph()
parser = GenericJavaParser()
parser.parse_directory("/path/to/project", kg)

api_extractor = APIExtractor(parser)
api_extractor.extract_all_apis(kg)

# 2. Create RAG indices
from src.rag.vectorstore import VectorStoreManager
from src.rag.documents import convert_api_graph_to_documents

documents = convert_api_graph_to_documents(kg)
manager = VectorStoreManager()
vectorstore = manager.create_vectorstore(documents, "my-api")

# 3. Analyze APIs
from src.inference.api_style_detector import APIStyleDetector
from src.inference.maturity_analyzer import RESTMaturityAnalyzer

detector = APIStyleDetector()
style_result = detector.detect_api_style(kg)

analyzer = RESTMaturityAnalyzer()
maturity_result = analyzer.analyze(kg.endpoints.values())

# 4. Generate modernization plan
from src.modernization.recommendations import APIModernizationEngine

engine = APIModernizationEngine()
plan = engine.generate_plan(
    api_discovery=kg.export_to_dict(),
    target_standard="OpenAPI 3.1",
    goals=["REST Level 3", "Consistent error handling", "JWT authentication"]
)

# 5. Generate OpenAPI spec
from src.modernization.openapi_generator import OpenAPIGenerator

generator = OpenAPIGenerator()
openapi_spec = generator.generate(kg, plan)
```

---

## Key Patterns to Follow

### 1. Structured Output with Pydantic

```python
from pydantic import BaseModel, Field

class APIAnalysisResult(BaseModel):
    style: str = Field(description="REST, GraphQL, SOAP, gRPC")
    maturity_level: int = Field(ge=0, le=3)
    issues: List[str]
    recommendations: List[str]

# Use with LLM
structured_llm = llm.with_structured_output(APIAnalysisResult)
result = structured_llm.invoke(prompt)
```

### 2. LangGraph Agent Pattern

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def search_api_knowledge(query: str) -> str:
    """Search API best practices and standards."""
    docs = vectorstore.similarity_search(query, k=5)
    return "\n\n".join([d.page_content for d in docs])

agent = create_react_agent(model, tools=[search_api_knowledge])
```

### 3. Dual RAG Architecture

```python
# Code RAG - understanding existing APIs
code_retriever = code_vectorstore.as_retriever(search_kwargs={"k": 10})

# Expert RAG - best practices and standards
expert_retriever = expert_vectorstore.as_retriever(search_kwargs={"k": 5})

# Combine in prompt
code_context = code_retriever.invoke(query)
expert_context = expert_retriever.invoke(query)
```

---

## Next Steps

1. **Set up project structure** following the template above
2. **Copy reusable components** from discovery-agent
3. **Create API knowledge base** with OpenAPI specs, REST best practices
4. **Build enhanced extractors** for API-specific data
5. **Implement analyzers** (maturity, versioning, security)
6. **Create modernization engine** with OpenAPI generation

---

## Resources

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
