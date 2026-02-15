"""Knowledge Graph - NetworkX-based code structure representation"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any
import networkx as nx
import json


class NodeType(Enum):
    """Node types in the knowledge graph"""
    CLASS = "class"
    METHOD = "method"
    FIELD = "field"
    ENDPOINT = "endpoint"
    ANNOTATION = "annotation"
    INTERFACE = "interface"
    ENUM = "enum"


class EdgeType(Enum):
    """Edge types in the knowledge graph"""
    CALLS = "calls"
    DEPENDS_ON = "depends_on"
    ACCESSES = "accesses"
    DECLARES = "declares"
    HANDLES = "handles"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    ANNOTATED_WITH = "annotated_with"
    RETURNS = "returns"
    PARAMETER = "parameter"


@dataclass
class ClassNode:
    """Represents a Java class"""
    name: str
    package: str
    file_path: str
    java_type: str = "class"  # class, interface, enum
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    superclass: Optional[str] = None
    is_abstract: bool = False


@dataclass
class MethodNode:
    """Represents a Java method"""
    name: str
    class_name: str
    signature: str
    return_type: str
    parameters: List[Dict[str, str]] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    body: Optional[str] = None
    line_start: int = 0
    line_end: int = 0


@dataclass
class FieldNode:
    """Represents a Java field"""
    name: str
    class_name: str
    field_type: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    initial_value: Optional[str] = None


@dataclass
class EndpointNode:
    """Represents a REST API endpoint"""
    http_method: str
    path: str
    handler_method: str
    handler_class: str
    params: List[Dict] = field(default_factory=list)
    consumes: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)


class KnowledgeGraph:
    """NetworkX-based knowledge graph for code structure"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.classes: Dict[str, ClassNode] = {}
        self.methods: Dict[str, MethodNode] = {}
        self.fields: Dict[str, FieldNode] = {}
        self.endpoints: Dict[str, EndpointNode] = {}
        self.entry_points: Set[str] = set()
        self.method_call_map: Dict[str, List[str]] = {}
    
    def add_class(self, class_node: ClassNode) -> str:
        """Add a class node"""
        node_id = f"class:{class_node.package}.{class_node.name}"
        self.classes[node_id] = class_node
        self.graph.add_node(
            node_id,
            type=NodeType.CLASS,
            data=class_node
        )
        return node_id
    
    def add_method(self, method_node: MethodNode) -> str:
        """Add a method node"""
        node_id = f"method:{method_node.class_name}.{method_node.name}"
        self.methods[node_id] = method_node
        self.graph.add_node(
            node_id,
            type=NodeType.METHOD,
            data=method_node
        )
        
        # Link to class
        class_id = f"class:{method_node.class_name}"
        if class_id in self.classes:
            self.graph.add_edge(class_id, node_id, type=EdgeType.DECLARES)
        
        if method_node.class_name not in self.method_call_map:
            self.method_call_map[method_node.class_name] = []
        
        return node_id
    
    def add_field(self, field_node: FieldNode) -> str:
        """Add a field node"""
        node_id = f"field:{field_node.class_name}.{field_node.name}"
        self.fields[node_id] = field_node
        self.graph.add_node(
            node_id,
            type=NodeType.FIELD,
            data=field_node
        )
        
        # Link to class
        class_id = f"class:{field_node.class_name}"
        if class_id in self.classes:
            self.graph.add_edge(class_id, node_id, type=EdgeType.DECLARES)
        
        return node_id
    
    def add_endpoint(self, endpoint_node: EndpointNode) -> str:
        """Add an endpoint node"""
        node_id = f"endpoint:{endpoint_node.http_method}:{endpoint_node.path}"
        self.endpoints[node_id] = endpoint_node
        self.graph.add_node(
            node_id,
            type=NodeType.ENDPOINT,
            data=endpoint_node
        )
        self.entry_points.add(node_id)
        
        # Link to handler
        handler_id = f"method:{endpoint_node.handler_class}.{endpoint_node.handler_method}"
        if handler_id in self.methods:
            self.graph.add_edge(node_id, handler_id, type=EdgeType.HANDLES)
        
        return node_id
    
    def add_method_call(self, caller_class: str, caller_method: str,
                       callee_class: str, callee_method: str):
        """Record a method call"""
        caller_id = f"method:{caller_class}.{caller_method}"
        callee_id = f"method:{callee_class}.{callee_method}"
        
        if caller_id in self.methods and callee_id in self.methods:
            self.graph.add_edge(caller_id, callee_id, type=EdgeType.CALLS)
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the graph"""
        return {
            "classes": len(self.classes),
            "methods": len(self.methods),
            "fields": len(self.fields),
            "endpoints": len(self.endpoints),
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges()
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary"""
        return {
            "classes": {k: v.__dict__ for k, v in self.classes.items()},
            "methods": {k: v.__dict__ for k, v in self.methods.items()},
            "fields": {k: v.__dict__ for k, v in self.fields.items()},
            "endpoints": {k: v.__dict__ for k, v in self.endpoints.items()},
            "stats": self.get_stats()
        }
