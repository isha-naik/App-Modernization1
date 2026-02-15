"""App Modernization - Cost Estimation & ROI Calculator"""
from typing import Dict, Any, List
from src.knowledge_graph.graph import KnowledgeGraph


class CostEstimator:
    """Estimate modernization costs and ROI"""
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
    
    def estimate_costs(self) -> Dict[str, Any]:
        """Comprehensive cost estimation"""
        planning = self._estimate_planning()
        development = self._estimate_development()
        testing = self._estimate_testing()
        deployment = self._estimate_deployment()
        training = self._estimate_training()
        
        total_cost = planning + development + testing + deployment + training
        
        return {
            "planning": planning,
            "development": development,
            "testing": testing,
            "deployment": deployment,
            "training": training,
            "total_cost": total_cost,
            "timeline_months": self._estimate_timeline(),
            "team_size": self._estimate_team_size(),
            "currency": "USD"
        }
    
    def calculate_roi(self) -> Dict[str, Any]:
        """Calculate return on investment"""
        costs = self.estimate_costs()
        
        # Estimated benefits
        efficiency_gains = 250000  # Annual
        reduction_in_incidents = 100000
        faster_deployments = 180000
        infrastructure_savings = 150000
        
        total_annual_benefits = efficiency_gains + reduction_in_incidents + faster_deployments + infrastructure_savings
        
        payback_period = costs["total_cost"] / (total_annual_benefits / 12)  # Months
        roi_percent = ((total_annual_benefits * 3 - costs["total_cost"]) / costs["total_cost"]) * 100  # 3-year ROI
        
        return {
            "total_cost": costs["total_cost"],
            "annual_benefits": {
                "efficiency_gains": efficiency_gains,
                "reduction_in_incidents": reduction_in_incidents,
                "faster_deployments": faster_deployments,
                "infrastructure_savings": infrastructure_savings,
                "total": total_annual_benefits
            },
            "payback_period_months": round(payback_period, 1),
            "roi_3_years": round(roi_percent, 1),
            "recommendation": "✅ High ROI - Proceed with modernization"
        }
    
    def _estimate_planning(self) -> int:
        """Estimate planning costs (4-6 weeks)"""
        # Planning team: 1 architect + 1 tech lead = $180/hour
        # 40 hours/week * 5 weeks * $180/hour = $36,000
        return 36000
    
    def _estimate_development(self) -> int:
        """Estimate development costs"""
        # Based on codebase size
        complexity = len(self.kg.classes) + len(self.kg.methods) + len(self.kg.endpoints)
        
        # Estimation: $80/developer hour
        # Average: 200 hours per complex system
        estimated_hours = min(complexity * 0.5, 2000)  # Cap at 2000 hours
        cost = estimated_hours * 150  # $150/hour for senior devs
        
        return int(cost)
    
    def _estimate_testing(self) -> int:
        """Estimate testing costs"""
        # Testing is typically 30-40% of development
        dev_cost = self._estimate_development()
        return int(dev_cost * 0.35)
    
    def _estimate_deployment(self) -> int:
        """Estimate deployment and DevOps costs"""
        # 2 weeks of DevOps engineer time
        # $180/hour * 80 hours = $14,400
        return 14400
    
    def _estimate_training(self) -> int:
        """Estimate training and documentation costs"""
        # 1 week trainer + documentation = $12,000
        return 12000
    
    def _estimate_timeline(self) -> int:
        """Estimate timeline in months"""
        complexity = len(self.kg.classes)
        if complexity < 50:
            return 3
        elif complexity < 150:
            return 6
        elif complexity < 300:
            return 9
        else:
            return 12
    
    def _estimate_team_size(self) -> Dict[str, int]:
        """Estimate team composition"""
        complexity = len(self.kg.classes)
        
        if complexity < 50:
            return {
                "architects": 1,
                "senior_developers": 1,
                "developers": 2,
                "qa_engineers": 1,
                "devops_engineers": 1,
                "total": 6
            }
        else:
            return {
                "architects": 1,
                "senior_developers": 2,
                "developers": 4,
                "qa_engineers": 2,
                "devops_engineers": 2,
                "total": 11
            }
