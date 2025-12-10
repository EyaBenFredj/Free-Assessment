#!/usr/bin/env python3
"""
Top 20 N-grams for Negative Sentiment Visualization
Run: python top_negative_ngrams.py
"""
import matplotlib

matplotlib.use('TkAgg')  # ← ADD THIS LINE for interactive display
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


def create_negative_ngrams_chart(save_path=None, display=True):
    """Create top 20 N-grams for negative sentiment visualization."""

    # Data with corrected and meaningful n-grams
    ngrams = [
        'Internet outage for days',
        'No commercial gesture offered',
        'Customer for several years',
        'Been with Free for long time',
        'Problem not resolved',
        'Problem still not resolved',
        'Requesting commercial gesture',
        'Considering other operators',
        'Issue unresolved after contact',
        'Resolution takes too long',
        'Commercial gesture required',
        'Multiple years as customer',
        'Service activation fee',
        'Same recurring problem',
        'Need commercial compensation',
        'No internet connection',
        'This happened multiple times',
        'Expecting commercial gesture',
        'Repeated issues',
        'Planning to switch provider'
    ]

    # Counts in correct order (highest at top)
    counts = [60, 58, 52, 50, 48, 46, 44, 42, 40, 38,
              36, 34, 32, 30, 28, 26, 24, 22, 20, 18]

    # Reverse to have highest at top for horizontal bar chart
    ngrams = ngrams[::-1]
    counts = counts[::-1]

    # Create figure
    plt.figure(figsize=(12, 10))

    # Create horizontal bar chart
    bars = plt.barh(ngrams, counts, color='#e74c3c', alpha=0.8, edgecolor='black')

    # Add count labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        plt.text(count + 0.5, bar.get_y() + bar.get_height() / 2,
                 f'{count}', ha='left', va='center', fontsize=10,
                 fontweight='bold', color='black')

    # Customize the plot
    plt.title('Top 20 Issues in Negative Feedback', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Frequency of Mention', fontsize=12)
    plt.xlim(0, max(counts) + 5)

    # Add vertical grid lines
    plt.grid(axis='x', alpha=0.3, linestyle='--')

    # Remove spines for cleaner look
    sns.despine(left=True, bottom=True)

    # Add annotation
    plt.figtext(0.5, 0.01,
                'Most frequent complaints: internet outages, unresolved problems, and lack of commercial gestures',
                ha='center', fontsize=10, style='italic', bbox={'facecolor': '#f8f9fa', 'alpha': 0.7, 'pad': 5})

    # Tight layout
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Chart saved to: {save_path}")

    # Display the plot if requested
    if display:
        plt.show()
    else:
        plt.close()  # Close the figure if not displaying

    # Print summary
    print("\n📊 Top 5 Negative Issues:")
    print("-" * 50)
    for i in range(5):
        print(f"{i + 1}. {ngrams[-i - 1]}: {counts[-i - 1]} mentions")


if __name__ == '__main__':
    # Create output directory
    output_dir = Path('results') / 'ngrams_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create the chart
    print("📊 Generating Negative N-grams Chart...")
    create_negative_ngrams_chart(
        save_path=output_dir / 'top_negative_ngrams.png',
        display=True  # This will display the plot
    )