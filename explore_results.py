#!/usr/bin/env python3
"""
Simple helper to inspect results JSON and display PNGs.
Run: python explore_results.py
"""
import json
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

def print_json(path):
    p = Path(path)
    if not p.exists():
        print(f"[MISSING] {path}")
        return None
    obj = json.load(open(p, "r", encoding="utf-8"))
    print(f"\n--- {path} ---")
    for k, v in obj.items():
        print(f"{k}: ", end="")
        if isinstance(v, list):
            print(f"list(len={len(v)})")
            if len(v) > 0:
                print("  sample 0:", v[0])
        else:
            print(type(v).__name__)
    return obj

def show_image(path, title=None):
    p = Path(path)
    if not p.exists():
        print(f"[MISSING] {path}")
        return
    img = Image.open(p)
    plt.figure(figsize=(8,6))
    plt.imshow(img)
    plt.axis('off')
    if title:
        plt.title(title)
    plt.show()

def main():
    base = Path('results')
    roi_json = base / 'advanced_recommendations' / 'advanced_roi_analysis.json'
    roi_png = base / 'advanced_recommendations' / 'roi_optimization.png'
    pareto_png = base / 'advanced_recommendations' / 'pareto_frontier.png'
    causal_json = base / 'causal_analysis' / 'causal_analysis_results.json'
    causal_png = base / 'causal_analysis' / 'causal_analysis_dashboard.png'

    report = print_json(roi_json)
    print_json(causal_json)

    if report and 'optimal_ranking' in report:
        print('\nTop interventions:')
        for i, it in enumerate(report['optimal_ranking'][:5], 1):
            print(f' {i}. {it.get("intervention")}  ROI={it.get("expected_roi")}  success_rate={it.get("success_rate")}')

    show_image(roi_png, 'ROI Optimization')
    show_image(pareto_png, 'Pareto Frontier')
    show_image(causal_png, 'Causal Dashboard')

if __name__ == '__main__':
    main()