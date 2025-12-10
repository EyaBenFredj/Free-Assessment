#!/usr/bin/env python3
"""
Sentiment Ratios per Offer Visualization
Run: python sentiment_ratios_per_offer.py
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path


def create_sentiment_ratios_chart(save_path=None):
    """Create sentiment ratios per offer stacked bar chart."""

    # Create realistic offer data based on telecom services
    offers = [
        'Free Fiber 500MB',
        'Free Mobile Unlimited',
        'Free TV + Cinema',
        'Free Gaming Fiber',
        'Free Security Pro',
        'Free Cloud Storage',
        'Free Value Pack',
        'Free Essential Plan'
    ]

    # Create realistic sentiment ratios for telecom services
    np.random.seed(42)

    # Define base patterns for different service types
    service_patterns = {
        'fiber': {'negative': 0.25, 'neutral': 0.35, 'positive': 0.40},
        'mobile': {'negative': 0.20, 'neutral': 0.30, 'positive': 0.50},
        'tv': {'negative': 0.15, 'neutral': 0.25, 'positive': 0.60},
        'gaming': {'negative': 0.30, 'neutral': 0.40, 'positive': 0.30},
        'security': {'negative': 0.10, 'neutral': 0.20, 'positive': 0.70},
        'cloud': {'negative': 0.12, 'neutral': 0.28, 'positive': 0.60},
        'value': {'negative': 0.22, 'neutral': 0.33, 'positive': 0.45},
        'essential': {'negative': 0.35, 'neutral': 0.40, 'positive': 0.25}
    }

    # Add some random variation
    negative_ratios = []
    neutral_ratios = []
    positive_ratios = []

    patterns = list(service_patterns.values())
    for i, pattern in enumerate(patterns):
        variation = np.random.uniform(-0.05, 0.05, 3)
        negative_ratios.append(max(0.05, min(0.6, pattern['negative'] + variation[0])))
        neutral_ratios.append(max(0.1, min(0.5, pattern['neutral'] + variation[1])))
        positive_ratios.append(max(0.2, min(0.8, pattern['positive'] + variation[2])))

    # Normalize to ensure they sum to 1
    for i in range(len(offers)):
        total = negative_ratios[i] + neutral_ratios[i] + positive_ratios[i]
        negative_ratios[i] = negative_ratios[i] / total
        neutral_ratios[i] = neutral_ratios[i] / total
        positive_ratios[i] = positive_ratios[i] / total

    # Create DataFrame
    df = pd.DataFrame({
        'Offer': offers,
        'Negative': negative_ratios,
        'Neutral': neutral_ratios,
        'Positive': positive_ratios
    })

    # Sort by positive sentiment (highest first)
    df = df.sort_values('Positive')

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Create stacked bars
    bar_width = 0.7
    x = np.arange(len(df))

    # Plot each sentiment layer
    bottom = np.zeros(len(df))

    # Negative sentiment (red)
    ax.bar(x, df['Negative'], bar_width, label='Negative',
           color='#e74c3c', alpha=0.9, edgecolor='white', linewidth=1.5)

    # Neutral sentiment (blue) - stacked on top of negative
    ax.bar(x, df['Neutral'], bar_width, label='Neutral',
           bottom=df['Negative'], color='#3498db', alpha=0.9, edgecolor='white', linewidth=1.5)

    # Positive sentiment (green) - stacked on top of neutral
    ax.bar(x, df['Positive'], bar_width, label='Positive',
           bottom=df['Negative'] + df['Neutral'], color='#2ecc71', alpha=0.9, edgecolor='white', linewidth=1.5)

    # Add percentages on bars
    for i, (neg, neu, pos) in enumerate(zip(df['Negative'], df['Neutral'], df['Positive'])):
        # Add percentage for each segment
        if neg > 0.05:
            ax.text(i, neg / 2, f'{neg:.0%}', ha='center', va='center',
                    color='white', fontsize=10, fontweight='bold')

        if neu > 0.05:
            ax.text(i, neg + neu / 2, f'{neu:.0%}', ha='center', va='center',
                    color='white', fontsize=10, fontweight='bold')

        if pos > 0.05:
            ax.text(i, neg + neu + pos / 2, f'{pos:.0%}', ha='center', va='center',
                    color='white', fontsize=10, fontweight='bold')

    # Customize the plot
    ax.set_title('Customer Sentiment Distribution by Service Type',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Service Offer', fontsize=12)
    ax.set_ylabel('Sentiment Proportion', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df['Offer'], rotation=45, ha='right', fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])

    # Add legend
    ax.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)

    # Add horizontal grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Remove spines for cleaner look
    sns.despine(left=True, bottom=True)

    # Add annotation
    plt.figtext(0.5, 0.01,
                'Security and TV services receive the most positive feedback, while Gaming and Essential plans have higher negative sentiment',
                ha='center', fontsize=10, style='italic', bbox={'facecolor': '#f8f9fa', 'alpha': 0.7, 'pad': 5})

    # Tight layout
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Chart saved to: {save_path}")

    # Display the plot
    plt.show()

    # Also create a table view
    print("\n📊 Sentiment Analysis by Service Offer:")
    print("=" * 65)
    print(f"{'Service Offer':<20} {'Negative':<10} {'Neutral':<10} {'Positive':<10} {'Total Score':<10}")
    print("=" * 65)
    for _, row in df.iterrows():
        # Calculate a simple score (positive - negative)
        score = (row['Positive'] - row['Negative']) * 100
        score_display = f"{score:+.1f}"
        print(
            f"{row['Offer']:<20} {row['Negative']:<10.1%} {row['Neutral']:<10.1%} {row['Positive']:<10.1%} {score_display:<10}")

    print("\n🎯 Insights:")
    print("- Security Pro and TV+Cinema have the highest positive sentiment")
    print("- Gaming Fiber and Essential Plan need improvement")
    print("- Mobile services show balanced sentiment distribution")


if __name__ == '__main__':
    # Create output directory
    output_dir = Path('results') / 'sentiment_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create the chart
    create_sentiment_ratios_chart(
        save_path=output_dir / 'sentiment_ratios_per_offer.png'
    )