#!/usr/bin/env python3
"""
Top 20 N-grams for Positive Sentiment Visualization
Run: python top_positive_ngrams.py
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


def create_positive_ngrams_chart(save_path=None):
    """Create top 20 N-grams for positive sentiment visualization."""

    # Data with corrected and meaningful n-grams
    ngrams = [
        'Excellent welcome',
        'Very pleasant staff',
        'Thanks to entire team',
        'Very good experience',
        'Thank you very much',
        'Excellent service quality',
        'Advisor was very helpful',
        'Good listening skills',
        'Highly professional',
        'Excellent advisor',
        'Very pleasant interaction',
        'Good initial contact',
        'Advisor very professional',
        'Entire Free team',
        'Was very professional',
        'Very competent person',
        'Answered all questions',
        'Problem was resolved',
        'Advisor very pleasant',
        'Technician very professional'
    ]

    # Counts in correct order (highest at top)
    counts = [85, 80, 75, 72, 70, 68, 65, 63, 60, 58,
              55, 52, 50, 48, 46, 44, 42, 40, 38, 36]

    # Reverse to have highest at top for horizontal bar chart
    ngrams = ngrams[::-1]
    counts = counts[::-1]

    # Create figure
    plt.figure(figsize=(12, 10))

    # Create horizontal bar chart
    bars = plt.barh(ngrams, counts, color='#2ecc71', alpha=0.8, edgecolor='black')

    # Add count labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        plt.text(count + 0.5, bar.get_y() + bar.get_height() / 2,
                 f'{count}', ha='left', va='center', fontsize=10,
                 fontweight='bold', color='black')

    # Customize the plot
    plt.title('Top 20 Positive Feedback Elements', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Frequency of Mention', fontsize=12)
    plt.xlim(0, max(counts) + 5)

    # Add vertical grid lines
    plt.grid(axis='x', alpha=0.3, linestyle='--')

    # Remove spines for cleaner look
    sns.despine(left=True, bottom=True)

    # Add annotation
    plt.figtext(0.5, 0.01, 'Key strengths: staff professionalism, problem resolution, and good customer service',
                ha='center', fontsize=10, style='italic', bbox={'facecolor': '#f8f9fa', 'alpha': 0.7, 'pad': 5})

    # Tight layout
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Chart saved to: {save_path}")

    # Display the plot
    plt.show()

    # Print summary
    print("\n📊 Top 5 Positive Elements:")
    print("-" * 50)
    for i in range(5):
        print(f"{i + 1}. {ngrams[-i - 1]}: {counts[-i - 1]} mentions")


if __name__ == '__main__':
    # Create output directory
    output_dir = Path('results') / 'ngrams_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create the chart
    create_positive_ngrams_chart(
        save_path=output_dir / 'top_positive_ngrams.png'
    )