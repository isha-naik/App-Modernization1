"""Inference - API and framework detection"""
import json
from typing import Dict, Any, List, Optional
from collections import Counter
from src.knowledge_graph.graph import KnowledgeGraph


class GraphSummarizer:
    """Create compact summaries of knowledge graph for LLM analysis"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
    
    def create_api_signature(self) -> Dict[str, Any]:
        """Create API signature for analysis"""
        return {
            "total_classes": len(self.kg.classes),
            "total_methods": len(self.kg.methods),
            "total_endpoints": len(self.kg.endpoints),
            "annotation_counts": self._count_annotations(),
            "http_methods": self._analyze_http_methods(),
            "endpoints": self._get_endpoint_summary(),
            "java_types": self._analyze_java_types(),
            "packages": self._analyze_packages()
        }
    
    def _count_annotations(self) -> Dict[str, int]:
        """Count all annotations"""
        counter = Counter()
        
        for class_node in self.kg.classes.values():
            for ann in class_node.annotations:
                counter[ann] += 1
        
        for method_node in self.kg.methods.values():
            for ann in method_node.annotations:
                counter[ann] += 1
        
        return dict(counter.most_common(20))
    
    def _analyze_http_methods(self) -> Dict[str, int]:
        """Analyze HTTP methods usage"""
        counter = Counter()
        for endpoint in self.kg.endpoints.values():
            counter[endpoint.http_method] += 1
        return dict(counter)
    
    def _get_endpoint_summary(self) -> List[Dict[str, str]]:
        """Get sample endpoints"""
        endpoints = []
        for endpoint in list(self.kg.endpoints.values())[:10]:
            endpoints.append({
                "method": endpoint.http_method,
                "path": endpoint.path,
                "handler": f"{endpoint.handler_class}.{endpoint.handler_method}"
            })
        return endpoints
    
    def _analyze_java_types(self) -> Dict[str, int]:
        """Analyze Java class types"""
        counter = Counter()
        for class_node in self.kg.classes.values():
            counter[class_node.java_type] += 1
        return dict(counter)
    
    def _analyze_packages(self) -> List[str]:
        """Get top level packages"""
        packages = set()
        for class_node in self.kg.classes.values():
            if class_node.package:
                top_level = class_node.package.split('.')[0]
                packages.add(top_level)
        return sorted(list(packages))


class APIStyleDetector:
    """Detect API style and REST maturity"""
    
    def __init__(self):
        self.patterns = {
            "REST": ["RequestMapping", "GetMapping", "PostMapping", "RestController"],
            "SOAP": ["WebService", "WebMethod"],
            "GraphQL": ["GraphQLQuery", "GraphQLMutation"],
            "RPC": ["JsonRpc", "Rpc"]
        }
    
    def detect_style(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """Detect API style from knowledge graph"""
        style_scores = {}
        
        # Collect all annotations
        all_annotations = []
        for class_node in kg.classes.values():
            all_annotations.extend(class_node.annotations)
        for method_node in kg.methods.values():
            all_annotations.extend(method_node.annotations)
        
        # Score each style
        for style, keywords in self.patterns.items():
            score = sum(1 for ann in all_annotations if any(k in ann for k in keywords))
            style_scores[style] = score
        
        primary_style = max(style_scores, key=style_scores.get)
        
        return {
            "primary_style": primary_style,
            "scores": style_scores,
            "endpoint_count": len(kg.endpoints),
            "has_rest_endpoints": len(kg.endpoints) > 0
        }
    
    def analyze_rest_maturity(self, kg: KnowledgeGraph) -> Dict[str, Any]:
        """Analyze REST maturity using Richardson Model"""
        # Level 0: POX (Plain Old XML)
        # Level 1: Resources
        # Level 2: HTTP Verbs
        # Level 3: HATEOAS
        
        if not kg.endpoints:
            return {
                "level": 0, 
                "description": "No REST endpoints found",
                "http_methods": [],
                "endpoint_count": 0,
                "recommendations": self._get_recommendations(0)
            }
        
        endpoints = kg.endpoints
        
        # Check for HTTP methods diversity
        methods = set(ep.http_method for ep in endpoints.values())
        has_methods = len(methods) > 1
        
        # Check for resource-based paths (ideally should follow pattern)
        paths = [ep.path for ep in endpoints.values()]
        has_resources = any('/' in p for p in paths)
        
        # Determine maturity level
        level = 0
        if has_resources:
            level = 1
        if has_methods:
            level = 2
        
        return {
            "level": level,
            "max_level": 3,
            "description": self._get_maturity_description(level),
            "http_methods": list(methods),
            "endpoint_count": len(endpoints),
            "recommendations": self._get_recommendations(level)
        }
    
    def _get_maturity_description(self, level: int) -> str:
        """Get description for maturity level"""
        descriptions = {
            0: "No REST endpoints - uses legacy/SOAP patterns",
            1: "Resource-based APIs - basic REST structure",
            2: "HTTP Verbs used - proper REST implementation",
            3: "HATEOAS implemented - fully mature REST API"
        }
        return descriptions.get(level, "Unknown")
    
    def _get_recommendations(self, level: int) -> List[str]:
        """Get recommendations based on maturity level"""
        if level == 0:
            return [
                "Migrate to REST architecture",
                "Create resource-based endpoints",
                "Use standard HTTP methods"
            ]
        elif level == 1:
            return [
                "Implement proper HTTP method verbs (GET, POST, PUT, DELETE)",
                "Add versioning to API paths",
                "Standardize error responses"
            ]
        elif level == 2:
            return [
                "Implement HATEOAS for discoverability",
                "Add comprehensive API documentation",
                "Consider API versioning strategy"
            ]
        else:
            return [
                "Maintain comprehensive API documentation",
                "Monitor API versioning strategy",
                "Consider adding caching strategies"
            ]
