# Expert RAG & Migration Module Documentation

## Overview

The Migration module provides AI-powered migration planning using a dual-RAG architecture:
1. **Code RAG** - Vectorized codebase for understanding existing structure
2. **Expert RAG** - Vectorized migration knowledge, best practices, and skill documents

---

## Component 1: ExpertRAGManager

**Purpose**: Index and query migration expertise documents (skills, framework guides, best practices).

**Location**: `src/migration/expert_rag_manager.py`

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Expert RAG System                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────┐   ┌──────────────────────┐   │
│  │ migration_knowledge/ │   │ migration_knowledge/ │   │
│  │ skills/              │   │ frameworks/          │   │
│  │ ├── controller.md    │   │ ├── spring_boot_3.md │   │
│  │ ├── service.md       │   │ ├── quarkus.md       │   │
│  │ ├── entity.md        │   │ └── jakarta_ee.md    │   │
│  │ └── config.md        │   │                      │   │
│  └──────────────────────┘   └──────────────────────┘   │
│              │                       │                   │
│              └───────────┬───────────┘                   │
│                          ▼                               │
│              ┌──────────────────────┐                   │
│              │ Text Splitter        │                   │
│              │ (Recursive, 2000     │                   │
│              │  chars, 200 overlap) │                   │
│              └──────────────────────┘                   │
│                          │                               │
│                          ▼                               │
│              ┌──────────────────────┐                   │
│              │ Embeddings           │                   │
│              │ (Gemini/HuggingFace) │                   │
│              └──────────────────────┘                   │
│                          │                               │
│                          ▼                               │
│              ┌──────────────────────┐                   │
│              │ FAISS VectorStore    │                   │
│              │ rag_index/           │                   │
│              │ migration_expert/    │                   │
│              └──────────────────────┘                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Class Definition

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ExpertRAGManager:
    def __init__(self, output_dimensionality: int = 768, use_local: bool = False):
        # Paths
        self.index_path = Path("rag_index/migration_expert")
        self.knowledge_base_path = Path("migration_knowledge")
        self.skills_path = self.knowledge_base_path / "skills"
        self.frameworks_path = self.knowledge_base_path / "frameworks"

        # Initialize embeddings (same pattern as VectorStoreManager)
        if not use_local and self.api_key:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                task_type="retrieval_document",
                output_dimensionality=output_dimensionality
            )
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "]
        )

        self.vectorstore: Optional[FAISS] = None
```

### Indexing Knowledge Base

```python
def index_knowledge_base(self, force_reindex: bool = False) -> bool:
    """Index all skill documents and framework guides"""

    # Check if already indexed
    if not force_reindex and self.load():
        return True

    documents = []

    # Index skill documents
    if self.skills_path.exists():
        for skill_file in self.skills_path.glob("*.md"):
            docs = self._process_skill_document(skill_file)
            documents.extend(docs)

    # Index framework guides
    if self.frameworks_path.exists():
        for framework_file in self.frameworks_path.glob("*.md"):
            docs = self._process_framework_document(framework_file)
            documents.extend(docs)

    # Create vectorstore
    self.vectorstore = FAISS.from_documents(documents, self.embeddings)
    self.save()

    return True

def _process_skill_document(self, file_path: Path) -> List[Document]:
    """Process skill document with metadata"""
    content = file_path.read_text(encoding='utf-8')
    skill_type = file_path.stem.replace("_migration", "").title()

    chunks = self.text_splitter.split_text(content)

    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": str(file_path),
                "document_type": "skill",
                "skill_type": skill_type,
                "section": self._extract_section(chunk),
                "chunk_index": i
            }
        )
        documents.append(doc)

    return documents
```

### Querying Expert Knowledge

```python
def query_migration_knowledge(
    self,
    query: str,
    k: int = 5,
    skill_type: Optional[str] = None,
    document_type: Optional[str] = None
) -> List[Document]:
    """Query for migration knowledge with optional filters"""

    if not self.vectorstore:
        self.load()

    # Get more results for filtering
    results = self.vectorstore.similarity_search(query, k=k * 3)

    # Apply filters
    filtered = []
    for doc in results:
        if skill_type and doc.metadata.get('skill_type', '').lower() != skill_type.lower():
            continue
        if document_type and doc.metadata.get('document_type') != document_type:
            continue
        filtered.append(doc)

    return filtered[:k]

def get_skill_document(self, skill_type: str) -> Optional[str]:
    """Get the full skill document content"""
    skill_file = self.skills_path / f"{skill_type.lower()}_migration.md"
    if skill_file.exists():
        return skill_file.read_text(encoding='utf-8')
    return None

def get_relevant_patterns(
    self,
    source_framework: str,
    target_framework: str,
    component_type: str
) -> List[Document]:
    """Get migration patterns for a specific scenario"""
    query = f"migrate {source_framework} {component_type} to {target_framework}"
    return self.query_migration_knowledge(query, k=5, skill_type=component_type)
```

### Usage
```python
from src.migration.expert_rag_manager import ExpertRAGManager, ensure_expert_rag_indexed

# Ensure indexed and get manager
expert_rag = ensure_expert_rag_indexed()

# Query for controller migration knowledge
docs = expert_rag.query_migration_knowledge(
    query="migrate Struts Action to Spring Controller",
    k=5,
    skill_type="Controller"
)

# Get full skill document
controller_guide = expert_rag.get_skill_document("controller")
```

---

## Component 2: AIMigrationEngine

**Purpose**: Generate AI-powered migration plans using Expert RAG and LLM.

**Location**: `src/migration/ai_mapping_engine.py`

### Class Definition

```python
import google.generativeai as genai

class AIMigrationEngine:
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Initialize Expert RAG
        self.expert_rag = ensure_expert_rag_indexed()
```

### Main Generation Method

```python
def generate_ai_migration_plan(
    self,
    project_name: str,
    source_framework: str,
    target_framework: str,
    target_version: str,
    target_architecture: str,
    discovery_data: Dict[str, Any],
    strategy: Dict[str, Any],
    migration_approach: str = "Minimal Changes"
) -> Dict[str, Any]:
    """Generate comprehensive AI-powered migration plan"""

    # Extract components from discovery data
    components = self._extract_components(discovery_data)

    migration_sections = {}

    # Generate plans for each component type
    controllers = [c for c in components if c['type'] == 'Controller']
    if controllers:
        migration_sections['controllers'] = self._generate_component_migration(
            controllers, 'controller', source_framework, target_framework, strategy
        )

    services = [c for c in components if c['type'] == 'Service']
    if services:
        migration_sections['services'] = self._generate_component_migration(
            services, 'service', source_framework, target_framework, strategy
        )

    # ... similar for repositories, entities

    # Generate architecture design
    architecture_design = self._generate_architecture_design(
        components, target_framework, target_architecture, migration_approach, strategy
    )

    # Generate summary
    summary = self._generate_migration_summary(
        migration_sections, source_framework, target_framework, target_architecture
    )

    return {
        "project_name": project_name,
        "source_framework": source_framework,
        "target_framework": target_framework,
        "summary": summary,
        "architecture_design": architecture_design,
        "sections": migration_sections
    }
```

### Component Migration Generation

```python
def _generate_component_migration(
    self,
    components: List[Dict],
    component_type: str,
    source_framework: str,
    target_framework: str,
    strategy: Dict
) -> Dict[str, Any]:
    """Generate migration plan for a component type"""

    # Query Expert RAG
    query = f"migrate {source_framework} {component_type} to {target_framework}"
    expert_docs = self.expert_rag.query_migration_knowledge(
        query=query,
        k=5,
        skill_type=component_type.title()
    )

    # Get full skill document
    skill_content = self.expert_rag.get_skill_document(component_type)

    # Build context
    context = self._build_ai_context(
        components, expert_docs, skill_content,
        source_framework, target_framework, strategy
    )

    # Call AI
    return self._call_ai_for_migration(context, component_type)

def _build_ai_context(self, components, expert_docs, skill_content,
                      source_framework, target_framework, strategy) -> str:
    """Build context string for AI prompt"""

    context_parts = []

    # Framework context
    context_parts.append(f"""
## Migration Context
- Source Framework: {source_framework}
- Target Framework: {target_framework}
- Principles: {', '.join(strategy.get('principles', []))}
""")

    # Component details
    context_parts.append("\n## Components to Migrate")
    for comp in components[:20]:
        context_parts.append(f"""
### {comp['name']}
- File: {comp.get('file', 'N/A')}
- Annotations: {', '.join(comp.get('annotations', []))}
""")

    # Expert knowledge
    if expert_docs:
        context_parts.append("\n## Expert Migration Knowledge")
        for doc in expert_docs[:3]:
            context_parts.append(f"\n{doc.page_content[:2000]}")

    return '\n'.join(context_parts)
```

### AI Call with JSON Output

```python
def _call_ai_for_migration(self, context: str, component_type: str) -> Dict[str, Any]:
    """Call Gemini to generate migration plan"""

    prompt = f"""{context}

Generate a migration plan for {component_type} components in JSON format:
{{
    "overview": "Brief overview of migration approach",
    "steps": [
        {{
            "step_number": 1,
            "title": "Step title",
            "description": "Detailed description",
            "code_example": "Before and after code",
            "effort": "Low/Medium/High",
            "risk": "Low/Medium/High"
        }}
    ],
    "annotation_changes": [
        {{"from": "old", "to": "new", "notes": "..."}}
    ],
    "code_patterns": [
        {{"pattern_name": "...", "before": "...", "after": "...", "explanation": "..."}}
    ],
    "common_issues": ["Issue 1", "Issue 2"],
    "testing_recommendations": ["Test 1", "Test 2"],
    "estimated_effort": "Total effort",
    "risk_assessment": "Overall risk"
}}

Return ONLY valid JSON."""

    response = self.model.generate_content(prompt)
    response_text = response.text.strip()

    # Clean up response
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]

    return json.loads(response_text)
```

### Architecture Design Generation

```python
def _generate_architecture_design(
    self,
    components: List[Dict],
    target_framework: str,
    target_architecture: str,
    migration_approach: str,
    strategy: Dict
) -> Dict[str, Any]:
    """Generate target architecture design"""

    # Query Expert RAG for architecture knowledge
    expert_docs = self.expert_rag.query_migration_knowledge(
        query=f"{target_architecture} architecture design {target_framework}",
        k=5
    )

    prompt = f"""Design target architecture for {target_framework}.

Target Architecture: {target_architecture}
Migration Approach: {migration_approach}

Components:
- Controllers: {len([c for c in components if c['type'] == 'Controller'])}
- Services: {len([c for c in components if c['type'] == 'Service'])}
- Repositories: {len([c for c in components if c['type'] == 'Repository'])}

Generate JSON:
{{
    "architecture_overview": "Description",
    "architecture_diagram": "ASCII diagram",
    "package_structure": {{
        "base_package": "com.company.project",
        "packages": [
            {{"name": "controller", "description": "...", "classes": [...]}}
        ]
    }},
    "api_design": {{
        "base_path": "/api/v1",
        "endpoints": [...]
    }},
    "migration_phases": [
        {{"phase": 1, "name": "Setup", "description": "...", "deliverables": [...]}}
    ]
}}

Return ONLY valid JSON."""

    response = self.model.generate_content(prompt)
    return json.loads(response.text.strip())
```

### Usage
```python
from src.migration.ai_mapping_engine import AIMigrationEngine

engine = AIMigrationEngine()

plan = engine.generate_ai_migration_plan(
    project_name="my-app",
    source_framework="Struts",
    target_framework="Spring Boot 3",
    target_version="3.2.0",
    target_architecture="Monolith",
    discovery_data=discovery_json,
    strategy={"principles": ["Minimal changes"], "constraints": []},
    migration_approach="Modernize"
)

print(plan['summary']['executive_summary'])
print(plan['sections']['controllers']['steps'])
```

---

## Knowledge Base Structure

### Skill Documents

Location: `migration_knowledge/skills/`

```
skills/
├── controller_migration.md    # Controller/Action migration patterns
├── service_migration.md       # Service layer migration
├── entity_migration.md        # JPA entity migration
├── repository_migration.md    # Data access migration
├── config_migration.md        # Configuration migration
└── architecture_design.md     # Architecture patterns
```

**Example: controller_migration.md**
```markdown
# Controller Migration Guide

## Struts to Spring Boot

### Action to Controller Mapping

**Before (Struts):**
```java
@Action(value = "users", results = {
    @Result(name = "success", location = "/users.jsp")
})
public class UserAction extends ActionSupport {
    public String execute() {
        // ...
    }
}
```

**After (Spring Boot):**
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping
    public ResponseEntity<List<User>> getUsers() {
        // ...
    }
}
```

### Common Patterns
- ActionSupport.execute() → @GetMapping method
- ActionContext → @Autowired services
- ValueStack → ResponseEntity
```

---

## Latest LangChain/LangGraph Implementation

### Modern RAG with LangChain 0.3+

```python
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

class ModernExpertRAG:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",  # Latest model
            task_type="retrieval_document"
        )

        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000,
            chunk_overlap=100
        )

    def create_retriever(self, search_type: str = "mmr") -> VectorStoreRetriever:
        """Create modern retriever with MMR for diversity"""
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={
                "k": 5,
                "fetch_k": 20,
                "lambda_mult": 0.7  # Balance relevance/diversity
            }
        )
```

### LangGraph Migration Agent

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

@tool
def search_migration_knowledge(query: str, skill_type: str = None) -> str:
    """Search expert knowledge base for migration patterns.

    Args:
        query: What to search for
        skill_type: Optional filter (Controller, Service, Entity, etc.)
    """
    docs = expert_rag.query_migration_knowledge(query, k=5, skill_type=skill_type)
    return "\n\n".join([d.page_content for d in docs])

@tool
def get_migration_guide(component_type: str) -> str:
    """Get full migration guide for a component type.

    Args:
        component_type: controller, service, entity, or config
    """
    return expert_rag.get_skill_document(component_type) or "Guide not found"

# Create stateful agent
memory = MemorySaver()

migration_agent = create_react_agent(
    model=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
    tools=[search_migration_knowledge, get_migration_guide],
    checkpointer=memory
)

# Invoke with thread for conversation history
config = {"configurable": {"thread_id": "migration-session-1"}}

response = migration_agent.invoke(
    {"messages": [("human", "How do I migrate Struts Actions to Spring Controllers?")]},
    config
)
```

---

## Adapting for API Modernization

### API Modernization Knowledge Base

```
api_modernization_knowledge/
├── skills/
│   ├── openapi_generation.md      # Generate OpenAPI specs
│   ├── versioning_strategies.md   # API versioning patterns
│   ├── rest_best_practices.md     # REST maturity, naming
│   ├── error_handling.md          # Standard error responses
│   ├── authentication.md          # OAuth2, JWT patterns
│   └── pagination.md              # Pagination patterns
├── standards/
│   ├── openapi_3.1.md             # OpenAPI 3.1 spec
│   ├── json_api.md                # JSON:API standard
│   └── problem_details.md         # RFC 7807 errors
└── migrations/
    ├── soap_to_rest.md            # SOAP → REST
    ├── rest_to_graphql.md         # REST → GraphQL
    └── monolith_to_microservices.md
```

### API Modernization Agent

```python
class APIModernizationEngine:
    """AI-powered API modernization planning"""

    def __init__(self):
        self.expert_rag = APIExpertRAGManager()
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_modernization_plan(
        self,
        api_discovery: Dict,
        target_standard: str = "OpenAPI 3.1",
        goals: List[str] = None
    ) -> Dict:
        """Generate API modernization plan"""

        # Query expert knowledge
        openapi_docs = self.expert_rag.query("OpenAPI 3.1 best practices", k=5)
        versioning_docs = self.expert_rag.query("API versioning strategies", k=3)

        prompt = self._build_modernization_prompt(
            api_discovery, openapi_docs, versioning_docs, goals
        )

        # Generate plan
        return self._generate_plan(prompt)
```

---

## Dependencies

```txt
# requirements.txt
langchain>=0.3.0
langchain-community>=0.3.0
langchain-google-genai>=2.0.0
langgraph>=0.2.0
faiss-cpu>=1.8.0
google-generativeai>=0.8.0
```
