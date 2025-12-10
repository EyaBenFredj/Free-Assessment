#!/usr/bin/env python3
"""
Simplified Offer Analysis - No tight_layout warnings
Clear, focused offer performance analysis
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path


def create_simple_offer_comparison(save_path=None):
    """Create simple offer comparison chart."""

    # Data
    offers = [
        'Freebox Pop S (23.99€)',
        'Freebox Révolution Light (29.99€)',
        'Freebox mini 4K (29.99€)',
        'Freebox Révolution TV (39.99€)',
        'Freebox Pop (39.99€)',
        'Freebox Delta (49.99€)',
        'Freebox Ultra (59.99€)',
        'Box 5G (39.99€)'
    ]

    csat_scores = [4.3, 4.2, 4.1, 4.0, 3.8, 3.9, 3.7, 3.6]
    nps_scores = [55, 48, 42, 35, 25, 30, 22, 18]

    # Create figure with manual layout
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # Manual spacing
    plt.subplots_adjust(wspace=0.35, left=0.08, right=0.95, top=0.9, bottom=0.15)

    # Plot 1: CSAT Scores
    bars1 = ax1.barh(offers, csat_scores,
                     color=['#2ecc71' if score >= 4.0 else '#e74c3c' for score in csat_scores],
                     alpha=0.8)

    ax1.set_xlabel('CSAT Score (1-5)', fontsize=12)
    ax1.set_title('Customer Satisfaction by Offer', fontsize=14, fontweight='bold')
    ax1.axvline(x=4.0, color='gray', linestyle='--', alpha=0.5, label='Target (4.0)')
    ax1.legend()
    ax1.grid(axis='x', alpha=0.3)

    # Add value labels
    for bar, score in zip(bars1, csat_scores):
        ax1.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                 f'{score:.1f}', va='center', fontweight='bold',
                 color='white' if score < 4.0 else 'black')

    # Plot 2: NPS Scores
    colors2 = []
    for nps in nps_scores:
        if nps >= 50:
            colors2.append('#2ecc71')  # Excellent
        elif nps >= 30:
            colors2.append('#f39c12')  # Good
        else:
            colors2.append('#e74c3c')  # Needs improvement

    # Shorten offer names for x-axis
    short_offers = ['Pop S', 'Rev Light', 'Mini 4K', 'Rev TV', 'Pop', 'Delta', 'Ultra', 'Box 5G']

    bars2 = ax2.bar(short_offers, nps_scores, color=colors2, alpha=0.8)
    ax2.set_xlabel('Offer Type', fontsize=12)
    ax2.set_ylabel('NPS Score (-100 to +100)', fontsize=12)
    ax2.set_title('Net Promoter Score by Offer', fontsize=14, fontweight='bold')
    ax2.axhline(y=30, color='gray', linestyle='--', alpha=0.5, label='Industry Average')
    ax2.axhline(y=50, color='green', linestyle='--', alpha=0.5, label='Excellent')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar, score in zip(bars2, nps_scores):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height + 1,
                 f'{score:+d}', ha='center', va='bottom',
                 fontweight='bold', fontsize=10)

    # Add overall analysis
    fig.text(0.5, 0.02,
             'Best Performing: Freebox Pop S | Needs Improvement: Box 5G',
             ha='center', fontsize=11, style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3))

    # Save figure
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Simple offer comparison saved to: {save_path}")

    plt.show()

    # Print summary
    print("\n📊 SIMPLE OFFER COMPARISON")
    print("=" * 70)

    best_idx = np.argmax(csat_scores)
    worst_idx = np.argmin(csat_scores)

    print(f"\n🏆 BEST PERFORMER: {offers[best_idx]}")
    print(f"   CSAT: {csat_scores[best_idx]:.1f} | NPS: {nps_scores[best_idx]:+d}")

    print(f"\n⚠️ NEEDS IMPROVEMENT: {offers[worst_idx]}")
    print(f"   CSAT: {csat_scores[worst_idx]:.1f} | NPS: {nps_scores[worst_idx]:+d}")

    print(f"\n📈 AVERAGE PERFORMANCE:")
    print(f"   Average CSAT: {np.mean(csat_scores):.2f}")
    print(f"   Average NPS: {np.mean(nps_scores):+.1f}")
    print(f"   Offers above CSAT target: {sum(1 for s in csat_scores if s >= 4.0)}/{len(csat_scores)}")


def create_price_performance_chart(save_path=None):
    """Create price vs performance analysis."""

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Data
    offers_short = ['Pop S', 'Rev Light', 'Mini 4K', 'Rev TV', 'Pop', 'Delta', 'Ultra', 'Box 5G']
    prices = [23.99, 29.99, 29.99, 39.99, 39.99, 49.99, 59.99, 39.99]
    csat_scores = [4.3, 4.2, 4.1, 4.0, 3.8, 3.9, 3.7, 3.6]

    # Create scatter plot
    scatter = ax.scatter(prices, csat_scores, s=300,
                         c=csat_scores, cmap='RdYlGn',
                         alpha=0.8, edgecolors='black')

    # Add offer labels
    for i, offer in enumerate(offers_short):
        ax.annotate(offer, (prices[i], csat_scores[i]),
                    xytext=(10, 5), textcoords='offset points',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

    ax.set_xlabel('Monthly Price (€)', fontsize=12)
    ax.set_ylabel('CSAT Score (1-5)', fontsize=12)
    ax.set_title('Price vs Customer Satisfaction Analysis', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add value-for-money zones
    ax.axhline(y=4.0, color='gray', linestyle='--', alpha=0.5, label='CSAT Target')
    ax.axvline(x=35, color='gray', linestyle='--', alpha=0.5, label='Price Midpoint')

    # Add zone labels
    ax.text(25, 4.25, 'High Value\n(Good CSAT, Low Price)',
            ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.5))

    ax.text(55, 4.25, 'Premium\n(Good CSAT, High Price)',
            ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.5))

    ax.text(25, 3.65, 'Underperforming\n(Low CSAT, Low Price)',
            ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcoral', alpha=0.5))

    ax.text(55, 3.65, 'Overpriced\n(Low CSAT, High Price)',
            ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='gold', alpha=0.5))

    ax.legend()
    plt.colorbar(scatter, ax=ax, label='CSAT Score')

    # Save figure
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Price performance chart saved to: {save_path}")

    plt.show()

    # Print analysis
    print("\n💰 PRICE VS PERFORMANCE ANALYSIS")
    print("=" * 70)

    # Calculate value score (CSAT/Price)
    value_scores = [csat / (price / 10) for csat, price in zip(csat_scores, prices)]

    print(f"\n🎯 VALUE FOR MONEY RANKING:")
    for i in np.argsort(value_scores)[::-1]:  # Sort descending
        print(f"   {i + 1}. {offers_short[i]}: CSAT {csat_scores[i]:.1f} / {prices[i]}€ = {value_scores[i]:.3f}")

    print(f"\n🔍 KEY INSIGHTS:")
    print("   1. Freebox Pop S offers best value (high CSAT, low price)")
    print("   2. Box 5G offers poor value despite mid-range price")
    print("   3. Premium offers (Ultra, Delta) need CSAT improvement")
    print("   4. Higher price doesn't correlate with higher satisfaction")


if __name__ == '__main__':
    output_dir = Path('results') / 'offer_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("📊 GENERATING SIMPLIFIED OFFER ANALYSIS")
    print("=" * 70)

    create_simple_offer_comparison(
        save_path=output_dir / 'simple_offer_comparison.png'
    )

    create_price_performance_chart(
        save_path=output_dir / 'price_performance_chart.png'
    )

    print("\n✅ Simplified offer analysis completed!")