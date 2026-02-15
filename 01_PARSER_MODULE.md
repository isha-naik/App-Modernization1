# Parser Module Documentation

## Overview

The Parser module provides framework-agnostic Java code parsing using tree-sitter. It extracts all code elements (classes, methods, fields, annotations) without making assumptions about which framework is used.

## Key Design Principles

1. **Framework-Agnostic**: Extracts ALL annotations without filtering for specific frameworks
2. **No Classification**: Doesn't classify class types (Controller/Service/etc.) during parsing
3. **Raw Data First**: Stores raw data, lets inference engine classify later
4. **Tree-sitter Based**: Uses compiled language parser for reliable, fast parsing

## Core Components

### GenericJavaParser

**Purpose**: Parse Java files and extract all code elements

**Location**: `src/parser/generic_java_parser.py`

```python
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava

class GenericJavaParser:
    def __init__(self):
        self.language = Language(tsjava.language(), 'java')
        self.parser = Parser()
        self.parser.set_language(self.language)
```

### Key Methods

#### 1. `parse_file(file_path: str) -> Optional[bytes]`
Reads a Java file and returns its content as bytes.

#### 2. `get_package_name(tree: Node, source_code: bytes) -> str`
Extracts the package declaration from the AST.

```python
def get_package_name(self, tree: Node, source_code: bytes) -> str:
    query = self.language.query("(package_declaration (scoped_identifier) @package)")
    captures = query.captures(tree)
    for node, _ in captures:
        return self.extract_text(node, source_code)
    return ""
```

#### 3. `get_all_annotations(node: Node, source_code: bytes) -> List[Dict[str, Any]]`
Extracts ALL annotations from a node without filtering.

**Returns**:
```python
{
    'name': 'RequestMapping',      # Annotation name
    'values': {'value': '/api'},   # Annotation parameters
    'raw': '@RequestMapping("/api")' # Full annotation text
}
```

#### 4. `extract_classes(tree, source_code, package, file_path) -> List[Dict]`
Extracts all classes, interfaces, and enums.

**Returns**:
```python
{
    'name': 'UserController',
    'package': 'com.example.controller',
    'file_path': '/path/to/file.java',
    'java_type': 'class',  # or 'interface', 'enum'
    'annotations': [{'name': 'RestController', 'values': {}, 'raw': '@RestController'}],
    'modifiers': ['public'],
    'interfaces': ['Serializable'],
    'superclass': 'BaseController',
    'is_abstract': False,
    'node': <tree_sitter.Node>  # Keep for method/field extraction
}
```

#### 5. `extract_methods(class_node, source_code, class_name) -> List[Dict]`
Extracts all methods from a class.

**Returns**:
```python
{
    'name': 'getUsers',
    'class_name': 'com.example.UserController',
    'signature': 'getUsers()',
    'return_type': 'List<User>',
    'parameters': [{'type': 'Long', 'name': 'id', 'annotations': [...]}],
    'modifiers': ['public'],
    'annotations': [{'name': 'GetMapping', 'values': {'value': '/users'}}],
    'body': '{ return userService.findAll(); }',
    'line_start': 25,
    'line_end': 28
}
```

#### 6. `extract_fields(class_node, source_code, class_name) -> List[Dict]`
Extracts all fields from a class.

#### 7. `parse_java_file(file_path, knowledge_graph)`
Main method to parse a file and populate the knowledge graph.

#### 8. `parse_directory(directory_path, knowledge_graph)`
Parse all Java files in a directory recursively.

---

### RelationshipExtractor

**Purpose**: Extracts relationships between code elements

**Location**: `src/parser/relationship_extractor.py`

```python
class RelationshipExtractor:
    def __init__(self, parser):
        self.parser = parser
        self.language = parser.language
```

### Key Methods

#### 1. `extract_method_calls(method_body, method_full_name, source_code, knowledge_graph)`
Identifies all method calls within a method body.

```python
query = self.language.query("""
    (method_invocation
        name: (identifier) @method_name
    ) @call
""")
```

#### 2. `extract_field_accesses(method_body, method_full_name, class_name, source_code, knowledge_graph)`
Identifies field read/write operations.

#### 3. `extract_endpoints(method_node, class_name, knowledge_graph)`
Extracts REST endpoint information from controller methods.

```python
endpoint_annotations = {
    'GetMapping': 'GET',
    'PostMapping': 'POST',
    'PutMapping': 'PUT',
    'DeleteMapping': 'DELETE',
    'PatchMapping': 'PATCH',
    'RequestMapping': 'REQUEST'
}
```

#### 4. `extract_all_relationships(knowledge_graph)`
Main method that processes all methods in the knowledge graph.

---

## Usage Example

```python
from src.knowledge_graph.graph import KnowledgeGraph
from src.parser.generic_java_parser import GenericJavaParser
from src.parser.relationship_extractor import RelationshipExtractor

# Initialize
knowledge_graph = KnowledgeGraph()
parser = GenericJavaParser()

# Parse directory
parser.parse_directory("/path/to/java/project", knowledge_graph)

# Extract relationships
extractor = RelationshipExtractor(parser)
extractor.extract_all_relationships(knowledge_graph)

# Get stats
stats = knowledge_graph.get_stats()
print(f"Classes: {stats['classes']}, Methods: {stats['methods']}")
```

---

## Adapting for API Modernization

### What to Keep
- Tree-sitter based parsing (fast, reliable)
- Annotation extraction (critical for API discovery)
- Method signature extraction
- Parameter extraction with annotations

### What to Extend

1. **Enhanced Endpoint Extraction**:
```python
# Add support for more API annotations
api_annotations = {
    # JAX-RS
    'Path': 'PATH',
    'GET': 'GET',
    'POST': 'POST',
    'Consumes': 'CONSUMES',
    'Produces': 'PRODUCES',

    # OpenAPI/Swagger
    'ApiOperation': 'OPERATION',
    'ApiResponse': 'RESPONSE',
    'ApiParam': 'PARAM',

    # GraphQL
    'QueryMapping': 'QUERY',
    'MutationMapping': 'MUTATION'
}
```

2. **Request/Response Body Extraction**:
```python
def extract_request_response_types(self, method_node, source_code):
    """Extract @RequestBody and return types for API contract"""
    request_body = None
    response_type = None

    for param in method_node['parameters']:
        if 'RequestBody' in [a['name'] for a in param.get('annotations', [])]:
            request_body = param['type']

    response_type = method_node['return_type']

    return {'request': request_body, 'response': response_type}
```

3. **Path Parameter Extraction**:
```python
def extract_path_params(self, method_node):
    """Extract @PathVariable, @PathParam, @QueryParam"""
    params = []
    for param in method_node['parameters']:
        for ann in param.get('annotations', []):
            if ann['name'] in ['PathVariable', 'PathParam', 'QueryParam', 'RequestParam']:
                params.append({
                    'name': param['name'],
                    'type': param['type'],
                    'source': ann['name'],
                    'required': ann.get('values', {}).get('required', True)
                })
    return params
```

---

## Dependencies (Latest Versions)

```txt
# requirements.txt
tree-sitter>=0.21.0
tree-sitter-java>=0.21.0
```

**Installation**:
```bash
pip install tree-sitter tree-sitter-java
```

---

## Tree-sitter Query Reference

Common queries for Java parsing:

```python
# Class declarations
"(class_declaration name: (identifier) @name) @class"

# Interface declarations
"(interface_declaration name: (identifier) @name) @interface"

# Method declarations
"(method_declaration name: (identifier) @name) @method"

# Field declarations
"(field_declaration) @field"

# Annotations
"(marker_annotation) @annotation"
"(annotation) @annotation"

# Method invocations
"(method_invocation name: (identifier) @method_name) @call"

# Field access
"(field_access field: (identifier) @field_name) @access"
```

---

## Notes for Latest LangChain/LangGraph

The parser module is **independent of LangChain/LangGraph**. It uses tree-sitter directly.

However, the output integrates with LangChain through the `GraphToDocuments` converter which creates `langchain_core.documents.Document` objects.
