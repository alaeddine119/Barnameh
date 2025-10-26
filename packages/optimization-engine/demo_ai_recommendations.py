"""
End-to-End Demo: Ask AI About Operations
Combines ML predictions + OR optimization + Groq Llama 3
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommendation_engine import RecommendationEngine, MLPrediction, OptimizationResult


def create_sample_data():
    """Create sample predictions and optimization results"""
    
    # ML Predictions
    ml_predictions = MLPrediction(
        demand_forecast={
            'avg_quantity': 850,
            'peak_quantity': 1200,
            'trend': 'growing',
            'confidence': 95
        },
        anomalies=[
            {
                'type': 'bottleneck',
                'severity': 'high',
                'time': 'in 3 days',
                'probability': 0.89,
                'description': 'Resource bottleneck predicted in Machine-001 due to increased demand'
            },
            {
                'type': 'performance_degradation',
                'severity': 'medium',
                'time': 'in 7 days',
                'probability': 0.72,
                'description': 'Performance degradation detected in production line B'
            }
        ],
        kpis={
            'total_production': 12450,
            'avg_utilization': 87.5,
            'total_downtime': 45.5,
            'avg_attendance': 94.2
        }
    )
    
    # Optimization Results
    optimization_results = OptimizationResult(
        resource_allocation={
            'assignments': ['A1', 'A2', 'A3', 'A4', 'A5'],
            'avg_utilization': 85.2,
            'total_cost': 125000,
            'utilization': {
                'Machine-001': 95.5,
                'Machine-002': 78.3,
                'Machine-003': 82.1,
                'Worker-Pool-A': 88.5,
                'Worker-Pool-B': 75.8
            }
        },
        schedule={
            'total_shifts': 84,
            'coverage_rate': 92.5,
            'total_cost': 42000
        },
        capacity_plan={
            'current_capacity': 10000,
            'required_capacity': 12500,
            'capacity_gap': 2500,
            'investment': 250000,
            'roi_months': 8.5
        }
    )
    
    context = {
        'organization_id': 'Crédit Agricole Operations',
        'time_period': 'Next 30 days',
        'current_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    return ml_predictions, optimization_results, context


def main():
    """Main demo function"""
    
    print("\n" + "="*70)
    print("  AI-POWERED OPERATIONAL RECOMMENDATION SYSTEM")
    print("  ML Predictions + OR Optimization + Llama 3")
    print("="*70 + "\n")
    
    # Check for API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not found in environment variables")
        print("\nTo use this demo:")
        print("1. Get your API key from: https://console.groq.com/keys")
        print("2. Set environment variable:")
        print("   export GROQ_API_KEY='your-api-key-here'")
        print("\nOr create a .env file in the project root:")
        print("   GROQ_API_KEY=your-api-key-here")
        return
    
    print("✓ Groq API key found")
    print("✓ Initializing recommendation engine with Llama 3...\n")
    
    try:
        # Initialize engine
        engine = RecommendationEngine(api_key=api_key)
        print("✓ Engine initialized\n")
        
        # Create sample data
        ml_predictions, optimization_results, context = create_sample_data()
        print("✓ Sample data loaded")
        print(f"  - Demand forecast: {ml_predictions.demand_forecast['avg_quantity']} units/day")
        print(f"  - Anomalies detected: {len(ml_predictions.anomalies)}")
        print(f"  - Current utilization: {ml_predictions.kpis['avg_utilization']}%")
        print(f"  - Capacity gap: {optimization_results.capacity_plan['capacity_gap']} units\n")
        
        # Ask the question
        question = "How do I optimize operations for the next month?"
        
        print("━"*70)
        print(f"❓ Question: {question}")
        print("━"*70)
        print("\n🤖 Generating AI recommendation with Llama 3...\n")
        
        # Generate recommendation
        recommendation = engine.chat(
            question,
            ml_predictions,
            optimization_results,
            context
        )
        
        # Display result
        print(recommendation)
        
        # Interactive mode
        print("\n" + "="*70)
        print("💬 Interactive Mode")
        print("="*70)
        print("Ask your own operational questions (or 'quit' to exit)\n")
        
        while True:
            user_question = input("\n❓ Your question: ").strip()
            
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if not user_question:
                continue
            
            print("\n🤖 Thinking...\n")
            
            try:
                recommendation = engine.chat(
                    user_question,
                    ml_predictions,
                    optimization_results,
                    context
                )
                print(recommendation)
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    except ImportError:
        print("\n❌ ERROR: Groq SDK not installed")
        print("\nInstall with:")
        print("  pip install groq")
        return
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
