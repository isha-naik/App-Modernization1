"""Bedrock-based Migration Engine for API Modernization"""
import json
from typing import Dict, Any, Optional, List
import boto3
from pathlib import Path
from src.knowledge_graph.graph import KnowledgeGraph
from src.inference.api_detector import APIStyleDetector, GraphSummarizer


class BedrockLLMManager:
    """Manage calls to AWS Bedrock for migration planning"""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize Bedrock client"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name=region_name)
            self.model_id = "anthropic.claude-3-5-sonnet-20241022"  # Latest Claude 3.5
            self.available = True
        except Exception as e:
            print(f"Warning: Bedrock not configured: {e}")
            print("Will use local LLM fallback")
            self.available = False
            self.client = None
    
    def invoke_model(self, prompt: str) -> Optional[str]:
        """Call Bedrock model and get response"""
        if not self.available:
            return self._fallback_response(prompt)
        
        try:
            message = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-06-01",
                    "max_tokens": 2000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(message['body'].read())
            return response_body['content'][0]['text']
        except Exception as e:
            print(f"Bedrock error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when Bedrock is unavailable"""
        return "Local LLM fallback: Migration plan would be generated here with Bedrock integration."


class MigrationPlanGenerator:
    """Generate comprehensive migration plans"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        self.bedrock = BedrockLLMManager()
        self.summarizer = GraphSummarizer(knowledge_graph)
        self.detector = APIStyleDetector()
    
    def generate_migration_plan(self, 
                               source_framework: str = "Legacy",
                               target_framework: str = "Spring Boot 3",
                               migration_approach: str = "Incremental") -> Dict[str, Any]:
        """Generate comprehensive migration plan"""
        
        # Get analysis
        api_sig = self.summarizer.create_api_signature()
        api_style = self.detector.detect_style(self.kg)
        maturity = self.detector.analyze_rest_maturity(self.kg)
        
        # Build prompt for Bedrock
        prompt = self._build_migration_prompt(
            api_sig, api_style, maturity,
            source_framework, target_framework, migration_approach
        )
        
        # Get AI response
        ai_response = self.bedrock.invoke_model(prompt)
        
        # Parse and structure response
        plan = {
            "summary": {
                "source_framework": source_framework,
                "target_framework": target_framework,
                "approach": migration_approach,
                "endpoint_count": api_sig['total_endpoints'],
                "estimated_effort": self._estimate_effort(api_sig),
                "ai_notes": ai_response[:500]  # Summary from Bedrock
            },
            "analysis": {
                "api_style": api_style,
                "rest_maturity": maturity,
                "annotations": api_sig['annotation_counts'],
                "endpoints": api_sig['endpoints']
            },
            "recommendations": self._generate_recommendations(api_sig, api_style, maturity),
            "migration_steps": self._generate_steps(api_sig),
            "risk_assessment": self._assess_risks(api_sig)
        }
        
        return plan
    
    def _build_migration_prompt(self, api_sig: Dict, api_style: Dict,
                                maturity: Dict, source_fw: str, 
                                target_fw: str, approach: str) -> str:
        """Build prompt for Bedrock"""
        return f"""You are an expert Java API architect. Generate a migration plan for this codebase.

CODEBASE ANALYSIS:
- Total Classes: {api_sig['total_classes']}
- Total Methods: {api_sig['total_methods']}
- REST Endpoints: {api_sig['total_endpoints']}
- Top Annotations: {json.dumps(api_sig['annotation_counts'], indent=2)}

API ANALYSIS:
- Current Style: {api_style['primary_style']}
- REST Maturity Level: {maturity['level']}/3
- HTTP Methods: {maturity['http_methods']}

TARGET MIGRATION:
- From: {source_fw}
- To: {target_fw}
- Approach: {approach}

PACKAGES: {json.dumps(api_sig['packages'])}

Generate a concise migration plan with:
1. Key changes needed
2. Risk factors
3. Timeline estimate
4. Critical success factors

Format as JSON with keys: key_changes, risks, timeline_weeks, critical_factors"""
    
    def _estimate_effort(self, api_sig: Dict) -> str:
        """Estimate migration effort"""
        endpoints = api_sig['total_endpoints']
        if endpoints < 10:
            return "1-2 weeks"
        elif endpoints < 50:
            return "2-4 weeks"
        else:
            return "4-8 weeks"
    
    def _generate_recommendations(self, api_sig: Dict, 
                                 api_style: Dict, maturity: Dict) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        # Style-based recommendations
        if api_style['primary_style'] != "REST":
            recommendations.append(f"Migrate from {api_style['primary_style']} to REST architecture")
        
        # Maturity-based recommendations
        recommendations.extend(maturity.get('recommendations', []))
        
        # Size-based recommendations
        if api_sig['total_endpoints'] > 50:
            recommendations.append("Consider API versioning strategy (v1, v2)")
            recommendations.append("Implement rate limiting for scalability")
        
        if api_sig['total_classes'] > 100:
            recommendations.append("Consider microservices architecture")
            recommendations.append("Implement service discovery pattern")
        
        return recommendations
    
    def _generate_steps(self, api_sig: Dict) -> List[Dict[str, str]]:
        """Generate migration steps"""
        return [
            {
                "phase": "1. Assessment",
                "duration": "1 week",
                "tasks": [
                    "Document current API structure",
                    f"Analyze {api_sig['total_endpoints']} endpoints",
                    "Identify breaking changes",
                    "Plan deprecation strategy"
                ]
            },
            {
                "phase": "2. Preparation",
                "duration": "1-2 weeks",
                "tasks": [
                    "Set up new framework project",
                    "Create data migration scripts",
                    "Set up parallel environments",
                    "Create comprehensive test suite"
                ]
            },
            {
                "phase": "3. Migration",
                "duration": "2-4 weeks",
                "tasks": [
                    "Migrate core endpoints",
                    "Implement new authentication/auth",
                    "Migrate business logic",
                    "Port data models"
                ]
            },
            {
                "phase": "4. Testing & Validation",
                "duration": "1-2 weeks",
                "tasks": [
                    "Run integration tests",
                    "Performance testing",
                    "User acceptance testing",
                    "Load testing"
                ]
            },
            {
                "phase": "5. Deployment",
                "duration": "1 week",
                "tasks": [
                    "Blue-green deployment setup",
                    "Gradual traffic migration",
                    "Monitor for issues",
                    "Rollback plan ready"
                ]
            }
        ]
    
    def _assess_risks(self, api_sig: Dict) -> Dict[str, Any]:
        """Assess migration risks"""
        risks = []
        
        if api_sig['total_endpoints'] > 50:
            risks.append({
                "risk": "High complexity",
                "probability": "High",
                "mitigation": "Implement phased migration strategy"
            })
        
        endpoints = api_sig['total_endpoints']
        if endpoints > 0:
            risks.append({
                "risk": "API compatibility issues",
                "probability": "Medium",
                "mitigation": "Maintain API versioning and deprecation periods"
            })
        
        risks.append({
            "risk": "Data migration issues",
            "probability": "Low",
            "mitigation": "Comprehensive backup and rollback procedures"
        })
        
        return {
            "overall_risk_level": "Medium" if api_sig['total_endpoints'] > 20 else "Low",
            "identified_risks": risks
        }


class OpenAPIGenerator:
    """Generate OpenAPI 3.1 specification from knowledge graph"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
    
    def generate_openapi_spec(self, title: str = "API", 
                             version: str = "1.0.0") -> Dict[str, Any]:
        """Generate OpenAPI 3.1 specification"""
        
        spec = {
            "openapi": "3.1.0",
            "info": {
                "title": title,
                "version": version,
                "description": "Auto-generated from legacy codebase analysis"
            },
            "servers": [
                {"url": "https://api.example.com", "description": "Production"}
            ],
            "paths": {}
        }
        
        # Group endpoints by path
        paths_map = {}
        for endpoint in self.kg.endpoints.values():
            path = endpoint.path
            if path not in paths_map:
                paths_map[path] = {}
            
            method = endpoint.http_method.lower()
            paths_map[path][method] = {
                "summary": f"{endpoint.http_method} {path}",
                "operationId": f"{method}{''.join(p.capitalize() for p in path.split('/'))}",
                "tags": ["default"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    } if method != "get" else None
                },
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
            
            # Remove null requestBody
            if paths_map[path][method]["requestBody"]["content"] is None:
                del paths_map[path][method]["requestBody"]
        
        spec["paths"] = paths_map
        
        return spec
