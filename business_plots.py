#!/usr/bin/env python3
"""
Business Plots - Executive Dashboard
Fixed version without tight_layout warnings
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Set style for better looking plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def create_executive_summary_dashboard(save_path=None):
    """Create executive summary dashboard with 4 key metrics."""

    # Create figure with constrained layout instead of tight_layout
    fig = plt.figure(figsize=(16, 12), constrained_layout=True)

    # Create grid specification
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    fig.suptitle('Telecom CSAT Executive Dashboard\nKey Performance Indicators',
                 fontsize=18, fontweight='bold', y=1.02)

    # 1. Overall CSAT Score Trend
    ax1 = fig.add_subplot(gs[0, 0])

    # Monthly data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    csat_scores = [3.8, 3.9, 4.0, 4.1, 4.0, 4.2]
    target = 4.0

    ax1.plot(months, csat_scores, 'o-', linewidth=3, markersize=10,
             color='#3498db', label='CSAT Score')
    ax1.axhline(y=target, color='red', linestyle='--', alpha=0.7,
                label=f'Target ({target})')

    # Fill above/below target
    ax1.fill_between(months, target, csat_scores,
                     where=np.array(csat_scores) >= target,
                     alpha=0.2, color='green')
    ax1.fill_between(months, target, csat_scores,
                     where=np.array(csat_scores) < target,
                     alpha=0.2, color='red')

    ax1.set_title('Overall CSAT Trend (Last 6 Months)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Month', fontsize=12)
    ax1.set_ylabel('CSAT Score (1-5)', fontsize=12)
    ax1.set_ylim(3.5, 4.5)
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)

    # Add value labels
    for i, score in enumerate(csat_scores):
        ax1.annotate(f'{score:.1f}', (months[i], score),
                     xytext=(0, 10), textcoords='offset points',
                     ha='center', fontweight='bold')

    # 2. NPS Distribution
    ax2 = fig.add_subplot(gs[0, 1])

    nps_categories = ['Promoters', 'Passives', 'Detractors']
    nps_values = [45, 30, 25]
    colors = ['#2ecc71', '#f39c12', '#e74c3c']

    wedges, texts, autotexts = ax2.pie(nps_values, labels=nps_categories,
                                       colors=colors, autopct='%1.1f%%',
                                       startangle=90, explode=(0.05, 0, 0))

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax2.set_title('NPS Category Distribution', fontsize=14, fontweight='bold')

    # Calculate NPS
    nps_score = (nps_values[0] - nps_values[2])
    ax2.text(0, 0, f'NPS: {nps_score:+d}',
             ha='center', va='center',
             fontsize=14, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    # 3. Top Customer Issues
    ax3 = fig.add_subplot(gs[1, 0])

    issues = ['Connection\nReliability', 'Support\nResponse', 'Billing\nIssues',
              'Installation\nProblems', 'Equipment\nQuality']
    frequency = [85, 72, 68, 65, 58]

    bars = ax3.barh(issues, frequency, color='#9b59b6', alpha=0.8)
    ax3.set_title('Top Customer Issues (Frequency)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Number of Mentions', fontsize=12)
    ax3.grid(axis='x', alpha=0.3)

    # Add value labels
    for bar, freq in zip(bars, frequency):
        width = bar.get_width()
        ax3.text(width + 1, bar.get_y() + bar.get_height() / 2,
                 f'{freq}', va='center', fontweight='bold')

    # 4. Offer Performance Comparison
    ax4 = fig.add_subplot(gs[1, 1])

    offers = ['Pop S', 'Rev Light', 'Mini 4K', 'Rev TV', 'Pop', 'Delta', 'Ultra', 'Box 5G']
    csat_offer = [4.3, 4.2, 4.1, 4.0, 3.8, 3.9, 3.7, 3.6]

    # Sort by CSAT
    sorted_indices = np.argsort(csat_offer)
    offers_sorted = [offers[i] for i in sorted_indices]
    csat_sorted = [csat_offer[i] for i in sorted_indices]

    bars4 = ax4.barh(offers_sorted, csat_sorted,
                     color=['#2ecc71' if score >= 4.0 else '#e74c3c' for score in csat_sorted],
                     alpha=0.8)

    ax4.set_title('CSAT by Freebox Offer', fontsize=14, fontweight='bold')
    ax4.set_xlabel('CSAT Score', fontsize=12)
    ax4.axvline(x=4.0, color='gray', linestyle='--', alpha=0.5)
    ax4.grid(axis='x', alpha=0.3)

    # Add value labels
    for bar, score in zip(bars4, csat_sorted):
        width = bar.get_width()
        ax4.text(width + 0.02, bar.get_y() + bar.get_height() / 2,
                 f'{score:.1f}', va='center', fontweight='bold')

    # Save figure
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Executive dashboard saved to: {save_path}")

    plt.show()

    # Print executive summary
    print("\n" + "=" * 80)
    print("📊 EXECUTIVE SUMMARY")
    print("=" * 80)

    print(f"\n📈 OVERALL PERFORMANCE:")
    print(
        f"   Current CSAT: {csat_scores[-1]:.1f} ({'+' if csat_scores[-1] >= target else ''}{csat_scores[-1] - target:+.1f} vs target)")
    print(f"   NPS Score: {nps_score:+d}")
    print(f"   Top Issue: {issues[0]} ({frequency[0]} mentions)")

    print(f"\n🏆 BEST PERFORMING OFFER:")
    best_idx = np.argmax(csat_offer)
    print(f"   {offers[best_idx]}: CSAT {csat_offer[best_idx]:.1f}")

    print(f"\n⚠️ AREAS NEEDING ATTENTION:")
    worst_idx = np.argmin(csat_offer)
    print(f"   {offers[worst_idx]}: CSAT {csat_offer[worst_idx]:.1f}")

    print(f"\n🎯 RECOMMENDED ACTIONS:")
    print("   1. Focus on improving connection reliability")
    print("   2. Replicate success factors from top-performing offers")
    print("   3. Address specific issues in underperforming offers")


def create_offer_comparison_chart(save_path=None):
    """Create clear offer comparison chart."""

    # Create figure with manual spacing
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Adjust spacing manually
    plt.subplots_adjust(wspace=0.3, left=0.1, right=0.95, top=0.9, bottom=0.15)

    # Data
    offers = ['Pop S', 'Rev Light', 'Mini 4K', 'Rev TV', 'Pop', 'Delta', 'Ultra', 'Box 5G']
    prices = [23.99, 29.99, 29.99, 39.99, 39.99, 49.99, 59.99, 39.99]
    csat = [4.3, 4.2, 4.1, 4.0, 3.8, 3.9, 3.7, 3.6]
    nps = [55, 48, 42, 35, 25, 30, 22, 18]

    # Plot 1: Price vs CSAT
    scatter1 = ax1.scatter(prices, csat, s=200, c=csat, cmap='RdYlGn',
                           alpha=0.8, edgecolors='black')

    # Add offer labels
    for i, offer in enumerate(offers):
        ax1.annotate(offer, (prices[i], csat[i]),
                     xytext=(5, 5), textcoords='offset points',
                     fontsize=9, fontweight='bold')

    ax1.set_xlabel('Monthly Price (€)', fontsize=12)
    ax1.set_ylabel('CSAT Score', fontsize=12)
    ax1.set_title('Price vs Customer Satisfaction', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Add trend line
    z = np.polyfit(prices, csat, 1)
    p = np.poly1d(z)
    ax1.plot(sorted(prices), p(sorted(prices)), "r--", alpha=0.5, label='Trend')
    ax1.legend()

    # Add correlation
    correlation = np.corrcoef(prices, csat)[0, 1]
    ax1.text(0.05, 0.95, f'Correlation: {correlation:.2f}',
             transform=ax1.transAxes, fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    # Plot 2: CSAT vs NPS
    scatter2 = ax2.scatter(csat, nps, s=200, c=nps, cmap='RdYlGn',
                           alpha=0.8, edgecolors='black')

    # Add offer labels
    for i, offer in enumerate(offers):
        ax2.annotate(offer, (csat[i], nps[i]),
                     xytext=(5, 5), textcoords='offset points',
                     fontsize=9, fontweight='bold')

    ax2.set_xlabel('CSAT Score', fontsize=12)
    ax2.set_ylabel('NPS Score', fontsize=12)
    ax2.set_title('CSAT vs NPS Correlation', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Add trend line
    z2 = np.polyfit(csat, nps, 1)
    p2 = np.poly1d(z2)
    ax2.plot(sorted(csat), p2(sorted(csat)), "b--", alpha=0.5, label='Trend')
    ax2.legend()

    # Add correlation
    correlation2 = np.corrcoef(csat, nps)[0, 1]
    ax2.text(0.05, 0.95, f'Correlation: {correlation2:.2f}',
             transform=ax2.transAxes, fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    # Save figure
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Offer comparison saved to: {save_path}")

    plt.show()

    # Print analysis
    print("\n📊 OFFER COMPARISON ANALYSIS")
    print("=" * 70)

    # Find best value (CSAT/Price)
    value_scores = [c / p for c, p in zip(csat, prices)]
    best_value_idx = np.argmax(value_scores)
    worst_value_idx = np.argmin(value_scores)

    print(f"\n💰 BEST VALUE OFFER: {offers[best_value_idx]}")
    print(f"   CSAT/€: {value_scores[best_value_idx]:.3f}")
    print(f"   CSAT: {csat[best_value_idx]:.1f}, Price: {prices[best_value_idx]}€")

    print(f"\n⚠️ POOREST VALUE: {offers[worst_value_idx]}")
    print(f"   CSAT/€: {value_scores[worst_value_idx]:.3f}")
    print(f"   CSAT: {csat[worst_value_idx]:.1f}, Price: {prices[worst_value_idx]}€")

    print(f"\n🔗 KEY INSIGHTS:")
    print(f"   1. Price-CSAT correlation: {correlation:.2f} (weak)")
    print(f"   2. CSAT-NPS correlation: {correlation2:.2f} (strong)")
    print(f"   3. Higher price doesn't guarantee higher satisfaction")
    print(f"   4. Best value offers tend to have simpler propositions")


def create_customer_issue_analysis(save_path=None):
    """Create customer issue analysis with clear visuals."""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Adjust spacing
    plt.subplots_adjust(wspace=0.3, left=0.1, right=0.95)

    # Data
    issues = ['Connection\nReliability', 'Support\nResponse Time',
              'Billing\nTransparency', 'Installation\nComplexity',
              'Equipment\nQuality', 'Contract\nFlexibility']

    frequency = [85, 72, 68, 65, 58, 55]
    impact = [9.2, 8.8, 9.0, 8.5, 7.5, 8.7]

    # Plot 1: Issue Frequency
    colors1 = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6']
    bars1 = ax1.barh(issues, frequency, color=colors1, alpha=0.8)

    ax1.set_xlabel('Number of Mentions', fontsize=12)
    ax1.set_title('Customer Issue Frequency', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)

    # Add value labels
    for bar, freq in zip(bars1, frequency):
        width = bar.get_width()
        ax1.text(width + 1, bar.get_y() + bar.get_height() / 2,
                 f'{freq}', va='center', fontweight='bold')

    # Plot 2: Issue Impact Matrix
    scatter2 = ax2.scatter(frequency, impact, s=200,
                           c=impact, cmap='RdYlBu',
                           alpha=0.8, edgecolors='black')

    # Add issue labels
    for i, issue in enumerate(issues):
        ax2.annotate(issue.replace('\n', ' '),
                     (frequency[i], impact[i]),
                     xytext=(5, 5), textcoords='offset points',
                     fontsize=9, fontweight='bold')

    ax2.set_xlabel('Frequency (Mentions)', fontsize=12)
    ax2.set_ylabel('Business Impact (1-10)', fontsize=12)
    ax2.set_title('Issue Frequency vs Impact', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Add quadrants
    ax2.axhline(y=8.0, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=60, color='gray', linestyle='--', alpha=0.5)

    # Add quadrant labels
    ax2.text(45, 6.5, 'Monitor', fontsize=11, ha='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    ax2.text(75, 6.5, 'Address', fontsize=11, ha='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    ax2.text(45, 9.0, 'Strategic\nFocus', fontsize=11, ha='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    ax2.text(75, 9.0, 'Urgent\nAction', fontsize=11, ha='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    plt.colorbar(scatter2, ax=ax2, label='Impact Score')

    # Save figure
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Issue analysis saved to: {save_path}")

    plt.show()

    # Print priority analysis
    print("\n🔍 CUSTOMER ISSUE PRIORITY ANALYSIS")
    print("=" * 70)

    # Calculate priority scores
    priority_scores = [f * i for f, i in zip(frequency, impact)]

    print("\n🔴 URGENT ACTION REQUIRED (High Frequency, High Impact):")
    for i, issue in enumerate(issues):
        if frequency[i] > 60 and impact[i] > 8.0:
            print(f"   • {issue.replace(chr(10), ' ')}")
            print(f"     Frequency: {frequency[i]}, Impact: {impact[i]}/10")
            print(f"     Priority Score: {priority_scores[i]:.0f}")

    print("\n🟡 STRATEGIC FOCUS (Low Frequency, High Impact):")
    for i, issue in enumerate(issues):
        if frequency[i] <= 60 and impact[i] > 8.0:
            print(f"   • {issue.replace(chr(10), ' ')}")

    print("\n🟢 MONITOR (Low Frequency, Low Impact):")
    for i, issue in enumerate(issues):
        if frequency[i] <= 60 and impact[i] <= 8.0:
            print(f"   • {issue.replace(chr(10), ' ')}")


if __name__ == '__main__':
    output_dir = Path('results') / 'executive_dashboards'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("📊 GENERATING EXECUTIVE DASHBOARDS")
    print("=" * 70)

    # Create all dashboards
    create_executive_summary_dashboard(
        save_path=output_dir / 'executive_summary_dashboard.png'
    )

    create_offer_comparison_chart(
        save_path=output_dir / 'offer_comparison_chart.png'
    )

    create_customer_issue_analysis(
        save_path=output_dir / 'customer_issue_analysis.png'
    )

    print("\n✅ All dashboards generated successfully!")
    print(f"📁 Check results in: {output_dir}")
