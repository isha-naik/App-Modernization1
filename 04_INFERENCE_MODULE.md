# Inference Module Documentation

## Overview

The Inference module provides AI-powered analysis capabilities using LLMs. It detects frameworks, summarizes code structures, and extracts patterns from the knowledge graph.

## Key Components

1. **GraphSummarizer** - Creates compact summaries for LLM analysis
2. **FrameworkDetectorV2** - AI-powered framework detection with structured output
3. **PresentationLayerExtractor** - Extracts controllers and endpoints

---

## Component 1: GraphSummarizer

**Purpose**: Create compact, structured summaries of the knowledge graph for efficient LLM analysis.

**Location**: `src/inference/graph_summarizer.py`

### Why Summarization?

- Avoids token limit issues with large codebases
- Provides structured data instead of raw text
- Enables pattern detection across the codebase
- More reliable than RAG alone for holistic analysis

### Class Definition

```python
from collections import Counter
from src.knowledge_graph.graph import KnowledgeGraph

class GraphSummarizer:
    """Creates compact summaries for LLM analysis"""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph

    def create_framework_signature(self) -> Dict[str, Any]:
        """
        Create a compact signature for framework detection.

        Returns structured summary containing:
        - Annotation counts and patterns
        - Package structure analysis
        - Inheritance patterns
        - Interface implementations
        - Sample representative classes
        """
        signature = {
            "total_classes": len(self.kg.classes),
            "total_methods": len(self.kg.methods),
            "total_fields": len(self.kg.fields),
            "java_type_breakdown": self._count_java_types(),
            "annotation_counts": self._count_annotations(),
            "package_analysis": self._analyze_packages(),
            "inheritance_patterns": self._analyze_inheritance(),
            "interface_patterns": self._analyze_interfaces(),
            "common_superclasses": self._find_common_superclasses(),
            "sample_classes": self._get_representative_samples(),
            "endpoint_patterns": self._analyze_endpoints(),
            "dependency_injection_hints": self._detect_di_patterns()
        }
        return signature
```

### Key Methods

#### Count Annotations
```python
def _count_annotations(self) -> Dict[str, int]:
    """Count all annotations across classes and methods"""
    annotation_counter = Counter()

    for class_node in self.kg.classes.values():
        for annotation in class_node.annotations:
            annotation_counter[annotation] += 1

    for method_node in self.kg.methods.values():
        for annotation in method_node.annotations:
            annotation_counter[annotation] += 1

    # Return top 20 most common
    return dict(annotation_counter.most_common(20))
```

**Output Example**:
```json
{
    "RestController": 5,
    "Service": 8,
    "Repository": 4,
    "Autowired": 23,
    "GetMapping": 15,
    "PostMapping": 8
}
```

#### Analyze Packages
```python
def _analyze_packages(self) -> Dict[str, Any]:
    """Analyze package structure"""
    package_counter = Counter()
    top_level_packages = Counter()

    for class_node in self.kg.classes.values():
        if class_node.package:
            package_counter[class_node.package] += 1
            parts = class_node.package.split('.')
            if len(parts) >= 2:
                top_level = f"{parts[0]}.{parts[1]}"
                top_level_packages[top_level] += 1

    return {
        "top_packages": dict(package_counter.most_common(10)),
        "top_level_packages": dict(top_level_packages.most_common(10)),
        "total_unique_packages": len(package_counter)
    }
```

#### Analyze Endpoints
```python
def _analyze_endpoints(self) -> Dict[str, Any]:
    """Analyze REST endpoints for web framework detection"""
    if not self.kg.endpoints:
        return {"count": 0, "patterns": []}

    method_counter = Counter()
    path_patterns = []

    for endpoint in self.kg.endpoints.values():
        method_counter[endpoint.http_method] += 1
        path_patterns.append(endpoint.path)

    return {
        "count": len(self.kg.endpoints),
        "http_methods": dict(method_counter),
        "sample_paths": path_patterns[:5]
    }
```

#### Detect DI Patterns
```python
def _detect_di_patterns(self) -> Dict[str, Any]:
    """Detect dependency injection patterns"""
    di_hints = {
        "autowired_fields": 0,
        "constructor_injection": 0,
        "setter_injection": 0
    }

    for field_node in self.kg.fields.values():
        if "Autowired" in field_node.annotations:
            di_hints["autowired_fields"] += 1

    for method_node in self.kg.methods.values():
        if "Autowired" in method_node.annotations:
            if method_node.name == method_node.class_name.split('.')[-1]:
                di_hints["constructor_injection"] += 1
            elif method_node.name.startswith("set"):
                di_hints["setter_injection"] += 1

    return di_hints
```

#### Get Representative Samples
```python
def _get_representative_samples(self, num_samples: int = 10) -> List[Dict]:
    """Get sample annotated classes for LLM context"""
    samples = []

    # Prioritize annotated classes
    annotated_classes = [
        cls for cls in self.kg.classes.values()
        if cls.annotations
    ]

    for class_node in annotated_classes[:num_samples]:
        samples.append({
            "name": class_node.name,
            "java_type": class_node.java_type,
            "package": class_node.package,
            "annotations": class_node.annotations,
            "interfaces": class_node.interfaces,
            "superclass": class_node.superclass,
            "is_abstract": class_node.is_abstract
        })

    return samples
```

### Usage
```python
from src.inference.graph_summarizer import GraphSummarizer

summarizer = GraphSummarizer(knowledge_graph)
signature = summarizer.create_framework_signature()

print(f"Annotations: {signature['annotation_counts']}")
print(f"Endpoints: {signature['endpoint_patterns']}")
```

---

## Component 2: FrameworkDetectorV2

**Purpose**: Detect the framework using LLM with Pydantic structured output.

**Location**: `src/inference/framework_detector_v2.py`

### Pydantic Models for Structured Output

```python
from pydantic import BaseModel, Field

class FrameworkCandidate(BaseModel):
    """Single framework candidate"""
    name: str = Field(description="Framework name (e.g., Spring Boot, Struts)")
    version: Optional[str] = Field(default=None, description="Estimated version")
    confidence: float = Field(description="Confidence 0.0 to 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="Why this framework was detected")

class FrameworkDetectionResult(BaseModel):
    """Complete detection result"""
    primary_framework: FrameworkCandidate
    secondary_frameworks: List[FrameworkCandidate] = Field(default_factory=list)
    architecture_patterns: List[str] = Field(default_factory=list)
```

### Class Definition

```python
from langchain_google_genai import ChatGoogleGenerativeAI

class FrameworkDetectorV2:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0
        )

    def detect_framework(self, knowledge_graph: KnowledgeGraph) -> Dict[str, Any]:
        """Detect framework using LLM with structured output"""

        # Create structured summary
        summarizer = GraphSummarizer(knowledge_graph)
        signature = summarizer.create_framework_signature()

        # Create analysis prompt
        prompt = self._create_analysis_prompt(signature)

        # Use structured output
        structured_llm = self.llm.with_structured_output(FrameworkDetectionResult)
        detection: FrameworkDetectionResult = structured_llm.invoke(prompt)

        return {
            'framework': detection.primary_framework.name,
            'confidence': detection.primary_framework.confidence,
            'reasoning': detection.primary_framework.reasoning,
            'architecture_patterns': detection.architecture_patterns,
            'source': 'LLM',
            'secondary_frameworks': [
                {'name': f.name, 'confidence': f.confidence}
                for f in detection.secondary_frameworks
            ]
        }
```

### Analysis Prompt Template

```python
def _create_analysis_prompt(self, signature: Dict[str, Any]) -> str:
    prompt = f"""You are a Java framework expert. Analyze this codebase structure.

CODEBASE STRUCTURE:

Statistics:
- Total Classes: {signature['total_classes']}
- Java Types: {signature['java_type_breakdown']}
- Methods: {signature['total_methods']}

Top Annotations (with counts):
{json.dumps(signature['annotation_counts'], indent=2)}

Package Analysis:
{json.dumps(signature['package_analysis'], indent=2)}

Inheritance Patterns:
{json.dumps(signature['inheritance_patterns'], indent=2)}

REST Endpoints:
{json.dumps(signature['endpoint_patterns'], indent=2)}

Sample Classes:
{json.dumps(signature['sample_classes'], indent=2)}

FRAMEWORKS TO CONSIDER:
- Spring Boot: @RestController, @Service, @Repository, @Autowired
- Struts: @Action, @Result, @Namespace, extends Action
- JAX-RS: @Path, @GET, @POST, @Produces, @Consumes
- Jakarta EE: @Stateless, @Entity, @PersistenceContext
- Micronaut: @Controller, @Get, @Singleton
- Quarkus: @Path, @ApplicationScoped, @Inject

INSTRUCTIONS:
1. Analyze ALL patterns
2. Identify primary framework with confidence (0.0-1.0)
3. Be confident (>0.85) ONLY if evidence is strong
4. Identify architecture patterns (MVC, REST, Microservices)

Provide structured framework detection result."""

    return prompt
```

### Heuristic Fallback

```python
def _heuristic_detection(self, knowledge_graph: KnowledgeGraph) -> Dict[str, Any]:
    """Fallback if LLM fails"""
    scores = {
        'Spring Boot': 0,
        'Struts': 0,
        'JAX-RS': 0,
        'Plain Java': 0
    }

    for class_node in knowledge_graph.classes.values():
        annotations = set(class_node.annotations)

        if 'RestController' in annotations or 'Controller' in annotations:
            scores['Spring Boot'] += 10
        if 'Service' in annotations:
            scores['Spring Boot'] += 5
        if 'Action' in annotations:
            scores['Struts'] += 10
        if 'Path' in annotations:
            scores['JAX-RS'] += 10

    framework = max(scores, key=scores.get)
    max_score = scores[framework]

    return {
        'framework': framework,
        'confidence': min(max_score / 30.0, 1.0),
        'reasoning': f'Heuristic detection (score: {max_score})',
        'source': 'HEURISTIC'
    }
```

### Usage
```python
from src.inference.framework_detector_v2 import FrameworkDetectorV2

detector = FrameworkDetectorV2()
result = detector.detect_framework(knowledge_graph)

print(f"Framework: {result['framework']}")
print(f"Confidence: {result['confidence']:.0%}")
print(f"Reasoning: {result['reasoning']}")
```

---

## Latest LangChain Implementation

### Structured Output with Pydantic (LangChain 0.3+)

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Optional

# Define structured output model
class APIStyleResult(BaseModel):
    """API style detection result"""
    primary_style: str = Field(description="REST, GraphQL, SOAP, gRPC")
    version_strategy: str = Field(description="URL, Header, Query parameter")
    maturity_level: int = Field(description="Richardson Maturity Model 0-3", ge=0, le=3)
    openapi_compliant: bool = Field(description="Whether APIs follow OpenAPI patterns")
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

# Use with LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0
)

# Bind structured output
structured_llm = llm.with_structured_output(APIStyleResult)

# Invoke
result = structured_llm.invoke(prompt)
print(result.primary_style)  # "REST"
print(result.maturity_level)  # 2
```

### Tool Calling Pattern (Alternative)

```python
from langchain_core.tools import tool

@tool
def analyze_api_structure(
    endpoint_count: int,
    http_methods: dict,
    path_patterns: list
) -> dict:
    """Analyze API structure and return metrics.

    Args:
        endpoint_count: Number of endpoints
        http_methods: Count of HTTP methods used
        path_patterns: Sample path patterns
    """
    return {
        "restful": "GET" in http_methods and "POST" in http_methods,
        "crud_complete": all(m in http_methods for m in ["GET", "POST", "PUT", "DELETE"]),
        "versioned": any("/v" in p for p in path_patterns)
    }

# Bind tool to LLM
llm_with_tools = llm.bind_tools([analyze_api_structure])
```

---

## Adapting for API Modernization

### APIStyleDetector

```python
class APIStyleDetector:
    """Detect API style and modernization opportunities"""

    def detect_api_style(self, knowledge_graph: KnowledgeGraph) -> Dict[str, Any]:
        summarizer = GraphSummarizer(knowledge_graph)
        signature = summarizer.create_framework_signature()

        prompt = self._create_api_analysis_prompt(signature)

        structured_llm = self.llm.with_structured_output(APIStyleResult)
        result = structured_llm.invoke(prompt)

        return result.model_dump()

    def _create_api_analysis_prompt(self, signature: Dict) -> str:
        return f"""Analyze this API for modernization opportunities.

ENDPOINTS:
{json.dumps(signature['endpoint_patterns'], indent=2)}

ANNOTATIONS:
{json.dumps(signature['annotation_counts'], indent=2)}

Analyze:
1. REST maturity level (Richardson Model 0-3)
2. OpenAPI/Swagger compatibility
3. Versioning strategy
4. HTTP method usage patterns
5. Path naming conventions
6. Security patterns used
7. Deprecation status

Provide structured API style analysis."""
```

### REST Maturity Analyzer

```python
class RESTMaturityAnalyzer:
    """Analyze REST API maturity level"""

    def analyze(self, endpoints: List[EndpointNode]) -> Dict:
        # Level 0: Single URI, single verb (usually POST)
        # Level 1: Multiple URIs for different resources
        # Level 2: Proper HTTP verbs (GET, POST, PUT, DELETE)
        # Level 3: HATEOAS (hypermedia controls)

        unique_paths = set(e.path for e in endpoints)
        http_methods = Counter(e.http_method for e in endpoints)

        level = 0

        # Check Level 1: Multiple resources
        if len(unique_paths) > 1:
            level = 1

        # Check Level 2: Proper HTTP verbs
        if len(http_methods) >= 3:  # Uses multiple verbs
            level = 2

        # Check Level 3: Would need HATEOAS detection
        # (check for _links, self, etc. in response types)

        return {
            "maturity_level": level,
            "unique_resources": len(unique_paths),
            "http_methods_used": dict(http_methods),
            "recommendations": self._get_recommendations(level, http_methods)
        }
```

---

## Dependencies

```txt
# requirements.txt
langchain-google-genai>=2.0.0
pydantic>=2.0.0
```
