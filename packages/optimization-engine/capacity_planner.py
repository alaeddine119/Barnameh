"""
Capacity Planner - Long-term Capacity Planning
Uses forecasts and trends to plan capacity expansions
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics


@dataclass
class CapacityForecast:
    """Capacity forecast for future period"""
    period: str  # e.g., "2024-Q1"
    forecasted_demand: float
    current_capacity: float
    required_capacity: float
    capacity_gap: float
    utilization_rate: float
    investment_needed: float


@dataclass
class ExpansionPlan:
    """Capacity expansion plan"""
    plan_id: str
    timeline: str
    investment: float
    capacity_increase: float
    roi_months: float
    priority: str  # "critical", "high", "medium", "low"
    description: str


@dataclass
class CapacityPlanResult:
    """Capacity planning result"""
    forecasts: List[CapacityForecast]
    expansion_plans: List[ExpansionPlan]
    total_investment: float
    expected_roi: float
    recommendations: List[str]
    execution_time: float


class CapacityPlanner:
    """
    Long-term Capacity Planning Engine
    
    Analyzes demand forecasts and current capacity to recommend
    capacity expansion plans with ROI analysis
    """
    
    def __init__(self, capacity_cost_per_unit: float = 1000.0):
        """
        Args:
            capacity_cost_per_unit: Cost to add one unit of capacity
        """
        self.capacity_cost_per_unit = capacity_cost_per_unit
        self.current_capacity = 0.0
        self.demand_history: List[Tuple[datetime, float]] = []
    
    def set_current_capacity(self, capacity: float):
        """Set current operational capacity"""
        self.current_capacity = capacity
    
    def add_demand_history(self, date: datetime, demand: float):
        """Add historical demand data point"""
        self.demand_history.append((date, demand))
    
    def plan_capacity(
        self,
        demand_forecasts: List[Dict],  # List of {period, predicted_quantity}
        planning_horizon_months: int = 12,
        target_utilization: float = 0.85,
        revenue_per_unit: float = 100.0
    ) -> CapacityPlanResult:
        """
        Generate capacity expansion plan
        
        Args:
            demand_forecasts: Future demand predictions
            planning_horizon_months: How far ahead to plan
            target_utilization: Target capacity utilization (0.0-1.0)
            revenue_per_unit: Revenue generated per unit of production
            
        Returns:
            CapacityPlanResult with expansion plans and recommendations
        """
        start_time = datetime.now()
        
        # Analyze demand trend
        trend = self._analyze_trend()
        
        # Generate capacity forecasts
        capacity_forecasts = []
        for i, forecast in enumerate(demand_forecasts[:planning_horizon_months]):
            period = f"Month {i+1}"
            forecasted_demand = forecast.get('predicted_quantity', 0)
            
            # Calculate required capacity with buffer
            required_capacity = forecasted_demand / target_utilization
            capacity_gap = max(0, required_capacity - self.current_capacity)
            
            utilization_rate = min(
                forecasted_demand / self.current_capacity if self.current_capacity > 0 else 0,
                1.0
            )
            
            investment_needed = capacity_gap * self.capacity_cost_per_unit
            
            capacity_forecasts.append(CapacityForecast(
                period=period,
                forecasted_demand=round(forecasted_demand, 2),
                current_capacity=round(self.current_capacity, 2),
                required_capacity=round(required_capacity, 2),
                capacity_gap=round(capacity_gap, 2),
                utilization_rate=round(utilization_rate * 100, 2),
                investment_needed=round(investment_needed, 2)
            ))
        
        # Generate expansion plans
        expansion_plans = self._generate_expansion_plans(
            capacity_forecasts,
            revenue_per_unit,
            trend
        )
        
        # Calculate metrics
        total_investment = sum(plan.investment for plan in expansion_plans)
        
        # Calculate expected ROI
        total_additional_capacity = sum(plan.capacity_increase for plan in expansion_plans)
        annual_additional_revenue = total_additional_capacity * revenue_per_unit * 12
        expected_roi = (annual_additional_revenue / total_investment) * 100 if total_investment > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            capacity_forecasts,
            expansion_plans,
            trend
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return CapacityPlanResult(
            forecasts=capacity_forecasts,
            expansion_plans=expansion_plans,
            total_investment=round(total_investment, 2),
            expected_roi=round(expected_roi, 2),
            recommendations=recommendations,
            execution_time=execution_time
        )
    
    def _analyze_trend(self) -> str:
        """Analyze demand trend from historical data"""
        if len(self.demand_history) < 3:
            return "insufficient_data"
        
        # Sort by date
        sorted_history = sorted(self.demand_history, key=lambda x: x[0])
        
        # Calculate moving averages
        recent = sorted_history[-30:] if len(sorted_history) >= 30 else sorted_history
        older = sorted_history[:len(sorted_history)//2] if len(sorted_history) > 30 else sorted_history[:len(sorted_history)//3]
        
        if not recent or not older:
            return "stable"
        
        recent_avg = statistics.mean([d for _, d in recent])
        older_avg = statistics.mean([d for _, d in older])
        
        change_pct = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
        
        if change_pct > 10:
            return "growing"
        elif change_pct < -10:
            return "declining"
        else:
            return "stable"
    
    def _generate_expansion_plans(
        self,
        capacity_forecasts: List[CapacityForecast],
        revenue_per_unit: float,
        trend: str
    ) -> List[ExpansionPlan]:
        """Generate specific expansion plans based on forecasts"""
        plans = []
        
        # Analyze critical periods (utilization > 95%)
        critical_periods = [
            fc for fc in capacity_forecasts
            if fc.utilization_rate > 95
        ]
        
        if critical_periods:
            # Immediate expansion needed
            max_gap = max(fc.capacity_gap for fc in critical_periods)
            investment = max_gap * self.capacity_cost_per_unit
            monthly_revenue = max_gap * revenue_per_unit
            roi_months = investment / monthly_revenue if monthly_revenue > 0 else 999
            
            plans.append(ExpansionPlan(
                plan_id="EXP-001-CRITICAL",
                timeline="Immediate (0-3 months)",
                investment=round(investment, 2),
                capacity_increase=round(max_gap, 2),
                roi_months=round(roi_months, 2),
                priority="critical",
                description=f"Immediate capacity expansion to address critical utilization (>95%). "
                           f"Add {round(max_gap, 2)} units of capacity."
            ))
        
        # Analyze high-utilization periods (80-95%)
        high_util_periods = [
            fc for fc in capacity_forecasts
            if 80 <= fc.utilization_rate <= 95
        ]
        
        if high_util_periods and len(high_util_periods) > 3:
            avg_gap = statistics.mean([fc.capacity_gap for fc in high_util_periods])
            investment = avg_gap * self.capacity_cost_per_unit
            monthly_revenue = avg_gap * revenue_per_unit
            roi_months = investment / monthly_revenue if monthly_revenue > 0 else 999
            
            plans.append(ExpansionPlan(
                plan_id="EXP-002-HIGH",
                timeline="Short-term (3-6 months)",
                investment=round(investment, 2),
                capacity_increase=round(avg_gap, 2),
                roi_months=round(roi_months, 2),
                priority="high",
                description=f"Proactive expansion to prevent bottlenecks. "
                           f"Add {round(avg_gap, 2)} units of capacity."
            ))
        
        # Long-term strategic expansion based on trend
        if trend == "growing":
            # Plan for 20% additional capacity
            strategic_increase = self.current_capacity * 0.20
            investment = strategic_increase * self.capacity_cost_per_unit
            monthly_revenue = strategic_increase * revenue_per_unit * 0.7  # Conservative estimate
            roi_months = investment / monthly_revenue if monthly_revenue > 0 else 999
            
            plans.append(ExpansionPlan(
                plan_id="EXP-003-STRATEGIC",
                timeline="Long-term (6-12 months)",
                investment=round(investment, 2),
                capacity_increase=round(strategic_increase, 2),
                roi_months=round(roi_months, 2),
                priority="medium",
                description=f"Strategic expansion aligned with growth trend. "
                           f"Add {round(strategic_increase, 2)} units for future demand."
            ))
        
        # If no plans generated, suggest monitoring
        if not plans:
            plans.append(ExpansionPlan(
                plan_id="EXP-000-MONITOR",
                timeline="Monitor only",
                investment=0.0,
                capacity_increase=0.0,
                roi_months=0.0,
                priority="low",
                description="Current capacity is sufficient. Continue monitoring demand trends."
            ))
        
        return plans
    
    def _generate_recommendations(
        self,
        capacity_forecasts: List[CapacityForecast],
        expansion_plans: List[ExpansionPlan],
        trend: str
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Trend-based recommendations
        if trend == "growing":
            recommendations.append(
                "📈 Demand is growing. Prioritize capacity expansion to capture market opportunity."
            )
        elif trend == "declining":
            recommendations.append(
                "📉 Demand is declining. Focus on efficiency improvements rather than expansion."
            )
        else:
            recommendations.append(
                "➡️ Demand is stable. Maintain current capacity and optimize utilization."
            )
        
        # Utilization-based recommendations
        avg_utilization = statistics.mean([fc.utilization_rate for fc in capacity_forecasts])
        
        if avg_utilization > 90:
            recommendations.append(
                f"⚠️ Average utilization is {round(avg_utilization, 1)}%. "
                f"High risk of bottlenecks - immediate action required."
            )
        elif avg_utilization > 80:
            recommendations.append(
                f"💡 Average utilization is {round(avg_utilization, 1)}%. "
                f"Consider proactive expansion within 3-6 months."
            )
        elif avg_utilization < 60:
            recommendations.append(
                f"💰 Average utilization is {round(avg_utilization, 1)}%. "
                f"Capacity is underutilized - focus on demand generation or cost reduction."
            )
        
        # Investment recommendations
        critical_plans = [p for p in expansion_plans if p.priority == "critical"]
        if critical_plans:
            total_critical_investment = sum(p.investment for p in critical_plans)
            recommendations.append(
                f"🚨 Critical investments needed: ${round(total_critical_investment, 2):,}. "
                f"Secure funding immediately."
            )
        
        # ROI recommendations
        good_roi_plans = [p for p in expansion_plans if p.roi_months < 12]
        if good_roi_plans:
            recommendations.append(
                f"✅ {len(good_roi_plans)} expansion plan(s) have ROI < 12 months. "
                f"Highly recommended investments."
            )
        
        return recommendations
