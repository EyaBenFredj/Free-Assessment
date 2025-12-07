"""
ACTUALLY IMPRESSIVE Recommendation Engine (fixed structure)

Fixes applied:
- Removed nested duplicate generate_roi_analysis definition.
- Moved helper functions (_convert_numpy_types, _create_optimization_visualizations) to class scope.
- Ensures JSON uses only native Python types before dumping.
- Adds seaborn import for nicer visuals (ensure seaborn in requirements).
"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List
import json
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class Intervention:
    name: str
    cost: float
    expected_impact: float
    uncertainty: float
    success_rate: float

class BayesianOptimizationEngine:
    """
    Bayesian multi-armed bandit for intervention optimization.
    Cleaned up and robust to JSON serialization and visualization.
    """

    def __init__(self):
        self.interventions: Dict[str, Intervention] = {}
        self.history = []
        self.results_dir = Path("results/advanced_recommendations")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def initialize_interventions(self):
        """Initialize with telecom-specific interventions"""
        self.interventions = {
            'wifi_optimization': Intervention(
                name="WiFi Mesh Network Deployment",
                cost=150000,  # €
                expected_impact=0.8,  # CSAT improvement
                uncertainty=0.2,
                success_rate=0.75
            ),
            'fiber_maintenance': Intervention(
                name="Proactive Fiber Maintenance",
                cost=80000,
                expected_impact=1.2,
                uncertainty=0.3,
                success_rate=0.65
            ),
            'advisor_training': Intervention(
                name="Advanced Advisor Training",
                cost=50000,
                expected_impact=0.6,
                uncertainty=0.15,
                success_rate=0.85
            ),
            'billing_simplification': Intervention(
                name="Billing Statement Simplification",
                cost=30000,
                expected_impact=0.4,
                uncertainty=0.1,
                success_rate=0.90
            ),
            'mobile_app_improvement': Intervention(
                name="Mobile App UX Overhaul",
                cost=200000,
                expected_impact=0.9,
                uncertainty=0.25,
                success_rate=0.70
            )
        }

    def thompson_sampling(self, n_trials: int = 1000) -> List:
        """
        Thompson Sampling for optimal intervention selection.
        Returns a ranked list of tuples: (key, stats_dict).
        """
        print("🎯 Running Thompson Sampling Optimization...")

        # Initialize Beta distributions for each intervention
        distributions = {}
        alphas = {}
        betas = {}

        for name, interv in self.interventions.items():
            alpha = interv.success_rate * 10 + 1
            beta = (1 - interv.success_rate) * 10 + 1
            alphas[name] = alpha
            betas[name] = beta
            distributions[name] = stats.beta(alpha, beta)

        results = {name: [] for name in self.interventions.keys()}

        for _ in range(n_trials):
            samples = {name: dist.rvs() for name, dist in distributions.items()}
            selected = max(samples, key=samples.get)
            outcome = np.random.binomial(1, self.interventions[selected].success_rate)

            # Update alpha/beta counters and distribution
            if outcome == 1:
                alphas[selected] += 1
            else:
                betas[selected] += 1
            distributions[selected] = stats.beta(alphas[selected], betas[selected])

            results[selected].append(int(outcome))

        final_stats = {}
        for name in self.interventions.keys():
            if results[name]:
                success_rate = float(np.mean(results[name]))
                # Example ROI metric: total value per cost
                total_value = success_rate * self.interventions[name].expected_impact * 1000
                roi = total_value / (self.interventions[name].cost + 1e-9)
                final_stats[name] = {
                    'success_rate': success_rate,
                    'expected_roi': float(roi),
                    'trials_selected': int(len(results[name])),
                    'total_value': float(total_value)
                }

        ranked = sorted(final_stats.items(), key=lambda x: x[1]['expected_roi'], reverse=True)
        return ranked

    def simulate_ab_test(self, intervention_a: str, intervention_b: str, sample_size: int = 1000) -> Dict:
        """
        Bayesian A/B test simulation.
        Returns probability that A beats B and a recommendation structure.
        """
        print(f"🔬 Simulating A/B Test: {intervention_a} vs {intervention_b}")

        if intervention_a not in self.interventions or intervention_b not in self.interventions:
            raise KeyError("Intervention keys not found in engine.interventions")

        interv_a = self.interventions[intervention_a]
        interv_b = self.interventions[intervention_b]

        outcomes_a = np.random.binomial(1, interv_a.success_rate, sample_size)
        outcomes_b = np.random.binomial(1, interv_b.success_rate, sample_size)

        alpha_a = int(outcomes_a.sum()) + 1
        beta_a = int(sample_size - outcomes_a.sum()) + 1
        alpha_b = int(outcomes_b.sum()) + 1
        beta_b = int(sample_size - outcomes_b.sum()) + 1

        n_sim = 10000
        samples_a = stats.beta(alpha_a, beta_a).rvs(n_sim)
        samples_b = stats.beta(alpha_b, beta_b).rvs(n_sim)

        prob_a_better = float(np.mean(samples_a > samples_b))
        expected_diff = float(samples_a.mean() - samples_b.mean())

        result = {
            'intervention_a': intervention_a,
            'intervention_b': intervention_b,
            'probability_a_beats_b': prob_a_better,
            'expected_difference': expected_diff,
            'recommendation': intervention_a if prob_a_better > 0.5 else intervention_b,
            'confidence': float(abs(prob_a_better - 0.5) * 2)
        }
        return result

    def pareto_optimization(self, budget: float = 300000) -> List[Dict]:
        """
        Multi-objective optimization: Maximize impact within budget.
        Returns Pareto front of optimal solutions (top 5).
        """
        print("📊 Running Multi-Objective Pareto Optimization...")

        interventions = list(self.interventions.items())
        n = len(interventions)
        n_portfolios = 10000
        portfolios = []

        for _ in range(n_portfolios):
            selected = np.random.binomial(1, 0.5, n)
            total_cost = float(sum(selected[i] * interventions[i][1].cost for i in range(n)))
            if total_cost <= budget:
                total_impact = float(sum(selected[i] * interventions[i][1].expected_impact for i in range(n)))
                efficiency = float(total_impact / total_cost) if total_cost > 0 else 0.0
                portfolios.append({
                    'selected': [interventions[i][0] for i in range(n) if selected[i] == 1],
                    'cost': total_cost,
                    'impact': total_impact,
                    'efficiency': efficiency
                })

        # Pareto front computation (non-dominated)
        pareto_front = []
        for i, p1 in enumerate(portfolios):
            dominated = False
            for j, p2 in enumerate(portfolios):
                if i != j:
                    if (p2['impact'] >= p1['impact'] and p2['cost'] <= p1['cost'] and
                            (p2['impact'] > p1['impact'] or p2['cost'] < p1['cost'])):
                        dominated = True
                        break
            if not dominated:
                pareto_front.append(p1)

        pareto_front.sort(key=lambda x: x['efficiency'], reverse=True)
        return pareto_front[:5]

    def generate_roi_analysis(self, historical_data: pd.DataFrame = None) -> Dict:
        """
        Comprehensive ROI analysis: runs Thompson sampling, A/B and Pareto optimization,
        builds a JSON report and writes visualization files to results/advanced_recommendations.
        """
        print("💰 Generating Advanced ROI Analysis...")

        optimal_ranking = self.thompson_sampling(n_trials=5000)

        if len(optimal_ranking) >= 2:
            ab_test = self.simulate_ab_test(optimal_ranking[0][0], optimal_ranking[1][0])
        else:
            ab_test = None

        pareto_solutions = self.pareto_optimization(budget=250000)

        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'optimal_ranking': [
                {
                    'intervention': name,
                    'success_rate': float(stats['success_rate']),
                    'expected_roi': float(stats['expected_roi']),
                    'total_value': float(stats['total_value'])
                }
                for name, stats in optimal_ranking[:3]
            ],
            'ab_test_result': ab_test,
            'pareto_optimal_solutions': pareto*

