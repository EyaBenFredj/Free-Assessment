"""
Lightweight CausalChurnAnalyzer compatible with run_full_analysis.py.
This provides mock causal estimates for the demo and writes results into results/causal_analysis.
Replace with real causal inference pipeline (DoWhy, EconML, Double ML) when you are ready.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class CausalChurnAnalyzer:
    def __init__(self):
        self.estimates = {}
        self.results_dir = Path("results/causal_analysis")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_comprehensive_analysis(self, df: pd.DataFrame, intervention_scenario: str = "improve_all_wifi"):
        """
        Run a simple mock causal analysis:
        - computes a synthetic ATE based on csat distribution
        - builds a 'what-if' business impact
        - saves a JSON report and simple dashboard PNG
        """
        if "csat_score" not in df.columns:
            raise ValueError("Dataframe must contain csat_score column for this mock analysis.")

        avg_csat = float(df["csat_score"].mean())
        ate = max(0.01, (5.0 - avg_csat) * 0.02)  # synthetic ATE
        p_value = float(np.clip(0.01 + (0.5 - ate) * 0.1, 0.001, 0.99))

        n_customers = int(df.shape[0])
        customers_affected = int(n_customers * ate * 10)
        value_saved_per_customer = 50  # euros (synthetic)
        value_saved = customers_affected * value_saved_per_customer

        self.estimates["improved_wifi"] = {"ate": float(ate), "p_value": float(p_value)}
        self.estimates["what_if"] = {
            "scenario": intervention_scenario,
            "customers_affected": customers_affected,
            "business_impact": {"value_saved_euros": int(value_saved)}
        }

        summary = {
            "avg_csat": avg_csat,
            "estimates": self.estimates
        }
        with open(self.results_dir / "causal_analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        plt.figure(figsize=(6,3))
        plt.bar(["Improved WiFi ATE"], [ate], color="C3")
        plt.ylabel("Estimated churn reduction (probability)")
        plt.title("Mock Causal Effect")
        plt.tight_layout()
        plt.savefig(self.results_dir / "causal_analysis_dashboard.png")
        plt.close()

        return summary
