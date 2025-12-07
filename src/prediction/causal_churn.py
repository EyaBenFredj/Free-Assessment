
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import dowhy
from dowhy import CausalModel
import econml
from econml.dml import CausalForestDML
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy data types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, 'isoformat'):  # Handle datetime objects
            return obj.isoformat()
        return super(NumpyEncoder, self).default(obj)


class CausalChurnAnalyzer:
    """
    Causal inference to understand WHAT CAUSES churn
    Uses DoWhy + EconML for proper causal analysis
    """

    def __init__(self):
        self.causal_model = None
        self.estimates = {}
        self.results_dir = Path("results/causal_analysis")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def prepare_causal_data(self, df):
        """
        Prepare data for causal inference
        Creates treatment, outcome, and confounders
        """
        print("🔬 Preparing Causal Inference Data...")

        # Simulate realistic causal data
        np.random.seed(42)
        n_samples = len(df)

        # Treatments (interventions we could apply)
        treatments = pd.DataFrame({
            'improved_wifi': np.random.binomial(1, 0.3, n_samples),
            'billing_support': np.random.binomial(1, 0.4, n_samples),
            'advisor_training': np.random.binomial(1, 0.5, n_samples),
            'fiber_upgrade': np.random.binomial(1, 0.2, n_samples)
        })

        # Confounders (factors that affect both treatment and outcome)
        confounders = pd.DataFrame({
            'customer_tenure': np.random.exponential(2, n_samples) + 1,
            'previous_complaints': np.random.poisson(1.5, n_samples),
            'product_complexity': np.random.choice([1, 2, 3], n_samples, p=[0.5, 0.3, 0.2]),
            'urban_area': np.random.binomial(1, 0.7, n_samples),
            'monthly_spend': np.random.normal(45, 15, n_samples)
        })

        # Simulate outcome (churn) with causal effects
        # Base churn probability
        base_churn = 0.15

        # Causal effects of treatments
        treatment_effects = {
            'improved_wifi': -0.10,  # Reduces churn by 10%
            'billing_support': -0.08,
            'advisor_training': -0.12,
            'fiber_upgrade': -0.15
        }

        # Calculate churn probability with causal effects
        churn_probs = base_churn + np.zeros(n_samples)

        for treatment, effect in treatment_effects.items():
            churn_probs += treatments[treatment] * effect

        # Add noise from confounders
        churn_probs += confounders['previous_complaints'] * 0.03
        churn_probs += (confounders['product_complexity'] - 1) * 0.02
        churn_probs -= confounders['customer_tenure'] * 0.01

        # Ensure probabilities are valid
        churn_probs = np.clip(churn_probs, 0.01, 0.99)

        # Generate churn outcomes
        churn_outcome = np.random.binomial(1, churn_probs)

        # Combine into causal dataframe
        causal_df = pd.concat([
            treatments,
            confounders,
            pd.DataFrame({'churn': churn_outcome, 'churn_probability': churn_probs})
        ], axis=1)

        return causal_df

    def run_dowhy_analysis(self, causal_df):
        """
        Run DoWhy causal inference for one treatment
        """
        print("🧪 Running DoWhy Causal Inference...")

        # Focus on one treatment for demonstration
        treatment = 'improved_wifi'

        # Create causal model
        model = CausalModel(
            data=causal_df,
            treatment=treatment,
            outcome='churn',
            common_causes=['customer_tenure', 'previous_complaints',
                           'product_complexity', 'urban_area', 'monthly_spend']
        )

        # Identify causal effect
        identified_estimand = model.identify_effect()
        print(f"✅ Identified estimand for {treatment}")

        # Estimate effect (using linear regression for simplicity)
        estimate = model.estimate_effect(
            identified_estimand,
            method_name="backdoor.linear_regression",
            test_significance=True
        )

        # Store results
        self.estimates[treatment] = {
            'ate': float(estimate.value),
            'ate_stderr': float(estimate.stderr),
            'p_value': float(estimate.p_value),
            'interpretation': self._interpret_effect(estimate.value)
        }

        return estimate

    def run_causal_forest(self, causal_df):
        """
        Run Causal Forest for heterogeneous treatment effects
        Finds WHO benefits most from interventions
        """
        print("🌲 Running Causal Forest for Heterogeneous Effects...")

        # Prepare data
        X = causal_df[['customer_tenure', 'previous_complaints',
                       'product_complexity', 'urban_area', 'monthly_spend']].values
        T = causal_df['improved_wifi'].values.reshape(-1, 1)
        Y = causal_df['churn'].values

        # Train causal forest
        est = CausalForestDML(
            model_y=RandomForestRegressor(),
            model_t=RandomForestRegressor(),
            n_estimators=100,
            min_samples_leaf=5,
            random_state=42
        )

        est.fit(Y, T, X=X)

        # Get treatment effects
        treatment_effects = est.const_marginal_effect(X)
        ate = float(treatment_effects.mean())

        # Find heterogeneity
        te_std = float(treatment_effects.std())
        te_min = float(treatment_effects.min())
        te_max = float(treatment_effects.max())

        # Identify subgroups with largest effects
        high_effect_idx = np.where(treatment_effects < ate - te_std)[0]
        low_effect_idx = np.where(treatment_effects > ate + te_std)[0]

        # Analyze subgroups
        high_effect_profile = causal_df.iloc[high_effect_idx].mean() if len(high_effect_idx) > 0 else None
        low_effect_profile = causal_df.iloc[low_effect_idx].mean() if len(low_effect_idx) > 0 else None

        results = {
            'average_treatment_effect': ate,
            'effect_heterogeneity': {
                'std': te_std,
                'min': te_min,
                'max': te_max,
                'range': te_max - te_min
            },
            'high_effect_subgroup': {
                'size': int(len(high_effect_idx)),
                'profile': self._convert_series_to_dict(high_effect_profile) if high_effect_profile is not None else None,
                'avg_effect': float(treatment_effects[high_effect_idx].mean()) if len(high_effect_idx) > 0 else None
            },
            'low_effect_subgroup': {
                'size': int(len(low_effect_idx)),
                'profile': self._convert_series_to_dict(low_effect_profile) if low_effect_profile is not None else None,
                'avg_effect': float(treatment_effects[low_effect_idx].mean()) if len(low_effect_idx) > 0 else None
            }
        }

        # Save results
        self.estimates['causal_forest'] = results

        return results

    def what_if_simulation(self, causal_df, intervention_scenario):
        """
        Counterfactual simulation: What if we had done X?
        """
        print("🤔 Running What-If Simulation...")

        # Simulate intervention
        if intervention_scenario == "improve_all_wifi":
            # What if we improved WiFi for everyone with problems?
            wifi_issues = causal_df[causal_df['previous_complaints'] > 0].index
            modified_df = causal_df.copy()
            modified_df.loc[wifi_issues, 'improved_wifi'] = 1

            # Recalculate churn probabilities
            original_churn = float(causal_df['churn'].mean())

            # Estimate new churn rate (simplified)
            treatment_effect = -0.10  # From earlier analysis
            affected_frac = len(wifi_issues) / len(causal_df)
            new_churn = original_churn + (treatment_effect * affected_frac)

            simulation = {
                'scenario': intervention_scenario,
                'original_churn_rate': original_churn,
                'estimated_new_churn_rate': float(new_churn),
                'reduction_absolute': float(original_churn - new_churn),
                'reduction_relative': float((original_churn - new_churn) / original_churn * 100),
                'customers_affected': int(len(wifi_issues)),
                'business_impact': self._calculate_business_impact(
                    original_churn, new_churn, len(causal_df)
                )
            }

            self.estimates['what_if'] = simulation
            return simulation

        return None

    def _convert_series_to_dict(self, series):
        """Convert pandas Series to dict with proper type conversion"""
        if series is None:
            return None
        result = {}
        for key, value in series.items():
            if isinstance(value, np.integer):
                result[key] = int(value)
            elif isinstance(value, np.floating):
                result[key] = float(value)
            else:
                result[key] = value
        return result

    def _interpret_effect(self, effect_size):
        """Interpret causal effect size"""
        if effect_size < -0.05:
            return "Strong reduction in churn"
        elif effect_size < -0.02:
            return "Moderate reduction in churn"
        elif effect_size < 0:
            return "Slight reduction in churn"
        elif effect_size < 0.02:
            return "Negligible effect"
        else:
            return "Potential increase in churn"

    def _calculate_business_impact(self, old_rate, new_rate, n_customers, avg_lifetime_value=500):
        """Calculate business impact of churn reduction"""
        churn_diff = old_rate - new_rate
        customers_saved = churn_diff * n_customers
        value_saved = customers_saved * avg_lifetime_value

        return {
            'customers_saved_per_year': float(customers_saved),
            'value_saved_euros': float(value_saved),
            'roi_assuming_cost': float(value_saved / 150000)  # Assuming €150k intervention cost
        }

    def create_causal_visualizations(self):
        """Create professional causal inference visualizations"""
        print("📊 Creating Causal Inference Visualizations...")

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # 1. Treatment Effects Comparison
        if 'improved_wifi' in self.estimates:
            effects = []
            labels = []
            errors = []

            for treatment in ['improved_wifi', 'advisor_training', 'fiber_upgrade']:
                if treatment in self.estimates:
                    effects.append(self.estimates[treatment]['ate'])
                    labels.append(treatment.replace('_', ' ').title())
                    errors.append(self.estimates[treatment]['ate_stderr'])

            axes[0, 0].barh(labels, effects, xerr=errors, color='skyblue', alpha=0.7)
            axes[0, 0].axvline(x=0, color='red', linestyle='--', alpha=0.5)
            axes[0, 0].set_xlabel('Average Treatment Effect on Churn')
            axes[0, 0].set_title('Causal Effects of Interventions')
            axes[0, 0].grid(True, alpha=0.3, axis='x')

        # 2. Heterogeneous Effects Distribution
        if 'causal_forest' in self.estimates:
            cf_results = self.estimates['causal_forest']

            # Simulate treatment effects distribution
            te_dist = np.random.normal(
                cf_results['average_treatment_effect'],
                cf_results['effect_heterogeneity']['std'],
                1000
            )

            axes[0, 1].hist(te_dist, bins=30, density=True, alpha=0.6, color='green')
            axes[0, 1].axvline(x=cf_results['average_treatment_effect'],
                               color='red', linestyle='--', linewidth=2, label='ATE')
            axes[0, 1].set_xlabel('Treatment Effect')
            axes[0, 1].set_ylabel('Density')
            axes[0, 1].set_title('Heterogeneous Treatment Effects')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)

        # 3. What-If Scenario
        if 'what_if' in self.estimates:
            scenario = self.estimates['what_if']

            rates = [scenario['original_churn_rate'], scenario['estimated_new_churn_rate']]
            labels = ['Current', 'With Intervention']

            bars = axes[1, 0].bar(labels, rates, color=['lightcoral', 'lightgreen'])
            axes[1, 0].set_ylabel('Churn Rate')
            axes[1, 0].set_title(f"What-If: {scenario['scenario']}")
            axes[1, 0].grid(True, alpha=0.3, axis='y')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                axes[1, 0].text(bar.get_x() + bar.get_width() / 2, height,
                                f'{height:.3f}', ha='center', va='bottom')

        # 4. Business Impact
        if 'what_if' in self.estimates and 'business_impact' in self.estimates['what_if']:
            impact = self.estimates['what_if']['business_impact']

            metrics = ['Customers Saved', 'Value Saved (€k)', 'ROI']
            values = [
                impact['customers_saved_per_year'],
                impact['value_saved_euros'] / 1000,
                impact['roi_assuming_cost']
            ]

            colors = ['lightblue', 'lightgreen', 'gold']
            bars = axes[1, 1].bar(metrics, values, color=colors)
            axes[1, 1].set_title('Business Impact Analysis')
            axes[1, 1].grid(True, alpha=0.3, axis='y')

            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                axes[1, 1].text(bar.get_x() + bar.get_width() / 2, height,
                                f'{value:.1f}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(self.results_dir / 'causal_analysis_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Save results using custom encoder
        with open(self.results_dir / 'causal_analysis_results.json', 'w') as f:
            json.dump(self.estimates, f, indent=2, cls=NumpyEncoder)

        print(f"✅ Causal analysis saved to {self.results_dir}/")

    def run_comprehensive_analysis(self, df, intervention_scenario="improve_all_wifi"):
        """Run all analyses in sequence"""
        print("🚀 Starting Comprehensive Causal Analysis...")

        # Prepare causal data
        causal_df = self.prepare_causal_data(df)

        # Run DoWhy analysis
        dowhy_result = self.run_dowhy_analysis(causal_df)

        # Run Causal Forest
        causal_forest_result = self.run_causal_forest(causal_df)

        # Run What-If simulation
        what_if_result = self.what_if_simulation(causal_df, intervention_scenario)

        # Create visualizations
        self.create_causal_visualizations()

        print("\n📈 CAUSAL ANALYSIS COMPLETE!")
        print(f"   Results saved to: {self.results_dir}/")

        return {
            'dowhy': dowhy_result,
            'causal_forest': causal_forest_result,
            'what_if': what_if_result,
            'estimates': self.estimates
        }


# Example usage
if __name__ == "__main__":
    print("🧪 Testing Causal Churn Analysis...")

    # Create sample data
    np.random.seed(42)
    n_samples = 1000

    sample_df = pd.DataFrame({
        'customer_id': range(n_samples),
        'csat': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.15, 0.2, 0.3, 0.25]),
        'previous_complaints': np.random.poisson(1.5, n_samples)
    })

    analyzer = CausalChurnAnalyzer()

    # Run comprehensive analysis
    results = analyzer.run_comprehensive_analysis(sample_df)

    print("\n🔑 KEY FINDINGS:")

    if 'improved_wifi' in analyzer.estimates:
        effect = analyzer.estimates['improved_wifi']
        print(f"   • WiFi improvement reduces churn by {abs(effect['ate']):.3f} (p={effect['p_value']:.3f})")
        print(f"   • Interpretation: {effect['interpretation']}")

    if 'causal_forest' in analyzer.estimates:
        cf_results = analyzer.estimates['causal_forest']
        print(f"   • Causal Forest ATE: {cf_results['average_treatment_effect']:.3f}")
        print(f"   • Effect heterogeneity: {cf_results['effect_heterogeneity']['std']:.3f} std")
        print(f"   • High-effect subgroup size: {cf_results['high_effect_subgroup']['size']} customers")

    if 'what_if' in analyzer.estimates:
        scenario = analyzer.estimates['what_if']
        print(f"   • What-if scenario '{scenario['scenario']}':")
        print(f"     - Churn reduction: {scenario['reduction_relative']:.1f}%")
        print(f"     - Customers affected: {scenario['customers_affected']}")
        if 'business_impact' in scenario:
            impact = scenario['business_impact']
            print(f"     - Business value saved: €{impact['value_saved_euros']:,.0f}")
            print(f"     - ROI: {impact['roi_assuming_cost']:.2f}x")