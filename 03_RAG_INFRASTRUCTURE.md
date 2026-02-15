# RAG Infrastructure Documentation

## Overview

The RAG (Retrieval Augmented Generation) infrastructure enables semantic search over the codebase and expert knowledge. It uses FAISS for vector storage and supports both Gemini and local HuggingFace embeddings.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     RAG Infrastructure                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐    ┌──────────────────────────────────┐ │
│  │ Knowledge Graph │───>│ GraphToDocuments                 │ │
│  └─────────────────┘    │ (Convert to LangChain Documents) │ │
│                         └──────────────────────────────────┘ │
│                                      │                        │
│                                      ▼                        │
│                         ┌──────────────────────────────────┐ │
│                         │ VectorStoreManager               │ │
│                         │ ┌────────────┐  ┌─────────────┐  │ │
│                         │ │ Embeddings │  │ FAISS Store │  │ │
│                         │ │ (Gemini/HF)│  │             │  │ │
│                         │ └────────────┘  └─────────────┘  │ │
│                         └──────────────────────────────────┘ │
│                                      │                        │
│                                      ▼                        │
│                         ┌──────────────────────────────────┐ │
│                         │ RetrieverTool                    │ │
│                         │ (LangChain Tool for Agents)      │ │
│                         └──────────────────────────────────┘ │
│                                      │                        │
│                                      ▼                        │
│                         ┌──────────────────────────────────┐ │
│                         │ ArchitectureAgent                │ │
│                         │ (ReAct Agent with RAG)           │ │
│                         └──────────────────────────────────┘ │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Component 1: GraphToDocuments

**Purpose**: Convert Knowledge Graph nodes to LangChain Document objects for vectorization.

**Location**: `src/rag/graph_to_documents.py`

### GraphDocumentConverter Class

```python
from langchain_core.documents import Document
from src.knowledge_graph.graph import KnowledgeGraph

class GraphDocumentConverter:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph

    def convert_to_documents(self) -> List[Document]:
        """Convert entire knowledge graph to documents"""
        documents = []
        documents.extend(self._convert_classes())
        documents.extend(self._convert_methods())
        documents.extend(self._convert_endpoints())
        return documents
```

### Document Structure

#### Class Documents
```python
def _convert_classes(self) -> List[Document]:
    for class_id, class_node in self.kg.classes.items():
        content_parts = [
            f"Type: {class_node.java_type.upper()}",
            f"Name: {class_node.name}",
            f"Full Name: {class_node.package}.{class_node.name}",
            f"Annotations: {', '.join([f'@{ann}' for ann in class_node.annotations])}",
            f"Methods ({len(class_methods)}): {', '.join(class_methods[:10])}"
        ]

        doc = Document(
            page_content="\n".join(content_parts),
            metadata={
                "type": "class",
                "java_type": class_node.java_type,
                "class_name": class_node.name,
                "full_name": f"{class_node.package}.{class_node.name}",
                "package": class_node.package,
                "annotations": class_node.annotations,
                "file_path": class_node.file_path,
            }
        )
        documents.append(doc)
```

#### Method Documents
```python
def _convert_methods(self) -> List[Document]:
    for method_id, method_node in self.kg.methods.items():
        content_parts = [
            f"Type: METHOD",
            f"Method Name: {method_node.name}",
            f"Class: {method_node.class_name}",
            f"Return Type: {method_node.return_type}",
            f"Parameters: {params_str}",
            f"Annotations: {annotations_str}"
        ]

        doc = Document(
            page_content="\n".join(content_parts),
            metadata={
                "type": "method",
                "method_name": method_node.name,
                "class_name": method_node.class_name,
                "annotations": method_node.annotations,
            }
        )
```

#### Endpoint Documents
```python
def _convert_endpoints(self) -> List[Document]:
    for endpoint_id, endpoint in self.kg.endpoints.items():
        content_parts = [
            f"Type: REST ENDPOINT",
            f"HTTP Method: {endpoint.http_method}",
            f"Path: {endpoint.path}",
            f"Handler: {endpoint.handler_class}.{endpoint.handler_method}"
        ]

        doc = Document(
            page_content="\n".join(content_parts),
            metadata={
                "type": "endpoint",
                "http_method": endpoint.http_method,
                "path": endpoint.path,
                "handler_class": endpoint.handler_class,
            }
        )
```

### Usage
```python
from src.rag.graph_to_documents import convert_graph_to_documents

documents = convert_graph_to_documents(knowledge_graph)
print(f"Created {len(documents)} documents")
```

---

## Component 2: VectorStoreManager

**Purpose**: Manage FAISS vector store creation, persistence, and retrieval.

**Location**: `src/rag/vectorstore_manager.py`

### Key Features
- Gemini embeddings (primary) with HuggingFace fallback
- Configurable embedding dimensions (768, 1536, 3072)
- Automatic persistence to disk
- Similarity search with optional scores

### Class Definition

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class VectorStoreManager:
    def __init__(self, output_dimensionality: int = 768, use_local: bool = False):
        self.use_local = use_local

        if not use_local:
            # Try Gemini embeddings first
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if self.api_key:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-001",
                    google_api_key=self.api_key,
                    task_type="retrieval_document",
                    output_dimensionality=output_dimensionality
                )
            else:
                self._init_local_embeddings()
        else:
            self._init_local_embeddings()

        self.vectorstore: Optional[FAISS] = None
        self.index_path = Path("rag_index")

    def _init_local_embeddings(self):
        """Fallback to local HuggingFace embeddings"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
```

### Key Methods

#### Create VectorStore
```python
def create_vectorstore(self, documents: List[Document], repo_name: str = "default") -> FAISS:
    """Create FAISS vectorstore from documents"""
    self.vectorstore = FAISS.from_documents(
        documents=documents,
        embedding=self.embeddings
    )
    self.save_vectorstore(repo_name)
    return self.vectorstore
```

#### Save/Load
```python
def save_vectorstore(self, repo_name: str = "default"):
    save_path = self.index_path / repo_name
    save_path.mkdir(exist_ok=True)
    self.vectorstore.save_local(str(save_path))

def load_vectorstore(self, repo_name: str = "default") -> Optional[FAISS]:
    load_path = self.index_path / repo_name
    self.vectorstore = FAISS.load_local(
        str(load_path),
        embeddings=self.embeddings,
        allow_dangerous_deserialization=True
    )
    return self.vectorstore
```

#### Search
```python
def search(self, query: str, k: int = 5) -> List[Document]:
    """Search vectorstore"""
    return self.vectorstore.similarity_search(query, k=k)

def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
    """Search with similarity scores"""
    return self.vectorstore.similarity_search_with_score(query, k=k)

def get_retriever(self, search_kwargs: Optional[dict] = None):
    """Get LangChain retriever"""
    if search_kwargs is None:
        search_kwargs = {"k": 5}
    return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
```

### Usage
```python
from src.rag.vectorstore_manager import VectorStoreManager

# Create
manager = VectorStoreManager(output_dimensionality=768)
vectorstore = manager.create_vectorstore(documents, "my-project")

# Load
manager = VectorStoreManager()
vectorstore = manager.load_vectorstore("my-project")

# Search
results = manager.search("REST endpoints", k=5)
```

---

## Component 3: RetrieverTool

**Purpose**: Wrap FAISS vectorstore as a LangChain tool for agents.

**Location**: `src/rag/retriever_tool.py`

```python
from langchain.tools.retriever import create_retriever_tool

def create_codebase_retriever_tool(
    vectorstore: FAISS,
    search_kwargs: Optional[dict] = None,
    name: str = "search_codebase",
    description: str = None
):
    """Create a retriever tool from FAISS vectorstore"""

    if search_kwargs is None:
        search_kwargs = {"k": 5}

    if description is None:
        description = """Search the Java codebase knowledge graph.

Use this tool to find:
- Classes, interfaces, and enums with their annotations
- Methods and their signatures
- REST API endpoints and their handlers
- Architecture patterns and design choices

Input should be a search query describing what you're looking for.
Examples:
- "Find all controller classes"
- "What REST endpoints exist?"
- "Show classes with @Service annotation"
"""

    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    tool = create_retriever_tool(
        retriever=retriever,
        name=name,
        description=description
    )

    return tool
```

### Usage
```python
from src.rag.retriever_tool import create_codebase_retriever_tool

tool = create_codebase_retriever_tool(
    vectorstore=vectorstore,
    search_kwargs={"k": 10},
    name="search_api",
    description="Search for API endpoints and controllers"
)

# Use in agent
tools = [tool]
```

---

## Component 4: ArchitectureAgent

**Purpose**: ReAct agent for architecture analysis using RAG.

**Location**: `src/rag/agents/architecture_agent.py`

### Class Definition

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

class ArchitectureAgent:
    def __init__(self, vectorstore: FAISS):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0.1
        )

        # Create retriever tool
        self.tools = [
            create_codebase_retriever_tool(
                vectorstore=vectorstore,
                search_kwargs={"k": 10}
            )
        ]

        # System prompt
        self.system_prompt = """You are an expert software architecture analyst...

You have access to the following tools:
{tools}

Use the following format:
Question: the input question
Thought: think about what to do
Action: the action to take, one of [{tool_names}]
Action Input: the input to the action
Observation: the result
... (repeat N times)
Thought: I now know the final answer
Final Answer: the answer

Question: {input}
Thought: {agent_scratchpad}"""

        # Create agent
        prompt = PromptTemplate.from_template(self.system_prompt)

        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )

    def analyze(self, query: str) -> Dict[str, Any]:
        """Analyze architecture based on query"""
        result = self.agent_executor.invoke({"input": query})
        return {
            "success": True,
            "query": query,
            "answer": result.get("output"),
            "intermediate_steps": result.get("intermediate_steps", [])
        }

    def ask(self, question: str) -> str:
        """Simple Q&A interface"""
        result = self.analyze(question)
        return result["answer"] if result["success"] else f"Error: {result['error']}"
```

### Usage
```python
from src.rag.agents.architecture_agent import create_architecture_agent

agent = create_architecture_agent(vectorstore)

# Ask questions
answer = agent.ask("What architecture patterns are used in this codebase?")
print(answer)

# Detailed analysis
result = agent.analyze("List all REST endpoints and their handlers")
print(result["answer"])
```

---

## Latest LangChain/LangGraph Implementation

### Updated Dependencies (2025)

```txt
# requirements.txt
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0
langchain-google-genai>=2.0.0
langgraph>=0.2.0
faiss-cpu>=1.8.0
sentence-transformers>=3.0.0
```

### Modern LangGraph Agent Pattern

```python
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Define tools using decorator
@tool
def search_codebase(query: str) -> str:
    """Search the codebase for classes, methods, and endpoints.

    Args:
        query: The search query describing what to find
    """
    results = vectorstore.similarity_search(query, k=5)
    return "\n\n".join([doc.page_content for doc in results])

# Create agent with LangGraph
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0
)

agent = create_react_agent(
    model=model,
    tools=[search_codebase]
)

# Invoke
response = agent.invoke({
    "messages": [("human", "What REST endpoints exist?")]
})
```

### Modern Retriever with Filtering

```python
from langchain_core.vectorstores import VectorStoreRetriever

# Create retriever with metadata filtering
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 10,
        "filter": {"type": "endpoint"}  # Only search endpoints
    }
)

# Or use MMR for diversity
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 10,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)
```

---

## Adapting for API Modernization

### Enhanced API Document Converter

```python
def _convert_api_endpoints(self) -> List[Document]:
    """Enhanced endpoint conversion for API analysis"""
    for endpoint_id, endpoint in self.kg.endpoints.items():
        content = f"""
API ENDPOINT
============
HTTP Method: {endpoint.http_method}
Path: {endpoint.path}
Handler: {endpoint.handler_class}.{endpoint.handler_method}
Request Body: {endpoint.request_body_type or 'None'}
Response Type: {endpoint.response_type or 'Unknown'}
Path Parameters: {json.dumps(endpoint.path_params)}
Query Parameters: {json.dumps(endpoint.query_params)}
Consumes: {', '.join(endpoint.consumes) or 'application/json'}
Produces: {', '.join(endpoint.produces) or 'application/json'}
Auth Required: {endpoint.auth_required}
Deprecated: {endpoint.deprecated}
"""

        doc = Document(
            page_content=content,
            metadata={
                "type": "api_endpoint",
                "http_method": endpoint.http_method,
                "path": endpoint.path,
                "handler": f"{endpoint.handler_class}.{endpoint.handler_method}",
                "has_request_body": endpoint.request_body_type is not None,
                "auth_required": endpoint.auth_required,
                "deprecated": endpoint.deprecated,
                "api_version": endpoint.api_version,
                "tags": endpoint.tags
            }
        )
        documents.append(doc)
```

### API Analysis Agent

```python
class APIAnalysisAgent:
    """Agent specialized for API modernization analysis"""

    def __init__(self, vectorstore: FAISS):
        self.tools = [
            self._create_api_search_tool(vectorstore),
            self._create_endpoint_details_tool(vectorstore),
            self._create_deprecation_checker_tool(vectorstore)
        ]

        self.system_prompt = """You are an API modernization expert.
Analyze APIs for:
- REST best practices compliance
- OpenAPI/Swagger compatibility
- Versioning strategies
- Security patterns
- Deprecation status
- Breaking changes
"""
```
