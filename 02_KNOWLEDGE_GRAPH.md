# Knowledge Graph Module Documentation

## Overview

The Knowledge Graph module provides a NetworkX-based graph structure for storing and querying codebase structure. It serves as the central data structure connecting all analysis components.

## Key Design Principles

1. **NetworkX MultiDiGraph**: Supports multiple edges between nodes (e.g., a method can both CALL and ACCESS)
2. **Typed Nodes**: Classes, Methods, Fields, Endpoints each have their own node type
3. **Typed Edges**: Relationships have explicit types (CALLS, DEPENDS_ON, etc.)
4. **Quick Lookups**: Maintains dictionaries for O(1) access to nodes

## Core Components

### Data Classes

**Location**: `src/knowledge_graph/graph.py`

#### NodeType (Enum)
```python
class NodeType(Enum):
    CLASS = "class"
    METHOD = "method"
    FIELD = "field"
    ENDPOINT = "endpoint"
    ANNOTATION = "annotation"
    INTERFACE = "interface"
    ENUM = "enum"
```

#### EdgeType (Enum)
```python
class EdgeType(Enum):
    CALLS = "calls"           # method -> method
    DEPENDS_ON = "depends_on" # class -> class
    ACCESSES = "accesses"     # method -> field
    DECLARES = "declares"     # class -> method/field
    HANDLES = "handles"       # endpoint -> method
    IMPLEMENTS = "implements" # class -> interface
    EXTENDS = "extends"       # class -> class
    ANNOTATED_WITH = "annotated_with"  # any -> annotation
    RETURNS = "returns"       # method -> type
    PARAMETER = "parameter"   # method -> type
```

---

### Node Data Classes

#### ClassNode
```python
@dataclass
class ClassNode:
    name: str                           # Class name
    package: str                        # Package name
    file_path: str                      # Source file path
    class_type: str                     # Controller, Service, etc. (inferred)
    java_type: str = "class"            # "class", "interface", "enum"
    modifiers: List[str] = []           # public, private, static, etc.
    annotations: List[str] = []         # Annotation names
    interfaces: List[str] = []          # Implemented interfaces
    superclass: Optional[str] = None    # Parent class
    is_abstract: bool = False
```

#### MethodNode
```python
@dataclass
class MethodNode:
    name: str                           # Method name
    class_name: str                     # Fully qualified class name
    signature: str                      # e.g., "getUser(Long)"
    return_type: str                    # Return type
    parameters: List[Dict[str, str]] = []  # [{type, name, annotations}]
    modifiers: List[str] = []
    annotations: List[str] = []
    body: Optional[str] = None          # Method body for analysis
    line_start: int = 0
    line_end: int = 0
```

#### FieldNode
```python
@dataclass
class FieldNode:
    name: str
    class_name: str
    field_type: str
    modifiers: List[str] = []
    annotations: List[str] = []
    initial_value: Optional[str] = None
```

#### EndpointNode
```python
@dataclass
class EndpointNode:
    http_method: str          # GET, POST, PUT, DELETE, PATCH
    path: str                 # /api/users/{id}
    handler_method: str       # Method name that handles this endpoint
    handler_class: str        # Class containing the handler
    params: List[Dict] = []   # Query/Path parameters
    consumes: List[str] = []  # Content types consumed
    produces: List[str] = []  # Content types produced
```

---

### KnowledgeGraph Class

```python
class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.classes: Dict[str, ClassNode] = {}
        self.methods: Dict[str, MethodNode] = {}
        self.fields: Dict[str, FieldNode] = {}
        self.endpoints: Dict[str, EndpointNode] = {}

        # Quick lookup maps
        self.field_access_map: Dict[str, List[str]] = {}  # field -> methods
        self.method_call_map: Dict[str, List[str]] = {}   # method -> called methods
        self.entry_points: Set[str] = set()               # REST endpoints, jobs, etc.
```

### Key Methods

#### Adding Nodes

```python
def add_class(self, class_node: ClassNode) -> str:
    """Add a class node. Returns node_id like 'class:com.example.UserController'"""
    node_id = f"class:{class_node.package}.{class_node.name}"
    self.classes[node_id] = class_node
    self.graph.add_node(node_id, type=NodeType.CLASS, data=class_node)
    return node_id

def add_method(self, method_node: MethodNode) -> str:
    """Add a method node and link to its class"""
    node_id = f"method:{method_node.class_name}.{method_node.name}"
    self.methods[node_id] = method_node
    self.graph.add_node(node_id, type=NodeType.METHOD, data=method_node)

    # Auto-link to class
    class_id = f"class:{method_node.class_name}"
    if class_id in self.classes:
        self.graph.add_edge(class_id, node_id, type=EdgeType.DECLARES)
    return node_id

def add_endpoint(self, endpoint_node: EndpointNode) -> str:
    """Add an endpoint and link to handler method"""
    node_id = f"endpoint:{endpoint_node.http_method}:{endpoint_node.path}"
    self.endpoints[node_id] = endpoint_node
    self.graph.add_node(node_id, type=NodeType.ENDPOINT, data=endpoint_node)
    self.entry_points.add(node_id)

    # Auto-link to handler
    handler_id = f"method:{endpoint_node.handler_class}.{endpoint_node.handler_method}"
    if handler_id in self.methods:
        self.graph.add_edge(node_id, handler_id, type=EdgeType.HANDLES)
    return node_id
```

#### Adding Relationships

```python
def add_method_call(self, caller: str, callee: str):
    """Record a method call relationship"""
    caller_id = f"method:{caller}"
    callee_id = f"method:{callee}"

    if caller_id in self.methods:
        self.graph.add_edge(caller_id, callee_id, type=EdgeType.CALLS)

        if caller not in self.method_call_map:
            self.method_call_map[caller] = []
        self.method_call_map[caller].append(callee)

def add_field_access(self, method: str, field: str, access_type: str = "read"):
    """Record a field access (read or write)"""
    method_id = f"method:{method}"
    field_id = f"field:{field}"

    if method_id in self.methods and field_id in self.fields:
        self.graph.add_edge(
            method_id, field_id,
            type=EdgeType.ACCESSES,
            access_type=access_type
        )
```

#### Querying the Graph

```python
def get_methods_accessing_field(self, field: str, access_type: Optional[str] = None) -> List[str]:
    """Get all methods that access a specific field"""
    field_id = f"field:{field}"
    accessors = []

    for pred in self.graph.predecessors(field_id):
        for edge_key in self.graph[pred][field_id]:
            edge_data = self.graph[pred][field_id][edge_key]
            if edge_data.get('type') == EdgeType.ACCESSES:
                if access_type is None or edge_data.get('access_type') == access_type:
                    accessors.append(pred)
    return accessors

def get_methods_called_by(self, method: str) -> List[str]:
    """Get all methods called by a specific method"""
    method_id = f"method:{method}"
    callees = []

    for succ in self.graph.successors(method_id):
        for edge_key in self.graph[method_id][succ]:
            if self.graph[method_id][succ][edge_key].get('type') == EdgeType.CALLS:
                callees.append(succ)
    return callees
```

#### Graph Traversal

```python
def backtrack_to_entry_points(self, target: str, max_depth: int = 10) -> List[List[str]]:
    """
    Find all paths from entry points to a target node.
    Useful for: "Which API endpoints can trigger this database operation?"
    """
    paths = []
    for entry_point in self.entry_points:
        try:
            all_paths = nx.all_simple_paths(
                self.graph,
                source=entry_point,
                target=target,
                cutoff=max_depth
            )
            paths.extend(list(all_paths))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue
    return paths

def forward_trace(self, entry_point: str, max_depth: int = 10) -> Set[str]:
    """
    Find all nodes reachable from an entry point.
    Useful for: "What code is touched by this API endpoint?"
    """
    if entry_point not in self.graph:
        return set()

    reachable = set()
    visited = {entry_point}
    queue = [(entry_point, 0)]

    while queue:
        node, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        reachable.add(node)

        for successor in self.graph.successors(node):
            if successor not in visited:
                visited.add(successor)
                queue.append((successor, depth + 1))
    return reachable
```

#### Export

```python
def export_to_dict(self) -> Dict[str, Any]:
    """Export the knowledge graph to a dictionary for serialization"""
    return {
        "classes": {k: v.__dict__ for k, v in self.classes.items()},
        "methods": {k: v.__dict__ for k, v in self.methods.items()},
        "fields": {k: v.__dict__ for k, v in self.fields.items()},
        "endpoints": {k: v.__dict__ for k, v in self.endpoints.items()},
        "stats": self.get_stats()
    }

def get_stats(self) -> Dict[str, int]:
    """Get statistics about the knowledge graph"""
    return {
        "total_nodes": self.graph.number_of_nodes(),
        "total_edges": self.graph.number_of_edges(),
        "classes": len(self.classes),
        "methods": len(self.methods),
        "fields": len(self.fields),
        "endpoints": len(self.endpoints),
        "entry_points": len(self.entry_points)
    }
```

---

## Usage Example

```python
from src.knowledge_graph.graph import (
    KnowledgeGraph, ClassNode, MethodNode, EndpointNode
)

# Create graph
kg = KnowledgeGraph()

# Add a class
user_controller = ClassNode(
    name="UserController",
    package="com.example.controller",
    file_path="/src/main/java/com/example/controller/UserController.java",
    class_type="UNCLASSIFIED",
    java_type="class",
    annotations=["RestController", "RequestMapping"],
    modifiers=["public"]
)
kg.add_class(user_controller)

# Add a method
get_user = MethodNode(
    name="getUser",
    class_name="com.example.controller.UserController",
    signature="getUser(Long)",
    return_type="User",
    parameters=[{"type": "Long", "name": "id"}],
    annotations=["GetMapping"]
)
kg.add_method(get_user)

# Add an endpoint
endpoint = EndpointNode(
    http_method="GET",
    path="/api/users/{id}",
    handler_method="getUser",
    handler_class="com.example.controller.UserController"
)
kg.add_endpoint(endpoint)

# Query
print(kg.get_stats())
print(kg.forward_trace("endpoint:GET:/api/users/{id}"))
```

---

## Adapting for API Modernization

### Extended EndpointNode for API Analysis

```python
@dataclass
class APIEndpointNode:
    """Enhanced endpoint node for API modernization"""
    http_method: str
    path: str
    handler_method: str
    handler_class: str

    # API Contract Info
    request_body_type: Optional[str] = None
    response_type: Optional[str] = None
    path_params: List[Dict] = field(default_factory=list)
    query_params: List[Dict] = field(default_factory=list)
    headers: List[Dict] = field(default_factory=list)

    # API Metadata
    consumes: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    deprecated: bool = False
    description: Optional[str] = None

    # Security
    auth_required: bool = False
    roles_allowed: List[str] = field(default_factory=list)

    # Versioning
    api_version: Optional[str] = None

    # OpenAPI annotations
    operation_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
```

### New Edge Types for API Analysis

```python
class APIEdgeType(Enum):
    # Existing
    CALLS = "calls"
    HANDLES = "handles"

    # API-specific
    TRANSFORMS_TO = "transforms_to"     # DTO -> Entity mapping
    VALIDATES = "validates"             # Validation rules
    AUTHENTICATES = "authenticates"     # Auth flow
    RATE_LIMITS = "rate_limits"         # Rate limiting rules
    CACHES = "caches"                   # Caching behavior
    DOCUMENTS = "documents"             # OpenAPI documentation
```

---

## Dependencies

```txt
# requirements.txt
networkx>=3.0
```

**Installation**:
```bash
pip install networkx
```

---

## Notes for Latest LangChain/LangGraph

The Knowledge Graph is **independent of LangChain/LangGraph** - it uses NetworkX directly.

Integration happens through:
1. `GraphToDocuments` - converts graph to LangChain Documents
2. `GraphSummarizer` - creates compact summaries for LLM prompts

The graph structure is framework-agnostic and can be serialized to JSON for persistence.
