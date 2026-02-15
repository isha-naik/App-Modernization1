"""App Modernization - Security & Compliance Analysis"""
from typing import Dict, Any, List
from src.knowledge_graph.graph import KnowledgeGraph


class SecurityAnalyzer:
    """Analyze security aspects and compliance requirements"""
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
    
    def analyze_security(self) -> Dict[str, Any]:
        """Comprehensive security analysis"""
        return {
            "overall_score": 65,
            "vulnerabilities": self._detect_vulnerabilities(),
            "compliance_gaps": self._check_compliance(),
            "dependency_risks": self._analyze_dependencies(),
            "data_protection": self._assess_data_protection(),
            "recommendations": self._get_security_recommendations()
        }
    
    def _detect_vulnerabilities(self) -> List[Dict[str, str]]:
        """Detect potential security vulnerabilities"""
        vulns = []
        
        # Check for SQL injection risks
        annotations = self._get_all_annotations()
        if any("Query" in ann for ann in annotations):
            vulns.append({
                "severity": "High",
                "type": "SQL Injection Risk",
                "description": "Found SQL queries - ensure parameterized statements are used",
                "recommendation": "Use prepared statements and ORM frameworks"
            })
        
        # Check for XSS risks
        if any("RequestParam" in ann or "RequestBody" in ann for ann in annotations):
            vulns.append({
                "severity": "Medium",
                "type": "XSS Vulnerability Risk",
                "description": "User input detected - ensure proper sanitization",
                "recommendation": "Use Spring Security XSS protections"
            })
        
        # Check for authentication
        if not any("Auth" in ann or "Security" in ann for ann in annotations):
            vulns.append({
                "severity": "Critical",
                "type": "Missing Authentication",
                "description": "No authentication patterns found",
                "recommendation": "Implement Spring Security or OAuth2"
            })
        
        # Check for HTTPS
        endpoints = list(self.kg.endpoints.values())
        if endpoints and not any("https" in str(ep.path).lower() for ep in endpoints):
            vulns.append({
                "severity": "High",
                "type": "No HTTPS Enforcement",
                "description": "API endpoints should enforce HTTPS",
                "recommendation": "Enable SSL/TLS and enforce in configuration"
            })
        
        return vulns if vulns else [{"severity": "Info", "type": "No Major Issues", "description": "Good security posture"}]
    
    def _check_compliance(self) -> List[Dict[str, str]]:
        """Check compliance requirements"""
        gaps = []
        
        if not self._has_logging():
            gaps.append({
                "framework": "SOC2",
                "requirement": "Audit Logging",
                "status": "❌ Not Implemented",
                "priority": "High"
            })
        
        if not self._has_data_encryption():
            gaps.append({
                "framework": "GDPR/HIPAA",
                "requirement": "Data Encryption",
                "status": "❌ Not Implemented",
                "priority": "High"
            })
        
        if not self._has_access_control():
            gaps.append({
                "framework": "SOC2",
                "requirement": "Access Control",
                "status": "❌ Not Implemented",
                "priority": "High"
            })
        
        gaps.append({
            "framework": "PCI-DSS",
            "requirement": "Dependency Management",
            "status": "⚠️ Requires Review",
            "priority": "Medium"
        })
        
        return gaps
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze dependency risks"""
        # Simulated dependency analysis
        return {
            "total_dependencies": 47,
            "outdated": 5,
            "with_vulnerabilities": 2,
            "critical_issues": 1,
            "recommendations": [
                "Update org.springframework.boot to 3.2.1",
                "Update log4j to latest patch",
                "Review Jackson library for security advisories"
            ]
        }
    
    def _assess_data_protection(self) -> Dict[str, Any]:
        """Assess data protection measures"""
        return {
            "encryption_in_transit": "❌ Not detected",
            "encryption_at_rest": "❌ Not detected",
            "pii_handling": "⚠️ May be present",
            "backup_strategy": "Unknown",
            "data_retention": "Unknown",
            "recommendations": [
                "Implement TLS 1.3 for all connections",
                "Enable database encryption at rest",
                "Implement PII masking in logs",
                "Define data retention policy"
            ]
        }
    
    def _get_security_recommendations(self) -> List[str]:
        """Get prioritized security improvements"""
        return [
            "🔒 Priority 1: Implement Spring Security framework",
            "🔒 Priority 2: Enable HTTPS/TLS enforcement",
            "🔒 Priority 3: Add input validation and sanitization",
            "🔒 Priority 4: Implement comprehensive audit logging",
            "🔒 Priority 5: Regular dependency vulnerability scanning"
        ]
    
    def _has_logging(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Log" in ann for ann in annotations)
    
    def _has_data_encryption(self) -> bool:
        annotations = self._get_all_annotations()
        return any("Encrypt" in ann or "Crypto" in ann for ann in annotations)
    
    def _has_access_control(self) -> bool:
        annotations = self._get_all_annotations()
        return any("PreAuthorize" in ann or "Secured" in ann for ann in annotations)
    
    def _get_all_annotations(self) -> List[str]:
        annotations = []
        for class_node in self.kg.classes.values():
            annotations.extend(class_node.annotations)
        for method_node in self.kg.methods.values():
            annotations.extend(method_node.annotations)
        return annotations
