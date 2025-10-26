"""
Resource Optimizer - Linear Programming for Resource Allocation
Uses ML forecasts to optimize resource allocation across operations
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

try:
    from pulp import LpMaximize, LpMinimize, LpProblem, LpStatus, LpVariable, lpSum
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    print("Warning: PuLP not installed. Using simplified optimization.")


@dataclass
class Resource:
    """Resource entity"""
    resource_id: str
    resource_type: str
    capacity: float
    cost_per_hour: float
    availability: float  # 0.0 to 1.0


@dataclass
class Task:
    """Task entity"""
    task_id: str
    product_id: str
    required_quantity: float
    duration_hours: float
    priority: int  # 1-10, higher = more important


@dataclass
class OptimizationResult:
    """Optimization result"""
    success: bool
    objective_value: float
    assignments: List[Dict]
    utilization: Dict[str, float]
    recommendations: List[str]
    execution_time: float


class ResourceOptimizer:
    """
    Resource Allocation Optimizer using Linear Programming
    
    Optimizes resource allocation to maximize throughput while minimizing costs
    """
    
    def __init__(self):
        self.resources: List[Resource] = []
        self.tasks: List[Task] = []
    
    def add_resource(self, resource: Resource):
        """Add a resource to the optimization problem"""
        self.resources.append(resource)
    
    def add_task(self, task: Task):
        """Add a task to the optimization problem"""
        self.tasks.append(task)
    
    def optimize(
        self, 
        forecasted_demand: Dict[str, float],
        time_horizon_hours: int = 168,
        minimize_cost: bool = False
    ) -> OptimizationResult:
        """
        Optimize resource allocation using Linear Programming
        
        Args:
            forecasted_demand: Dict mapping product_id to forecasted quantity
            time_horizon_hours: Planning horizon (default 1 week)
            minimize_cost: If True, minimize cost; if False, maximize throughput
            
        Returns:
            OptimizationResult with optimal assignments and recommendations
        """
        start_time = datetime.now()
        
        if not PULP_AVAILABLE:
            return self._simple_optimization(forecasted_demand, time_horizon_hours)
        
        # Create LP problem
        if minimize_cost:
            problem = LpProblem("Resource_Allocation_Cost_Minimization", LpMinimize)
        else:
            problem = LpProblem("Resource_Allocation_Throughput_Maximization", LpMaximize)
        
        # Decision variables: x[task_id][resource_id] = hours allocated
        x = {}
        for task in self.tasks:
            x[task.task_id] = {}
            for resource in self.resources:
                var_name = f"x_{task.task_id}_{resource.resource_id}"
                x[task.task_id][resource.resource_id] = LpVariable(
                    var_name, 
                    lowBound=0, 
                    upBound=resource.capacity * resource.availability
                )
        
        # Objective function
        if minimize_cost:
            # Minimize total cost
            problem += lpSum([
                x[task.task_id][resource.resource_id] * resource.cost_per_hour
                for task in self.tasks
                for resource in self.resources
            ])
        else:
            # Maximize throughput weighted by priority
            problem += lpSum([
                x[task.task_id][resource.resource_id] * task.priority
                for task in self.tasks
                for resource in self.resources
            ])
        
        # Constraints
        # 1. Resource capacity constraints
        for resource in self.resources:
            problem += (
                lpSum([
                    x[task.task_id][resource.resource_id]
                    for task in self.tasks
                ]) <= resource.capacity * resource.availability * time_horizon_hours,
                f"Capacity_{resource.resource_id}"
            )
        
        # 2. Task completion constraints (meet forecasted demand)
        for task in self.tasks:
            forecasted = forecasted_demand.get(task.product_id, 0)
            if forecasted > 0:
                problem += (
                    lpSum([
                        x[task.task_id][resource.resource_id]
                        for resource in self.resources
                    ]) >= task.duration_hours * min(forecasted, task.required_quantity),
                    f"Demand_{task.task_id}"
                )
        
        # Solve
        problem.solve()
        
        # Extract results
        assignments = []
        utilization = {}
        
        for resource in self.resources:
            total_hours = 0
            for task in self.tasks:
                allocated_hours = x[task.task_id][resource.resource_id].varValue or 0
                if allocated_hours > 0:
                    assignments.append({
                        'task_id': task.task_id,
                        'product_id': task.product_id,
                        'resource_id': resource.resource_id,
                        'resource_type': resource.resource_type,
                        'allocated_hours': round(allocated_hours, 2),
                        'cost': round(allocated_hours * resource.cost_per_hour, 2)
                    })
                    total_hours += allocated_hours
            
            utilization[resource.resource_id] = round(
                total_hours / (resource.capacity * time_horizon_hours) * 100, 2
            )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            assignments, 
            utilization, 
            forecasted_demand
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return OptimizationResult(
            success=LpStatus[problem.status] == 'Optimal',
            objective_value=problem.objective.value() or 0,
            assignments=assignments,
            utilization=utilization,
            recommendations=recommendations,
            execution_time=execution_time
        )
    
    def _simple_optimization(
        self, 
        forecasted_demand: Dict[str, float],
        time_horizon_hours: int
    ) -> OptimizationResult:
        """Simple greedy optimization when PuLP is not available"""
        start_time = datetime.now()
        
        assignments = []
        utilization = {}
        
        # Sort tasks by priority (highest first)
        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority, reverse=True)
        
        # Track remaining capacity
        remaining_capacity = {
            r.resource_id: r.capacity * r.availability * time_horizon_hours
            for r in self.resources
        }
        
        # Greedy assignment
        for task in sorted_tasks:
            forecasted = forecasted_demand.get(task.product_id, 0)
            if forecasted == 0:
                continue
            
            # Find best resource (lowest cost with available capacity)
            best_resource = None
            for resource in sorted(self.resources, key=lambda r: r.cost_per_hour):
                if remaining_capacity[resource.resource_id] >= task.duration_hours:
                    best_resource = resource
                    break
            
            if best_resource:
                allocated_hours = min(
                    task.duration_hours * forecasted,
                    remaining_capacity[best_resource.resource_id]
                )
                
                assignments.append({
                    'task_id': task.task_id,
                    'product_id': task.product_id,
                    'resource_id': best_resource.resource_id,
                    'resource_type': best_resource.resource_type,
                    'allocated_hours': round(allocated_hours, 2),
                    'cost': round(allocated_hours * best_resource.cost_per_hour, 2)
                })
                
                remaining_capacity[best_resource.resource_id] -= allocated_hours
        
        # Calculate utilization
        for resource in self.resources:
            used = (resource.capacity * resource.availability * time_horizon_hours - 
                   remaining_capacity[resource.resource_id])
            utilization[resource.resource_id] = round(
                used / (resource.capacity * resource.availability * time_horizon_hours) * 100, 2
            )
        
        recommendations = self._generate_recommendations(
            assignments, 
            utilization, 
            forecasted_demand
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return OptimizationResult(
            success=True,
            objective_value=sum(a['allocated_hours'] for a in assignments),
            assignments=assignments,
            utilization=utilization,
            recommendations=recommendations,
            execution_time=execution_time
        )
    
    def _generate_recommendations(
        self,
        assignments: List[Dict],
        utilization: Dict[str, float],
        forecasted_demand: Dict[str, float]
    ) -> List[str]:
        """Generate actionable recommendations based on optimization results"""
        recommendations = []
        
        # Check for over-utilized resources
        for resource_id, util in utilization.items():
            if util > 90:
                recommendations.append(
                    f"⚠️ Resource {resource_id} is highly utilized ({util}%). "
                    f"Consider adding capacity or redistributing workload."
                )
            elif util < 50:
                recommendations.append(
                    f"💡 Resource {resource_id} is under-utilized ({util}%). "
                    f"Consider reducing capacity or assigning additional tasks."
                )
        
        # Check for unmet demand
        assigned_products = {a['product_id'] for a in assignments}
        for product_id, demand in forecasted_demand.items():
            if product_id not in assigned_products and demand > 0:
                recommendations.append(
                    f"⚠️ No resources allocated for product {product_id} with demand {demand}. "
                    f"Consider adding resources or adjusting priorities."
                )
        
        # Cost optimization suggestions
        if assignments:
            total_cost = sum(a['cost'] for a in assignments)
            avg_cost = total_cost / len(assignments)
            high_cost_assignments = [a for a in assignments if a['cost'] > avg_cost * 1.5]
            
            if high_cost_assignments:
                recommendations.append(
                    f"💰 {len(high_cost_assignments)} assignments have costs 50% above average. "
                    f"Review resource allocation for cost optimization."
                )
        
        if not recommendations:
            recommendations.append("✅ Resource allocation is optimal. No immediate actions required.")
        
        return recommendations
