"""
Scheduling Optimizer - Constraint Programming for Shift Scheduling
Optimizes employee shift schedules based on demand forecasts
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class Employee:
    """Employee entity"""
    employee_id: str
    name: str
    role: str
    max_hours_per_week: float
    cost_per_hour: float
    skills: List[str]
    availability: List[int]  # List of available hour indices (0-167 for a week)


@dataclass
class ShiftRequirement:
    """Shift requirement based on forecasted demand"""
    time_slot: int  # Hour index (0-167 for a week)
    role: str
    required_count: int
    priority: int


@dataclass
class Shift:
    """Assigned shift"""
    employee_id: str
    time_slot: int
    duration_hours: int
    role: str
    cost: float


@dataclass
class ScheduleResult:
    """Scheduling optimization result"""
    success: bool
    shifts: List[Shift]
    coverage: Dict[int, int]  # time_slot -> employee count
    total_cost: float
    employee_utilization: Dict[str, float]
    recommendations: List[str]
    execution_time: float


class SchedulingOptimizer:
    """
    Employee Shift Scheduling Optimizer
    
    Uses constraint programming principles to optimize employee schedules
    based on demand forecasts and availability constraints
    """
    
    def __init__(self):
        self.employees: List[Employee] = []
        self.requirements: List[ShiftRequirement] = []
    
    def add_employee(self, employee: Employee):
        """Add an employee to the scheduling problem"""
        self.employees.append(employee)
    
    def add_requirement(self, requirement: ShiftRequirement):
        """Add a shift requirement"""
        self.requirements.append(requirement)
    
    def generate_requirements_from_forecast(
        self,
        demand_forecast: List[Dict],
        conversion_factor: float = 0.5  # employees needed per unit of demand
    ):
        """
        Generate shift requirements from demand forecast
        
        Args:
            demand_forecast: List of forecast dicts with 'date' and 'quantity'
            conversion_factor: How many employees needed per unit of demand
        """
        for i, forecast in enumerate(demand_forecast):
            required_count = max(1, int(forecast.get('predicted_quantity', 0) * conversion_factor))
            
            # Create requirements for each 8-hour shift in the day
            for shift_start in [0, 8, 16]:  # Morning, afternoon, night shifts
                time_slot = i * 24 + shift_start
                
                self.requirements.append(ShiftRequirement(
                    time_slot=time_slot,
                    role='operator',
                    required_count=required_count,
                    priority=10 if shift_start == 8 else 7  # Higher priority for day shift
                ))
    
    def optimize(
        self,
        time_horizon_hours: int = 168,
        shift_duration: int = 8,
        minimize_cost: bool = True
    ) -> ScheduleResult:
        """
        Optimize shift schedule using greedy constraint satisfaction
        
        Args:
            time_horizon_hours: Planning horizon (default 1 week)
            shift_duration: Duration of each shift in hours
            minimize_cost: If True, prefer lower-cost employees
            
        Returns:
            ScheduleResult with optimal schedule and recommendations
        """
        start_time = datetime.now()
        
        shifts = []
        coverage = {}
        employee_hours = {emp.employee_id: 0 for emp in self.employees}
        
        # Sort requirements by priority (highest first)
        sorted_requirements = sorted(
            self.requirements, 
            key=lambda r: (r.priority, r.time_slot), 
            reverse=True
        )
        
        # Sort employees by cost (lowest first if minimizing cost)
        sorted_employees = sorted(
            self.employees,
            key=lambda e: e.cost_per_hour if minimize_cost else -e.cost_per_hour
        )
        
        # Greedy assignment
        for req in sorted_requirements:
            assigned_count = 0
            
            for employee in sorted_employees:
                # Check constraints
                if assigned_count >= req.required_count:
                    break
                
                # Check role match
                if req.role not in employee.skills:
                    continue
                
                # Check availability
                if req.time_slot not in employee.availability:
                    continue
                
                # Check max hours
                if employee_hours[employee.employee_id] + shift_duration > employee.max_hours_per_week:
                    continue
                
                # Check for shift conflicts
                conflict = False
                for shift in shifts:
                    if (shift.employee_id == employee.employee_id and
                        abs(shift.time_slot - req.time_slot) < shift_duration):
                        conflict = True
                        break
                
                if conflict:
                    continue
                
                # Assign shift
                shift = Shift(
                    employee_id=employee.employee_id,
                    time_slot=req.time_slot,
                    duration_hours=shift_duration,
                    role=req.role,
                    cost=shift_duration * employee.cost_per_hour
                )
                
                shifts.append(shift)
                employee_hours[employee.employee_id] += shift_duration
                assigned_count += 1
                
                # Update coverage
                for hour in range(req.time_slot, req.time_slot + shift_duration):
                    coverage[hour] = coverage.get(hour, 0) + 1
        
        # Calculate metrics
        total_cost = sum(shift.cost for shift in shifts)
        
        employee_utilization = {}
        for employee in self.employees:
            hours_worked = employee_hours[employee.employee_id]
            utilization = (hours_worked / employee.max_hours_per_week) * 100
            employee_utilization[employee.employee_id] = round(utilization, 2)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            shifts,
            coverage,
            employee_utilization,
            sorted_requirements
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ScheduleResult(
            success=len(shifts) > 0,
            shifts=shifts,
            coverage=coverage,
            total_cost=round(total_cost, 2),
            employee_utilization=employee_utilization,
            recommendations=recommendations,
            execution_time=execution_time
        )
    
    def _generate_recommendations(
        self,
        shifts: List[Shift],
        coverage: Dict[int, int],
        employee_utilization: Dict[str, float],
        requirements: List[ShiftRequirement]
    ) -> List[str]:
        """Generate actionable recommendations based on scheduling results"""
        recommendations = []
        
        # Check for understaffed time slots
        understaffed_slots = []
        for req in requirements:
            actual_coverage = sum(
                coverage.get(hour, 0)
                for hour in range(req.time_slot, req.time_slot + 8)
            ) / 8
            
            if actual_coverage < req.required_count * 0.8:  # Less than 80% coverage
                understaffed_slots.append(req.time_slot)
        
        if understaffed_slots:
            recommendations.append(
                f"⚠️ {len(understaffed_slots)} time slots have insufficient coverage. "
                f"Consider hiring additional staff or adjusting employee availability."
            )
        
        # Check for over/under-utilized employees
        overworked = [emp_id for emp_id, util in employee_utilization.items() if util > 95]
        underutilized = [emp_id for emp_id, util in employee_utilization.items() if util < 50]
        
        if overworked:
            recommendations.append(
                f"⚠️ {len(overworked)} employees are near maximum hours. "
                f"Monitor for burnout and consider workload redistribution."
            )
        
        if underutilized:
            recommendations.append(
                f"💡 {len(underutilized)} employees have low utilization. "
                f"Consider cross-training or adjusting schedules for better efficiency."
            )
        
        # Check shift distribution
        if shifts:
            shift_by_employee = {}
            for shift in shifts:
                shift_by_employee[shift.employee_id] = shift_by_employee.get(shift.employee_id, 0) + 1
            
            max_shifts = max(shift_by_employee.values())
            min_shifts = min(shift_by_employee.values())
            
            if max_shifts - min_shifts > 5:
                recommendations.append(
                    f"📊 Large variance in shift distribution (max: {max_shifts}, min: {min_shifts}). "
                    f"Consider balancing workload more evenly."
                )
        
        if not recommendations:
            recommendations.append("✅ Schedule is well-balanced. No immediate actions required.")
        
        return recommendations
    
    def export_schedule(self, result: ScheduleResult, format: str = 'json') -> str:
        """
        Export schedule to various formats
        
        Args:
            result: ScheduleResult to export
            format: 'json', 'csv', or 'text'
            
        Returns:
            Formatted schedule string
        """
        if format == 'json':
            export_data = {
                'shifts': [
                    {
                        'employee_id': s.employee_id,
                        'time_slot': s.time_slot,
                        'duration_hours': s.duration_hours,
                        'role': s.role,
                        'cost': s.cost
                    }
                    for s in result.shifts
                ],
                'total_cost': result.total_cost,
                'employee_utilization': result.employee_utilization,
                'recommendations': result.recommendations
            }
            return json.dumps(export_data, indent=2)
        
        elif format == 'text':
            lines = ["=== SHIFT SCHEDULE ===\n"]
            
            # Group by employee
            shifts_by_employee = {}
            for shift in result.shifts:
                if shift.employee_id not in shifts_by_employee:
                    shifts_by_employee[shift.employee_id] = []
                shifts_by_employee[shift.employee_id].append(shift)
            
            for emp_id, emp_shifts in shifts_by_employee.items():
                lines.append(f"\nEmployee: {emp_id}")
                lines.append(f"Utilization: {result.employee_utilization.get(emp_id, 0)}%")
                
                for shift in sorted(emp_shifts, key=lambda s: s.time_slot):
                    day = shift.time_slot // 24
                    hour = shift.time_slot % 24
                    lines.append(
                        f"  Day {day+1}, {hour:02d}:00 - {(hour+shift.duration_hours)%24:02d}:00 "
                        f"({shift.role}) - ${shift.cost}"
                    )
            
            lines.append(f"\nTotal Cost: ${result.total_cost}")
            lines.append(f"\nRecommendations:")
            for rec in result.recommendations:
                lines.append(f"  • {rec}")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
