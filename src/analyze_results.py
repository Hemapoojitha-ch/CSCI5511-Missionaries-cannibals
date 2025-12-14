"""
Analysis and visualization of experiment results.
Creates plots and tables for the report.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_results(filepath):
    """Load experiment results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_comparison_table(results, output_path=None):
    """
    Create a comparison table of algorithm performance.
    
    Args:
        results: List of result dictionaries
        output_path: Optional path to save table
        
    Returns:
        DataFrame with comparison
    """
    df = pd.DataFrame(results)
    
    # Create algorithm key
    df['algo_key'] = df.apply(
        lambda r: f"{r['algorithm']}_{r['heuristic']}" if r['algorithm'] in ['astar', 'idastar'] else r['algorithm'],
        axis=1
    )
    
    # Group and aggregate
    summary = df.groupby('algo_key').agg({
        'success': ['sum', 'count'],
        'time': ['mean', 'std', 'min', 'max'],
        'nodes_expanded': ['mean', 'std'],
        'solution_length': 'mean'
    }).round(4)
    
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary['success_rate'] = (summary['success_sum'] / summary['success_count'] * 100).round(1)
    
    print("\n" + "="*80)
    print("ALGORITHM COMPARISON TABLE")
    print("="*80)
    print(summary)
    
    if output_path:
        summary.to_csv(output_path)
        print(f"\nTable saved to {output_path}")
    
    return summary


def plot_nodes_vs_n(results, output_path=None):
    """
    Plot nodes expanded vs problem size (n).
    
    Args:
        results: List of result dictionaries
        output_path: Optional path to save figure
    """
    df = pd.DataFrame(results)
    df = df[df['success'] == True]  # Only successful runs
    
    # Create algorithm key
    df['algo_key'] = df.apply(
        lambda r: f"{r['algorithm']}-{r['heuristic']}" if r['algorithm'] in ['astar', 'idastar'] else r['algorithm'],
        axis=1
    )
    
    plt.figure(figsize=(12, 6))
    
    for algo in df['algo_key'].unique():
        algo_data = df[df['algo_key'] == algo]
        
        # Group by n and b
        for b in sorted(algo_data['b'].unique()):
            b_data = algo_data[algo_data['b'] == b]
            grouped = b_data.groupby('n')['nodes_expanded'].mean()
            
            plt.plot(grouped.index, grouped.values, marker='o', 
                    label=f"{algo} (b={b})", linewidth=2)
    
    plt.xlabel('Problem Size (n)', fontsize=12)
    plt.ylabel('Average Nodes Expanded', fontsize=12)
    plt.title('Nodes Expanded vs Problem Size', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    plt.show()


def plot_time_vs_n(results, output_path=None):
    """
    Plot execution time vs problem size (n).
    
    Args:
        results: List of result dictionaries
        output_path: Optional path to save figure
    """
    df = pd.DataFrame(results)
    df = df[df['success'] == True]
    
    df['algo_key'] = df.apply(
        lambda r: f"{r['algorithm']}-{r['heuristic']}" if r['algorithm'] in ['astar', 'idastar'] else r['algorithm'],
        axis=1
    )
    
    plt.figure(figsize=(12, 6))
    
    for algo in df['algo_key'].unique():
        algo_data = df[df['algo_key'] == algo]
        
        for b in sorted(algo_data['b'].unique()):
            b_data = algo_data[algo_data['b'] == b]
            grouped = b_data.groupby('n')['time'].mean()
            
            plt.plot(grouped.index, grouped.values, marker='s', 
                    label=f"{algo} (b={b})", linewidth=2)
    
    plt.xlabel('Problem Size (n)', fontsize=12)
    plt.ylabel('Average Time (seconds)', fontsize=12)
    plt.title('Execution Time vs Problem Size', fontsize=14, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    plt.show()


def plot_heuristic_comparison(results, output_path=None):
    """
    Compare different heuristics for A*.
    
    Args:
        results: List of result dictionaries
        output_path: Optional path to save figure
    """
    df = pd.DataFrame(results)
    df = df[(df['algorithm'] == 'astar') & (df['success'] == True)]
    
    if df.empty:
        print("No A* results to compare")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Nodes expanded
    heuristic_data = df.groupby('heuristic')['nodes_expanded'].mean().sort_values()
    ax1.bar(range(len(heuristic_data)), heuristic_data.values, color='steelblue')
    ax1.set_xticks(range(len(heuristic_data)))
    ax1.set_xticklabels(heuristic_data.index)
    ax1.set_ylabel('Average Nodes Expanded', fontsize=12)
    ax1.set_title('Heuristic Performance: Nodes Expanded', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Time
    heuristic_time = df.groupby('heuristic')['time'].mean().sort_values()
    ax2.bar(range(len(heuristic_time)), heuristic_time.values, color='coral')
    ax2.set_xticks(range(len(heuristic_time)))
    ax2.set_xticklabels(heuristic_time.index)
    ax2.set_ylabel('Average Time (seconds)', fontsize=12)
    ax2.set_title('Heuristic Performance: Time', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    plt.show()


def plot_algorithm_comparison_bar(results, output_path=None):
    """
    Bar chart comparing algorithms across multiple metrics.
    
    Args:
        results: List of result dictionaries
        output_path: Optional path to save figure
    """
    df = pd.DataFrame(results)
    df = df[df['success'] == True]
    
    df['algo_key'] = df.apply(
        lambda r: f"{r['algorithm']}-{r['heuristic']}" if r['algorithm'] in ['astar', 'idastar'] else r['algorithm'],
        axis=1
    )
    
    # Aggregate by algorithm
    agg_data = df.groupby('algo_key').agg({
        'nodes_expanded': 'mean',
        'time': 'mean',
        'solution_length': 'mean'
    }).round(2)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Nodes expanded
    agg_data['nodes_expanded'].plot(kind='bar', ax=axes[0], color='steelblue')
    axes[0].set_ylabel('Avg Nodes Expanded', fontsize=11)
    axes[0].set_title('Nodes Expanded', fontsize=12, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Time
    agg_data['time'].plot(kind='bar', ax=axes[1], color='coral')
    axes[1].set_ylabel('Avg Time (seconds)', fontsize=11)
    axes[1].set_title('Execution Time', fontsize=12, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Solution length
    agg_data['solution_length'].plot(kind='bar', ax=axes[2], color='seagreen')
    axes[2].set_ylabel('Avg Solution Length', fontsize=11)
    axes[2].set_title('Solution Length', fontsize=12, fontweight='bold')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    plt.show()


def create_latex_table(results, output_path=None):
    """
    Create a LaTeX-formatted table for the report.
    
    Args:
        results: List of result dictionaries
        output_path: Optional path to save LaTeX code
    """
    df = pd.DataFrame(results)
    df['algo_key'] = df.apply(
        lambda r: f"{r['algorithm']}-{r['heuristic']}" if r['algorithm'] in ['astar', 'idastar'] else r['algorithm'],
        axis=1
    )
    
    summary = df.groupby('algo_key').agg({
        'success': lambda x: f"{sum(x)}/{len(x)}",
        'time': lambda x: f"{x.mean():.4f}",
        'nodes_expanded': lambda x: f"{x.mean():.1f}",
        'solution_length': lambda x: f"{x.mean():.1f}"
    })
    
    latex = summary.to_latex(
        column_format='l|cccc',
        caption='Algorithm Performance Comparison',
        label='tab:results'
    )
    
    print("\nLaTeX Table:")
    print(latex)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(latex)
        print(f"LaTeX table saved to {output_path}")
    
    return latex


if __name__ == '__main__':
    # Find most recent results file
    data_dir = Path('../data')
    
    if not data_dir.exists():
        print("No data directory found. Run experiments first.")
        exit(1)
    
    json_files = list(data_dir.glob('results_*.json'))
    
    if not json_files:
        print("No results files found. Run experiments first.")
        exit(1)
    
    # Load most recent
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading results from: {latest_file}")
    
    results = load_results(latest_file)
    
    # Create output directory for plots
    plots_dir = data_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    # Generate all analyses
    create_comparison_table(results, plots_dir / 'comparison_table.csv')
    plot_nodes_vs_n(results, plots_dir / 'nodes_vs_n.png')
    plot_time_vs_n(results, plots_dir / 'time_vs_n.png')
    plot_heuristic_comparison(results, plots_dir / 'heuristic_comparison.png')
    plot_algorithm_comparison_bar(results, plots_dir / 'algorithm_comparison.png')
    create_latex_table(results, plots_dir / 'results_table.tex')
    
    print(f"\n{'='*70}")
    print("Analysis complete! Check the plots directory for visualizations.")
    print(f"{'='*70}")