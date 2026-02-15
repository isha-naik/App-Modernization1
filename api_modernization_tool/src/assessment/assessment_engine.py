"""App Modernization - Comprehensive Assessment Engine"""
from typing import Dict, Any, List
from src.knowledge_graph.graph import KnowledgeGraph


class ArchitectureAssessment:
    """Assess application architecture quality"""
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
    
    def assess_architecture(self) -> Dict[str, Any]:
        """Comprehensive architecture assessment"""
        return {
            "modularity_score": self._calculate_modularity(),
            "scalability_score": self._assess_scalability(),
            "maintainability_score": self._assess_maintainability(),
            "testability_score": self._assess_testability(),
            "security_concerns": self._identify_security_concerns(),
            "technical_debt": self._estimate_technical_debt(),
            "overall_score": 0  # Will be calculated
        }
    
    def _calculate_modularity(self) -> float:
        """Assess how modular the code is (0-100)"""
        if not self.kg.classes:
            return 0
        
        # Count packages as indication of modularity
        packages = set()
        for class_node in self.kg.classes.values():
            if class_node.package:
                packages.add(class_node.package)
        
        # More packages = better modularity
        modularity = min(100, (len(packages) / len(self.kg.classes)) * 100)
        return round(modularity, 1)
    
    def _assess_scalability(self) -> float:
        """Assess scalability readiness (0-100)"""
        score = 50  # Base score
        
        # Check for stateless design
        if self._has_dependency_injection():
            score += 15
        
        # Check for async patterns
        if self._has_async_patterns():
            score += 15
        
        # Check for caching
        if self._has_caching():
            score += 10
        
        # Check endpoint count
        if len(self.kg.endpoints) > 10:
            score += 10
        
        return min(100, score)
    
    def _assess_maintainability(self) -> float:
        """Assess code maintainability (0-100)"""
        score = 40  # Base score
        
        # Number of classes
        if len(self.kg.classes) > 20:
            score += 15
        
        # Separation of concerns
        if self._has_separation_of_concerns():
            score += 25
        
        # Clear naming
        if self._has_clear_naming():
            score += 20
        
        return min(100, score)
    
    def _assess_testability(self) -> float:
        """Assess testability (0-100)"""
        score = 30
        
        # Dependency injection = more testable
        if self._has_dependency_injection():
            score += 30
        
        # Interface usage
        if self._has_interfaces():
            score += 20
        
        # Small methods
        if self._has_small_methods():
            score += 20
        
        return min(100, score)
    
    def _identify_security_concerns(self) -> List[str]:
        """Identify potential security issues"""
        concerns = []
        
        if not self._has_authentication():
            concerns.append("⚠️ No authentication patterns detected")
        
        if not self._has_input_validation():
            concerns.append("⚠️ No input validation patterns detected")
        
        if not self._has_error_handling():
            concerns.append("⚠️ Inadequate error handling")
        
        if self._has_sql_patterns():
            concerns.append("⚠️ Potential SQL injection risks")
        
        return concerns if concerns else ["✅ No major security concerns detected"]
    
    def _estimate_technical_debt(self) -> Dict[str, Any]:
        """Estimate technical debt"""
        debt_items = []
        
        if not self._has_logging():
            debt_items.append("Missing comprehensive logging")
        
        if not self._has_error_handling():
            debt_items.append("Insufficient error handling")
        
        if not self._has_documentation():
            debt_items.append("Lack of code documentation")
        
        debt_score = len(debt_items) * 10
        
        return {
            "score": min(100, debt_score),
            "items": debt_items,
            "severity": "High" if debt_score > 50 else "Medium" if debt_score > 25 else "Low"
        }
    
    # Helper methods
    def _has_dependency_injection(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Autowired" in ann or "Inject" in ann for ann in annotations)
    
    def _has_async_patterns(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Async" in ann or "CompletableFuture" in ann for ann in annotations)
    
    def _has_caching(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Cacheable" in ann or "Cache" in ann for ann in annotations)
    
    def _has_separation_of_concerns(self) -> bool:
        annotations = self._get_all_annotations()
        patterns = ["Service", "Controller", "Repository", "Component"]
        return sum(1 for ann in annotations if any(p in ann for p in patterns)) > 3
    
    def _has_clear_naming(self) -> bool:
        # Check if methods have descriptive names
        method_names = [m.name for m in self.kg.methods.values()]
        good_names = sum(1 for name in method_names if len(name) > 3)
        return good_names / len(method_names) > 0.7 if method_names else False
    
    def _has_interfaces(self) -> bool:
        for method in self.kg.methods.values():
            if "implements" in method.metadata or "interface" in method.metadata:
                return True
        return False
    
    def _has_small_methods(self) -> bool:
        method_sizes = [len(m.metadata.get("lines", "").split("\n")) for m in self.kg.methods.values()]
        avg_size = sum(method_sizes) / len(method_sizes) if method_sizes else 0
        return avg_size < 30
    
    def _has_authentication(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Auth" in ann or "Security" in ann for ann in annotations)
    
    def _has_input_validation(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Valid" in ann or "RequestBody" in ann for ann in annotations)
    
    def _has_error_handling(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Exception" in ann or "ExceptionHandler" in ann for ann in annotations)
    
    def _has_sql_patterns(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Query" in ann or "SQL" in ann for ann in annotations)
    
    def _has_logging(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Log" in ann for ann in annotations)
    
    def _has_documentation(self) -> bool:
        # Check for JavaDoc style comments
        for method in self.kg.methods.values():
            if "/**" in method.metadata.get("comment", ""):
                return True
        return False
    
    def _get_all_annotations(self) -> List[str]:
        annotations = []
        for class_node in self.kg.classes.values():
            annotations.extend(class_node.annotations)
        for method_node in self.kg.methods.values():
            annotations.extend(method_node.annotations)
        return annotations
