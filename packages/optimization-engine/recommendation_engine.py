"""
Intelligent Recommendation Engine
Uses Groq's Llama 3 to generate natural language recommendations
from ML predictions and OR optimization results
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: Groq SDK not installed. Install with: pip install groq")


@dataclass
class MLPrediction:
    """ML Engine predictions"""
    demand_forecast: Dict
    anomalies: List[Dict]
    kpis: Dict


@dataclass
class OptimizationResult:
    """Optimization Engine results"""
    resource_allocation: Dict
    schedule: Dict
    capacity_plan: Dict


@dataclass
class IntelligentRecommendation:
    """AI-generated recommendation"""
    summary: str
    priority: str
    actions: List[str]
    rationale: str
    estimated_impact: str


class RecommendationEngine:
    """
    Intelligent Recommendation Engine using Groq's Llama 3
    
    Combines ML predictions with OR optimization results to generate
    natural language recommendations for operational decisions
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with Groq API key
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        if not GROQ_AVAILABLE:
            raise ImportError("Groq SDK not installed. Install with: pip install groq")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Updated to latest available model
    
    def generate_recommendation(
        self,
        user_question: str,
        ml_predictions: MLPrediction,
        optimization_results: OptimizationResult,
        context: Optional[Dict] = None
    ) -> IntelligentRecommendation:
        """
        Generate intelligent recommendation using Llama 3
        
        Args:
            user_question: User's operational question
            ml_predictions: Predictions from ML engine
            optimization_results: Results from optimization engine
            context: Additional context (organization, time period, etc.)
            
        Returns:
            IntelligentRecommendation with natural language guidance
        """
        
        # Build prompt with all context
        prompt = self._build_prompt(
            user_question,
            ml_predictions,
            optimization_results,
            context or {}
        )
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert operations consultant specializing in "
                        "operational efficiency optimization. You analyze ML predictions "
                        "and optimization algorithms to provide actionable recommendations. "
                        "Be specific, quantitative, and focus on business impact."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower for more consistent recommendations
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        result = json.loads(response.choices[0].message.content)
        
        # Convert estimated_impact to string if it's a dict
        estimated_impact = result.get('estimated_impact', 'Impact not estimated')
        if isinstance(estimated_impact, dict):
            # Convert dict to formatted string
            impact_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in estimated_impact.items()]
            estimated_impact = ', '.join(impact_parts)
        
        return IntelligentRecommendation(
            summary=result.get('summary', 'No summary available'),
            priority=result.get('priority', 'medium'),
            actions=result.get('actions', []),
            rationale=result.get('rationale', 'No rationale provided'),
            estimated_impact=str(estimated_impact)
        )
    
    def _build_prompt(
        self,
        question: str,
        ml_predictions: MLPrediction,
        optimization_results: OptimizationResult,
        context: Dict
    ) -> str:
        """Build comprehensive prompt for Llama 3"""
        
        prompt = f"""# Operational Question
{question}

# Current Context
- Organization: {context.get('organization_id', 'Unknown')}
- Time Period: {context.get('time_period', 'Next 30 days')}
- Current Date: {context.get('current_date', 'Today')}

# ML Predictions

## Demand Forecast
- Average Daily Demand: {ml_predictions.demand_forecast.get('avg_quantity', 0):.0f} units
- Peak Demand: {ml_predictions.demand_forecast.get('peak_quantity', 0):.0f} units
- Trend: {ml_predictions.demand_forecast.get('trend', 'stable')}
- Confidence: {ml_predictions.demand_forecast.get('confidence', 95)}%

## Detected Anomalies
"""
        
        # Add anomalies
        for i, anomaly in enumerate(ml_predictions.anomalies[:3], 1):
            prompt += f"""
### Anomaly {i}
- Type: {anomaly.get('type', 'unknown')}
- Severity: {anomaly.get('severity', 'medium')}
- Predicted Time: {anomaly.get('time', 'soon')}
- Probability: {anomaly.get('probability', 0)*100:.0f}%
- Description: {anomaly.get('description', 'No description')}
"""
        
        prompt += f"""
## Current KPIs
- Production: {ml_predictions.kpis.get('total_production', 0):.0f} units
- Utilization: {ml_predictions.kpis.get('avg_utilization', 0):.1f}%
- Downtime: {ml_predictions.kpis.get('total_downtime', 0):.1f} hours
- Attendance: {ml_predictions.kpis.get('avg_attendance', 0):.1f}%

# Optimization Results

## Resource Allocation
- Total Assignments: {len(optimization_results.resource_allocation.get('assignments', []))}
- Average Utilization: {optimization_results.resource_allocation.get('avg_utilization', 0):.1f}%
- Total Cost: ${optimization_results.resource_allocation.get('total_cost', 0):,.2f}
"""
        
        # Add resource details
        for resource_id, util in list(optimization_results.resource_allocation.get('utilization', {}).items())[:5]:
            prompt += f"- {resource_id}: {util}% utilized\n"
        
        prompt += f"""
## Staffing Schedule
- Total Shifts: {optimization_results.schedule.get('total_shifts', 0)}
- Coverage: {optimization_results.schedule.get('coverage_rate', 0):.1f}%
- Labor Cost: ${optimization_results.schedule.get('total_cost', 0):,.2f}

## Capacity Planning
- Current Capacity: {optimization_results.capacity_plan.get('current_capacity', 0):.0f} units
- Required Capacity: {optimization_results.capacity_plan.get('required_capacity', 0):.0f} units
- Capacity Gap: {optimization_results.capacity_plan.get('capacity_gap', 0):.0f} units
- Recommended Investment: ${optimization_results.capacity_plan.get('investment', 0):,.2f}
- Expected ROI: {optimization_results.capacity_plan.get('roi_months', 0):.1f} months

# Task
Based on the above data, provide a comprehensive operational recommendation.

Return your response as JSON with this structure:
{{
  "summary": "One-sentence executive summary",
  "priority": "critical|high|medium|low",
  "actions": ["Specific action 1", "Specific action 2", "Specific action 3"],
  "rationale": "Detailed explanation of why these actions are recommended",
  "estimated_impact": "Quantified expected impact (cost savings, efficiency gains, etc.)"
}}

Focus on:
1. Specific, actionable steps
2. Quantified impact (use numbers from the data)
3. Priority and timeline
4. Business value and ROI
"""
        
        return prompt
    
    def chat(
        self,
        question: str,
        ml_predictions: MLPrediction,
        optimization_results: OptimizationResult,
        context: Optional[Dict] = None
    ) -> str:
        """
        Simpler chat interface that returns formatted text
        
        Args:
            question: User's question
            ml_predictions: ML predictions
            optimization_results: Optimization results
            context: Additional context
            
        Returns:
            Formatted recommendation text
        """
        recommendation = self.generate_recommendation(
            question,
            ml_predictions,
            optimization_results,
            context
        )
        
        output = f"""
╔════════════════════════════════════════════════════════════════╗
║              INTELLIGENT OPERATIONAL RECOMMENDATION            ║
╚════════════════════════════════════════════════════════════════╝

Priority: {recommendation.priority.upper()}

📋 Summary
{recommendation.summary}

🎯 Recommended Actions
"""
        
        for i, action in enumerate(recommendation.actions, 1):
            output += f"{i}. {action}\n"
        
        output += f"""
💡 Rationale
{recommendation.rationale}

📈 Estimated Impact
{recommendation.estimated_impact}

────────────────────────────────────────────────────────────────
Generated by Llama 3 via Groq • Powered by ML + OR Algorithms
"""
        
        return output


# Convenience function for quick usage
def ask_operational_question(
    question: str,
    ml_predictions: Dict,
    optimization_results: Dict,
    api_key: Optional[str] = None
) -> str:
    """
    Quick function to get AI recommendation
    
    Example:
        recommendation = ask_operational_question(
            "How do I optimize operations?",
            ml_predictions=predictions,
            optimization_results=results
        )
        print(recommendation)
    """
    engine = RecommendationEngine(api_key=api_key)
    
    ml_pred = MLPrediction(
        demand_forecast=ml_predictions.get('forecast', {}),
        anomalies=ml_predictions.get('anomalies', []),
        kpis=ml_predictions.get('kpis', {})
    )
    
    opt_results = OptimizationResult(
        resource_allocation=optimization_results.get('resources', {}),
        schedule=optimization_results.get('schedule', {}),
        capacity_plan=optimization_results.get('capacity', {})
    )
    
    return engine.chat(question, ml_pred, opt_results)
