"""App Modernization - Preference Management System"""
import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ModernizationPreferences:
    """Stores user modernization preferences"""
    
    # Framework preferences
    target_framework: str = "Spring Boot 3.x"
    api_style: str = "REST"  # REST, GraphQL, gRPC, WebSocket
    
    # Architecture
    architecture: str = "Microservices"  # Monolith, Microservices, Serverless, Hybrid
    async_enabled: bool = True
    reactive_enabled: bool = False
    
    # Cloud
    cloud_provider: str = "AWS"  # AWS, Azure, GCP, Multi-cloud, On-premise
    containerization: str = "Docker"  # Docker, Kubernetes, Serverless
    
    # Database
    database_type: str = "PostgreSQL"  # PostgreSQL, MySQL, DynamoDB, MongoDB
    orm_framework: str = "JPA/Hibernate"  # JPA/Hibernate, Spring Data, MyBatis
    cache_strategy: str = "Redis"  # None, Redis, Memcached, ElastiCache
    # Build system
    build_system: str = "Maven"  # Maven or Gradle
    
    # Security
    security_framework: str = "Spring Security"  # Spring Security, OAuth2, Custom
    authentication: str = "JWT"  # JWT, OAuth2, SAML, LDAP
    encryption: str = "TLS1.3"  # TLS1.3, TLS1.2, Custom
    
    # Performance
    performance_priority: str = "Balanced"  # Speed, Balanced, Stability
    caching_enabled: bool = True
    cdn_enabled: bool = True
    
    # Budget & Timeline
    budget_usd: int = 150000
    timeline_months: int = 6
    team_size: int = 8
    
    # Compliance
    compliance_requirements: List[str] = None
    
    def __post_init__(self):
        if self.compliance_requirements is None:
            self.compliance_requirements = ["GDPR", "SOC2"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModernizationPreferences':
        """Create from dictionary"""
        return cls(**data)
    
    def save(self, path: str = "preferences.json"):
        """Save preferences to file"""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: str = "preferences.json") -> 'ModernizationPreferences':
        """Load preferences from file"""
        if Path(path).exists():
            data = json.loads(Path(path).read_text())
            return cls.from_dict(data)
        return cls()


class PreferenceManager:
    """Manage modernization preferences"""
    
    def __init__(self):
        self.preferences = ModernizationPreferences()
    
    def update_preferences(self, updates: Dict[str, Any]):
        """Update preferences"""
        for key, value in updates.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
    
    def get_summary(self) -> Dict[str, str]:
        """Get preference summary"""
        return {
            "Framework": self.preferences.target_framework,
            "API Style": self.preferences.api_style,
            "Architecture": self.preferences.architecture,
            "Cloud": self.preferences.cloud_provider,
            "Database": self.preferences.database_type,
            "Build System": self.preferences.build_system,
            "Security": self.preferences.authentication,
            "Budget": f"${self.preferences.budget_usd:,}",
            "Timeline": f"{self.preferences.timeline_months} months"
        }
    
    def validate_preferences(self) -> List[str]:
        """Validate preferences"""
        warnings = []
        
        if self.preferences.reactive_enabled and self.preferences.async_enabled:
            warnings.append("⚠️ Both async and reactive enabled - may be redundant")
        
        if self.preferences.cloud_provider == "On-premise" and self.preferences.containerization == "Kubernetes":
            warnings.append("ℹ️ Kubernetes requires infrastructure setup")
        
        if self.preferences.timeline_months < 3:
            warnings.append("⚠️ Timeline < 3 months may be too aggressive")
        
        return warnings if warnings else ["✅ Preferences validated successfully"]
