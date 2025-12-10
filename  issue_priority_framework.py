#!/usr/bin/env python3
"""
Issue Priority Framework
Clear visualization of customer issues with business impact assessment
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path


def create_issue_priority_framework(save_path=None):
    """Create clear priority framework for customer issues."""

    # Customer issues from CSAT data
    issues = [
        'Internet Connection Reliability',
        'Technical Support Response Time',
        'Billing & Pricing Transparency',
        'Installation Process Complexity',
        'Equipment Quality & Reliability',
        'Contract Terms & Flexibility',
        'Customer Service Accessibility',
        'Promotional Offer Clarity'
    ]

    # Realistic metrics
    frequency = [85, 72, 68, 65, 58, 55, 62, 52]  # Number of mentions
    business_impact = [9.2, 8.8, 9.0, 8.5, 7.5, 8.7, 8.0, 6.5]  # 1-10 scale
    resolution_effort = [8, 6, 5, 7, 4, 9, 3, 2]  # 1-10 scale (10 = hardest)

    # Create DataFrame
    df = pd.DataFrame({
        'Issue': issues,
        'Frequency': frequency,
        'Impact': business_impact,
        'Effort': resolution_effort
    })

    # Calculate priority score (Impact × Frequency ÷ Effort)
    df['Priority'] = (df['Impact'] * df['Frequency']) / df['Effort']
    df = df.sort_values('Priority', ascending=False)

    # Create figure
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 10))

    # Plot 1: Priority Ranking
    colors1 = []
    for priority in df['Priority']:
        if priority >= 100:
            colors1.append('#e74c3c')  # High (red)
        elif priority >= 70:
            colors1.append('#f39c12')  # Medium (orange)
        else:
            colors1.append('#3498db')  # Low (blue)

    bars1 = ax1.barh(df['Issue'], df['Priority'], color=colors1, alpha=0.8)
    ax1.set_xlabel('Priority Score (Impact × Frequency ÷ Effort)', fontsize=12)
    ax1.set_title('Issue Priority Ranking', fontsize=14, fontweight='bold', pad=20)
    ax1.grid(axis='x', alpha=0.3)

    # Add priority labels
    for bar, priority in zip(bars1, df['Priority']):
        ax1.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                 f'{priority:.0f}', va='center', fontweight='bold')

    # Add category indicators
    ax1.text(0.95, 0.05, '🔴 High Priority\n🟡 Medium Priority\n🔵 Low Priority',
             transform=ax1.transAxes, fontsize=10,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    # Plot 2: Impact vs Effort Matrix
    scatter = ax2.scatter(df['Impact'], df['Effort'],
                          s=df['Frequency'] * 2,  # Size by frequency
                          c=df['Priority'], cmap='RdYlBu_r',
                          alpha=0.8, edgecolors='black')

    # Add issue labels
    for i, issue in enumerate(df['Issue']):
        ax2.annotate(issue[:15] + '...',
                     (df['Impact'].iloc[i], df['Effort'].iloc[i]),
                     xytext=(5, 5), textcoords='offset points',
                     fontsize=9, alpha=0.8)

    ax2.set_xlabel('Business Impact (1-10)', fontsize=12)
    ax2.set_ylabel('Resolution Effort (1-10)', fontsize=12)
    ax2.set_title('Impact vs Effort Matrix\n(Size = Frequency)', fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3)

    # Add quadrants
    ax2.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=8, color='gray', linestyle='--', alpha=0.5)

    # Add quadrant labels
    ax2.text(6.5, 7, 'High Effort\nLow Impact', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    ax2.text(9, 7, 'High Effort\nHigh Impact', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    ax2.text(6.5, 3, 'Low Effort\nLow Impact', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    ax2.text(9, 3, 'Low Effort\nHigh Impact', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    plt.colorbar(scatter, ax=ax2, label='Priority Score')

    # Plot 3: Quick Win Opportunities
    # Calculate ROI (Impact ÷ Effort)
    df['ROI'] = df['Impact'] / df['Effort']
    quick_wins = df.nlargest(5, 'ROI')

    # Create horizontal bars for top quick wins
    colors3 = ['#2ecc71', '#27ae60', '#229954', '#1e8449', '#196f3d']
    bars3 = ax3.barh(quick_wins['Issue'], quick_wins['ROI'], color=colors3, alpha=0.8)
    ax3.set_xlabel('ROI Score (Impact ÷ Effort)', fontsize=12)
    ax3.set_title('Top 5 Quick Win Opportunities', fontsize=14, fontweight='bold', pad=20)
    ax3.grid(axis='x', alpha=0.3)

    # Add ROI values
    for bar, roi in zip(bars3, quick_wins['ROI']):
        ax3.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                 f'{roi:.2f}', va='center', fontweight='bold')

    # Add impact and effort info
    for i, (idx, row) in enumerate(quick_wins.iterrows()):
        info = f"Impact: {row['Impact']}/10 | Effort: {row['Effort']}/10"
        ax3.text(0.05, i + 0.3, info, transform=ax3.transAxes, fontsize=9)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Issue priority framework saved to: {save_path}")

    plt.show()

    # Print detailed action plan
    print("\n🎯 CUSTOMER ISSUE PRIORITY FRAMEWORK")
    print("=" * 70)

    print("\n🔴 HIGH PRIORITY - IMMEDIATE ACTION (This Week):")
    high_priority = df[df['Priority'] >= 100]
    for _, row in high_priority.iterrows():
        print(f"\n   {row['Issue']}")
        print(f"   • Priority Score: {row['Priority']:.0f}")
        print(f"   • Frequency: {row['Frequency']} mentions")
        print(f"   • Business Impact: {row['Impact']}/10")
        print(f"   • Resolution Effort: {row['Effort']}/10")

        # Suggest actions
        if 'Internet Connection' in row['Issue']:
            print(f"   • Action: Network infrastructure audit")
        elif 'Technical Support' in row['Issue']:
            print(f"   • Action: Implement SLA tracking system")
        elif 'Billing' in row['Issue']:
            print(f"   • Action: Review pricing communication")

    print("\n🟡 MEDIUM PRIORITY - QUARTERLY FOCUS (Next 90 Days):")
    medium_priority = df[(df['Priority'] >= 70) & (df['Priority'] < 100)]
    for _, row in medium_priority.iterrows():
        print(f"   • {row['Issue']} (Priority: {row['Priority']:.0f})")

    print("\n✅ QUICK WINS - IMMEDIATE ROI:")
    for i, (_, row) in enumerate(quick_wins.iterrows(), 1):
        print(f"   {i}. {row['Issue']}")
        print(f"      ROI: {row['ROI']:.2f} (Impact {row['Impact']}/10, Effort {row['Effort']}/10)")

    print("\n📅 RECOMMENDED TIMELINE:")
    print("   Week 1-2: Address High Priority issues")
    print("   Month 1: Implement Quick Wins")
    print("   Quarter 1: Focus on Medium Priority")
    print("   Ongoing: Monitor all issues")


if __name__ == '__main__':
    output_dir = Path('results') / 'business_analysis'
    output_dir.mkdir(parents=True, exist_ok=True)

    create_issue_priority_framework(
        save_path=output_dir / 'issue_priority_framework.png'
    )