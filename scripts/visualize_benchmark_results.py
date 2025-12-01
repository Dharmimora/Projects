#!/usr/bin/env python3
"""
Visualization script for benchmark results.
Creates performance comparison charts for all technologies.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_benchmark_results(file_path: str) -> dict:
    """Load benchmark results from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_performance_comparison_chart(results: dict, output_dir: str):
    """Create performance comparison bar chart."""
    # Extract data
    technologies = []
    rewards = []
    queue_lengths = []
    
    for tech_name, data in results['results'].items():
        technologies.append(data['name'])
        rewards.append(data['avg_reward'])
        queue_lengths.append(data['avg_queue_length'])
    
    # Sort by reward (better rewards are less negative)
    sorted_indices = np.argsort(rewards)
    technologies = [technologies[i] for i in sorted_indices]
    rewards = [rewards[i] for i in sorted_indices]
    queue_lengths = [queue_lengths[i] for i in sorted_indices]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # Plot 1: Average Reward
    bars1 = ax1.barh(technologies, rewards, color='skyblue')
    ax1.set_xlabel('Average Reward')
    ax1.set_title('Performance Comparison: Average Reward')
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars1, rewards)):
        ax1.text(value + 1, i, f'{value:.1f}', va='center', ha='left')
    
    # Plot 2: Average Queue Length
    bars2 = ax2.barh(technologies, queue_lengths, color='lightcoral')
    ax2.set_xlabel('Average Queue Length')
    ax2.set_title('Performance Comparison: Average Queue Length')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars2, queue_lengths)):
        ax2.text(value + 0.01, i, f'{value:.2f}', va='center', ha='left')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_reward_improvement_chart(results: dict, output_dir: str):
    """Create reward improvement over baseline chart."""
    baseline_reward = None
    for tech_name, data in results['results'].items():
        if data['name'] == 'Fuzzy Logic':
            baseline_reward = data['avg_reward']
            break
    
    if baseline_reward is None:
        return
    
    # Calculate improvements
    technologies = []
    improvements = []
    
    for tech_name, data in results['results'].items():
        if data['name'] != 'Fuzzy Logic':  # Skip baseline
            technologies.append(data['name'])
            improvement = ((data['avg_reward'] - baseline_reward) / abs(baseline_reward)) * 100
            improvements.append(improvement)
    
    # Sort by improvement
    sorted_indices = np.argsort(improvements)[::-1]  # Descending order
    technologies = [technologies[i] for i in sorted_indices]
    improvements = [improvements[i] for i in sorted_indices]
    
    # Create chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(technologies, improvements, color=['green' if x > 0 else 'red' for x in improvements])
    plt.xlabel('Technology')
    plt.ylabel('Reward Improvement (%)')
    plt.title('Reward Improvement Over Fuzzy Logic Baseline')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, improvements)):
        plt.text(i, value + (1 if value > 0 else -1), f'{value:.1f}%', 
                ha='center', va='bottom' if value > 0 else 'top')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/reward_improvement.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_detailed_comparison_table(results: dict, output_dir: str):
    """Create detailed comparison table as image."""
    # Extract data
    data = []
    for tech_name, result in results['results'].items():
        data.append([
            result['name'],
            f"{result['avg_reward']:.2f}",
            f"{result['avg_queue_length']:.2f}",
            f"{result['avg_episode_length']:.1f}",
            f"{result['std_wait_time']:.2f}"
        ])
    
    # Sort by reward
    data.sort(key=lambda x: float(x[1]))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(cellText=data,
                     colLabels=['Technology', 'Avg Reward', 'Queue Length', 'Episode Length', 'Wait Time Std'],
                     cellLoc='center',
                     loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Style the table
    for i in range(len(data) + 1):
        for j in range(5):
            if i == 0:  # Header
                table[(i, j)].set_facecolor('#4CAF50')
                table[(i, j)].set_text_props(weight='bold', color='white')
            else:
                # Alternate row colors
                color = '#f0f0f0' if i % 2 == 0 else 'white'
                table[(i, j)].set_facecolor(color)
    
    plt.title('Detailed Performance Comparison', fontsize=16, pad=20)
    plt.savefig(f'{output_dir}/detailed_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_summary_report(results: dict, output_dir: str):
    """Generate a summary report."""
    best_by_reward = results['best_performer']['by_reward']
    best_by_wait = results['best_performer']['by_wait_time']
    
    # Find baseline performance
    baseline_reward = None
    baseline_name = None
    for tech_name, data in results['results'].items():
        if data['name'] == 'Fuzzy Logic':
            baseline_reward = data['avg_reward']
            baseline_name = data['name']
            break
    
    # Calculate improvement
    improvement = 0
    if baseline_reward:
        improvement = ((best_by_reward['reward'] - baseline_reward) / abs(baseline_reward)) * 100
    
    report = f"""
BENCHMARK RESULTS SUMMARY
=========================

Best Performer by Reward:
  Technology: {best_by_reward['name']}
  Reward: {best_by_reward['reward']:.2f}
  Wait Time: {best_by_reward['wait_time']:.2f}s

Baseline Performance ({baseline_name}):
  Reward: {baseline_reward:.2f} (if available)

Improvement over Baseline:
  {improvement:.1f}% improvement in reward

Total Technologies Tested: {len(results['results'])}

Test Configuration:
  Episodes per Technology: {results['num_test_episodes']}
  Benchmark Date: {results['benchmark_date']}
"""
    
    with open(f'{output_dir}/benchmark_summary.txt', 'w') as f:
        f.write(report)
    
    print(report)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize benchmark results")
    parser.add_argument('--input', type=str, default='runs/novel_tech_training_gpu/benchmark_results_fixed.json',
                       help='Input benchmark results file')
    parser.add_argument('--output', type=str, default='runs/novel_tech_training_gpu',
                       help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    # Load results
    results = load_benchmark_results(args.input)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    create_performance_comparison_chart(results, str(output_dir))
    create_reward_improvement_chart(results, str(output_dir))
    create_detailed_comparison_table(results, str(output_dir))
    generate_summary_report(results, str(output_dir))
    
    print(f"Visualizations saved to {output_dir}")

if __name__ == '__main__':
    main()