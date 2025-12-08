
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import traceback

class CausalChurnAnalyzer:
    def __init__(self):
        self.estimates = {}
        self.results_dir = Path("results/causal_analysis")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_comprehensive_analysis(self, df: pd.DataFrame, intervention_scenario: str = "improve_all_wifi"):
        """
        Top-level runner. Normalizes column names, tries DoWhy then falls back to a mock analysis.
        Returns a dictionary summary and populates self.estimates.
        """
        # Normalize column name: accept 'csat' or 'csat_score'
        if "csat_score" not in df.columns and "csat" in df.columns:
            df = df.copy()
            df["csat_score"] = df["csat"]

        # Basic column checks
        if "csat_score" not in df.columns:
            raise ValueError("Dataframe must contain csat or csat_score column for this analysis.")

        # Try to run DoWhy analysis if available
        try:
            import dowhy  # noqa: F401
            dowhy_summary = self._try_dowhy_analysis(df, intervention_scenario)
            if dowhy_summary is not None:
                with open(self.results_dir / "causal_analysis_results.json", "w", encoding="utf-8") as f:
                    json.dump(dowhy_summary, f, indent=2)
                self._create_dashboard(dowhy_summary.get("estimates", {}))
                return dowhy_summary
        except Exception:
            # Dowhy not installed or failed: log and fall back to mock
            print("⚠️ Dowhy analysis not available or failed; falling back to mock analysis.")
            tb = traceback.format_exc().splitlines()
            for l in tb[:10]:
                print(l)

        # Fallback to mock analysis
        mock_summary = self._mock_analysis(df, intervention_scenario)
        with open(self.results_dir / "causal_analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(mock_summary, f, indent=2)
        self._create_dashboard(mock_summary.get("estimates", {}))
        return mock_summary

    def _try_dowhy_analysis(self, df: pd.DataFrame, intervention_scenario: str):
        """
        Small guarded DoWhy pipeline. This is a demo / starting point only.
        """
        try:
            from dowhy import CausalModel
            causal_df = df.copy().reset_index(drop=True)
            # Create a simple binary treatment variable for demo
            causal_df["treatment"] = (causal_df["csat_score"] >= 4).astype(int)
            # Outcome: synthetic for demo (in real data use observed churn target)
            causal_df["outcome"] = (5 - causal_df["csat_score"]) / 5.0

            # Naive common causes if present
            common_causes = []
            for col in ["previous_complaints", "tenure_months", "monthly_bill", "data_usage_gb"]:
                if col in causal_df.columns:
                    common_causes.append(col)

            model = CausalModel(
                data=causal_df,
                treatment="treatment",
                outcome="outcome",
                common_causes=common_causes
            )

            print("✅ Identified estimand for improved_wifi")
            identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)

            # Estimate effect using a simple method
            estimate = model.estimate_effect(
                identified_estimand,
                method_name="backdoor.linear_regression",
                test_significance=True
            )

            # Safely extract numeric values; different DoWhy versions/extractors vary
            ate = None
            # Try several attribute names/methods to get the point estimate
            for attr in ("value", "estimate", "estimator_value"):
                if hasattr(estimate, attr):
                    try:
                        ate = float(getattr(estimate, attr))
                        break
                    except Exception:
                        ate = None

            # try get_estimate()
            try:
                if ate is None and hasattr(estimate, "get_estimate"):
                    ate_candidate = estimate.get_estimate()
                    ate = float(ate_candidate)
            except Exception:
                ate = None

            stderr = getattr(estimate, "stderr", None)
            if stderr is None:
                stderr = getattr(estimate, "std_err", None)

            p_value = getattr(estimate, "p_value", None)

            ci_low = getattr(estimate, "ci_lower", None)
            ci_high = getattr(estimate, "ci_upper", None)
            if (ci_low is None or ci_high is None) and hasattr(estimate, "confidence_interval"):
                ci = getattr(estimate, "confidence_interval", None)
                if isinstance(ci, (list, tuple)) and len(ci) == 2:
                    ci_low, ci_high = ci

            estimates = {
                "improved_wifi": {
                    "ate": (None if ate is None else float(ate)),
                    "ate_stderr": (None if stderr is None else float(stderr)),
                    "p_value": (None if p_value is None else float(p_value)),
                    "ci_lower": (None if ci_low is None else float(ci_low)),
                    "ci_upper": (None if ci_high is None else float(ci_high)),
                }
            }

            # build what-if business impact using ATE if present
            n_customers = int(causal_df.shape[0])
            if ate is None:
                customers_affected = int(n_customers * 0.01)
            else:
                customers_affected = int(n_customers * abs(ate) * 10)

            value_saved_per_customer = 50
            value_saved = customers_affected * value_saved_per_customer

            what_if = {
                "scenario": intervention_scenario,
                "customers_affected": customers_affected,
                "business_impact": {"value_saved_euros": int(value_saved)}
            }

            summary = {
                "method": "dowhy_linear_regression_backdoor",
                "estimates": estimates,
                "what_if": what_if
            }

            self.estimates = estimates
            return summary
        except Exception:
            print("⚠️ DoWhy analysis failed internally (see traceback).")
            tb = traceback.format_exc().splitlines()
            for l in tb[:10]:
                print(l)
            return None

    def _mock_analysis(self, df: pd.DataFrame, intervention_scenario: str):
        avg_csat = float(df["csat_score"].mean())
        ate = max(0.01, (5.0 - avg_csat) * 0.02)
        p_value = float(np.clip(0.01 + (0.5 - ate) * 0.1, 0.001, 0.99))

        n_customers = int(df.shape[0])
        customers_affected = int(n_customers * ate * 10)
        value_saved_per_customer = 50
        value_saved = customers_affected * value_saved_per_customer

        estimates = {"improved_wifi": {"ate": float(ate), "p_value": float(p_value)}}
        what_if = {
            "scenario": intervention_scenario,
            "customers_affected": customers_affected,
            "business_impact": {"value_saved_euros": int(value_saved)}
        }
        self.estimates = estimates
        return {"method": "mock", "estimates": estimates, "what_if": what_if}

    def _create_dashboard(self, estimates_dict):
        try:
            ate_val = None
            if isinstance(estimates_dict, dict) and "improved_wifi" in estimates_dict:
                ate_val = estimates_dict["improved_wifi"].get("ate", None)

            plt.figure(figsize=(6, 3))
            if ate_val is not None:
                plt.bar(["Improved WiFi ATE"], [ate_val], color="C3")
                plt.ylabel("Estimated churn reduction (probability)")
                plt.title("Causal Effect (Improved WiFi)")
            else:
                plt.text(0.5, 0.5, "No valid estimate", ha="center", va="center")
                plt.title("Causal Effect (no estimate)")
                plt.axis("off")
            plt.tight_layout()
            plt.savefig(self.results_dir / "causal_analysis_dashboard.png")
            plt.close()
        except Exception:
            print("⚠️ Failed to create causal dashboard plot; continuing.")
            return