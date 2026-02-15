"""Java code parser using tree-sitter"""
import re
from typing import Optional, List, Dict, Any
from pathlib import Path

# Make tree-sitter optional
try:
    from tree_sitter import Language, Parser
    import tree_sitter_java as tsjava
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Language = None
    Parser = None
    tsjava = None

from src.knowledge_graph.graph import (
    KnowledgeGraph, ClassNode, MethodNode, FieldNode, EndpointNode
)


class JavaParserMock:
    """Mock parser for when tree-sitter is not available"""
    
    def __init__(self):
        self.annotations_pattern = r'@(\w+)(?:\([^)]*\))?'
        self.method_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(\w+)\s+(\w+)\s*\((.*?)\)'
        self.field_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(\w+)\s+(\w+)\s*(?:=|;)'
        self.class_pattern = r'(?:public|private)?\s*(?:class|interface|enum)\s+(\w+)'
    
    def parse_file(self, file_path: str) -> Optional[bytes]:
        """Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().encode('utf-8')
        except Exception:
            return None
    
    def extract_annotations(self, content: str) -> List[Dict[str, Any]]:
        """Extract annotations using regex"""
        annotations = []
        for match in re.finditer(self.annotations_pattern, content):
            annotations.append({
                'name': match.group(1),
                'values': {},
                'raw': match.group(0)
            })
        return annotations
    
    def extract_package(self, content: str) -> str:
        """Extract package declaration"""
        match = re.search(r'package\s+([\w.]+)', content)
        return match.group(1) if match else ""
    
    def extract_classes(self, file_path: str, content: str, 
                       package: str) -> List[Dict[str, Any]]:
        """Extract classes from file"""
        classes = []
        
        # Simple regex-based parsing
        for match in re.finditer(
            r'(?:public|private)?\s*(?:class|interface|enum)\s+(\w+)(?:\s+extends\s+(\w+))?',
            content
        ):
            class_name = match.group(1)
            superclass = match.group(2)
            
            classes.append({
                'name': class_name,
                'package': package,
                'file_path': file_path,
                'java_type': 'class',
                'modifiers': ['public'],
                'annotations': self.extract_annotations(content),
                'interfaces': [],
                'superclass': superclass,
                'is_abstract': 'abstract' in content[:match.start()]
            })
        
        return classes
    
    def extract_methods(self, content: str, class_name: str) -> List[Dict[str, Any]]:
        """Extract methods from class"""
        methods = []
        
        for match in re.finditer(self.method_pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)
            
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        parameters.append({
                            'type': parts[0],
                            'name': parts[1],
                            'annotations': []
                        })
            
            methods.append({
                'name': method_name,
                'class_name': class_name,
                'signature': f"{method_name}({params_str})",
                'return_type': return_type,
                'parameters': parameters,
                'modifiers': ['public'],
                'annotations': self.extract_annotations(content),
                'body': None,
                'line_start': 0,
                'line_end': 0
            })
        
        return methods


class GenericJavaParser:
    """Java parser using tree-sitter (or mock fallback)"""
    
    def __init__(self):
        self.use_treeitter = TREE_SITTER_AVAILABLE
        if TREE_SITTER_AVAILABLE:
            self.language = Language(tsjava.language(), 'java')
            self.parser = Parser()
            self.parser.set_language(self.language)
        else:
            self.parser = JavaParserMock()
    
    def parse_directory(self, directory_path: str, knowledge_graph: KnowledgeGraph):
        """Parse all Java files in directory"""
        path = Path(directory_path)
        java_files = list(path.rglob("*.java"))
        
        for java_file in java_files:
            self.parse_java_file(str(java_file), knowledge_graph)
    
    def parse_file(self, file_path: str, knowledge_graph: KnowledgeGraph):
        """Parse a single file (wrapper for compatibility)"""
        self.parse_java_file(file_path, knowledge_graph)
    
    def parse_java_file(self, file_path: str, knowledge_graph: KnowledgeGraph):
        """Parse a single Java file"""
        try:
            content = self.parser.parse_file(file_path)
            if not content:
                return
            
            content_str = content.decode('utf-8') if isinstance(content, bytes) else content
            
            # Extract package
            package = self.parser.extract_package(content_str)
            
            # Extract classes
            classes = self.parser.extract_classes(file_path, content_str, package)
            
            for class_info in classes:
                # Add class to graph
                class_node = ClassNode(
                    name=class_info['name'],
                    package=class_info['package'],
                    file_path=class_info['file_path'],
                    java_type=class_info['java_type'],
                    modifiers=class_info.get('modifiers', []),
                    annotations=[a['name'] for a in class_info.get('annotations', [])],
                    interfaces=class_info.get('interfaces', []),
                    superclass=class_info.get('superclass'),
                    is_abstract=class_info.get('is_abstract', False)
                )
                knowledge_graph.add_class(class_node)
                
                # Extract and add methods
                methods = self.parser.extract_methods(content_str, 
                                                     f"{package}.{class_info['name']}")
                
                for method_info in methods:
                    method_node = MethodNode(
                        name=method_info['name'],
                        class_name=method_info['class_name'],
                        signature=method_info['signature'],
                        return_type=method_info['return_type'],
                        parameters=method_info.get('parameters', []),
                        modifiers=method_info.get('modifiers', []),
                        annotations=[a['name'] for a in method_info.get('annotations', [])],
                        body=method_info.get('body'),
                        line_start=method_info.get('line_start', 0),
                        line_end=method_info.get('line_end', 0)
                    )
                    knowledge_graph.add_method(method_node)
                    
                    # Extract endpoints if REST-related annotations exist
                    self._extract_endpoints(method_node, class_node, knowledge_graph)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    
    def _extract_endpoints(self, method: MethodNode, class_node: ClassNode,
                          kg: KnowledgeGraph):
        """Extract REST endpoints from method annotations"""
        endpoint_annotations = {
            'GetMapping': 'GET',
            'PostMapping': 'POST',
            'PutMapping': 'PUT',
            'DeleteMapping': 'DELETE',
            'PatchMapping': 'PATCH',
            'RequestMapping': 'REQUEST'
        }
        
        for annotation in method.annotations:
            if annotation in endpoint_annotations:
                http_method = endpoint_annotations[annotation]
                path = f"/{class_node.name.lower()}/{method.name}"
                
                endpoint = EndpointNode(
                    http_method=http_method,
                    path=path,
                    handler_method=method.name,
                    handler_class=f"{class_node.package}.{class_node.name}",
                    params=method.parameters,
                    consumes=['application/json'],
                    produces=['application/json']
                )
                kg.add_endpoint(endpoint)
