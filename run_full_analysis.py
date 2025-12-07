
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.recommendation.advanced_engine import BayesianOptimizationEngine
from src.prediction.causal_churn import CausalChurnAnalyzer
import pandas as pd
import numpy as np
from pathlib import Path


def run_complete_analysis():
    print("🚀 STARTING COMPLETE TELECOM CSAT ANALYSIS")
    print("=" * 50)

    # Create results directories
    Path("results").mkdir(exist_ok=True)

    # ========================================
    # 1. BAYESIAN OPTIMIZATION ENGINE
    # ========================================
    print("\n🔬 PHASE 1: Bayesian Intervention Optimization")
    print("-" * 40)

    engine = BayesianOptimizationEngine()
    engine.initialize_interventions()

    # Run Thompson Sampling
    print("🎯 Running Thompson Sampling...")
    ts_results = engine.thompson_sampling(n_trials=2000)
    print("   Top 3 interventions:")
    for name, stats in ts_results[:3]:
        print(f"   • {name}: ROI={stats['expected_roi']:.2f}, Success={stats['success_rate']:.1%}")

    # Run A/B test for top 2
    if len(ts_results) >= 2:
        print(f"\n🔬 Simulating A/B Test: {ts_results[0][0]} vs {ts_results[1][0]}")
        ab_test = engine.simulate_ab_test(ts_results[0][0], ts_results[1][0])
        print(f"   Winner: {ab_test['recommendation']} (Confidence: {ab_test['confidence']:.1%})")

    # Run Pareto optimization
    print("\n📊 Running Pareto Portfolio Optimization...")
    pareto = engine.pareto_optimization(budget=250000)
    if pareto:
        print(f"   Best portfolio (€{pareto[0]['cost']:,.0f}):")
        for intervention in pareto[0]['selected']:
            print(f"     - {intervention}")

    # Generate final ROI report
    print("\n💰 Generating Comprehensive ROI Analysis...")
    roi_report = engine.generate_roi_analysis()

    # ========================================
    # 2. CAUSAL CHURN ANALYSIS
    # ========================================
    print("\n\n🧪 PHASE 2: Causal Churn Analysis")
    print("-" * 40)

    # Create sample data (replace with your actual data)
    np.random.seed(42)
    n_samples = 2000

    print("📊 Creating synthetic telecom dataset...")
    telecom_data = pd.DataFrame({
        'customer_id': range(n_samples),
        'csat_score': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.15, 0.25, 0.3, 0.2]),
        'previous_complaints': np.random.poisson(1.2, n_samples),
        'tenure_months': np.random.exponential(24, n_samples) + 1,
        'monthly_bill': np.random.normal(55, 15, n_samples),
        'data_usage_gb': np.random.gamma(2, 10, n_samples),
        'contract_type': np.random.choice(['Monthly', 'Yearly', 'Two-Year'], n_samples, p=[0.4, 0.4, 0.2])
    })

    analyzer = CausalChurnAnalyzer()

    print("🔬 Running causal inference...")
    causal_results = analyzer.run_comprehensive_analysis(
        telecom_data,
        intervention_scenario="improve_all_wifi"
    )

    # ========================================
    # 3. INTEGRATED RECOMMENDATIONS
    # ========================================
    print("\n\n🎯 PHASE 3: Integrated Recommendations")
    print("-" * 40)

    print("\n📋 EXECUTIVE SUMMARY")
    print("-" * 40)

    # Combine insights from both analyses
    print("\n🏆 TOP 3 INTERVENTIONS (Bayesian Ranking):")
    if 'optimal_ranking' in roi_report:
        for i, item in enumerate(roi_report['optimal_ranking'][:3], 1):
            print(f"   {i}. {item['intervention']}")
            print(f"      Expected ROI: {item['expected_roi']:.2f}")
            print(f"      Success Rate: {item['success_rate']:.1%}")

    print("\n💡 CAUSAL INSIGHTS:")
    if 'improved_wifi' in analyzer.estimates:
        effect = analyzer.estimates['improved_wifi']
        print(f"   • WiFi Improvement reduces churn by {abs(effect['ate']):.3f}")
        print(f"   • Statistical significance: p={effect['p_value']:.3f}")

    if 'what_if' in analyzer.estimates:
        scenario = analyzer.estimates['what_if']
        print(f"   • '{scenario['scenario']}' would save:")
        print(
            f"     {scenario['customers_affected']} customers (${scenario['business_impact']['value_saved_euros']:,.0f})")

    # ========================================
    # 4. ACTION PLAN
    # ========================================
    print("\n\n📋 ACTION PLAN")
    print("-" * 40)

    print("\n🟢 IMMEDIATE ACTIONS (Next 30 days):")
    print("   1. Implement top intervention from Bayesian analysis")
    print("   2. Target WiFi improvements for high-complaint customers")
    print("   3. Allocate budget using Pareto-optimal portfolio")

    print("\n🟡 MID-TERM ACTIONS (Next 90 days):")
    print("   1. Set up A/B testing framework for interventions")
    print("   2. Create customer segments based on causal effects")
    print("   3. Monitor ROI weekly")

    print("\n🔴 LONG-TERM STRATEGY (Next 12 months):")
    print("   1. Build real-time recommendation engine")
    print("   2. Implement automated intervention system")
    print("   3. Create dashboard for executive monitoring")

    # ========================================
    # 5. OUTPUT FILES
    # ========================================
    print("\n\n💾 OUTPUT FILES")
    print("-" * 40)

    print("\n✅ Analysis complete! Files saved to:")
    print(f"   • results/advanced_recommendations/advanced_roi_analysis.json")
    print(f"   • results/advanced_recommendations/roi_optimization.png")
    print(f"   • results/advanced_recommendations/pareto_frontier.png")
    print(f"   • results/causal_analysis/causal_analysis_results.json")
    print(f"   • results/causal_analysis/causal_analysis_dashboard.png")

    print("\n📈 VISUALIZATION DASHBOARDS:")
    print("   Open the PNG files in /results to view:")
    print("     1. ROI Comparison Charts")
    print("     2. Pareto Optimal Frontier")
    print("     3. Causal Effects Dashboard")

    print("\n🎉 ANALYSIS COMPLETE! Ready for decision-making.")


if __name__ == "__main__":
    run_complete_analysis()