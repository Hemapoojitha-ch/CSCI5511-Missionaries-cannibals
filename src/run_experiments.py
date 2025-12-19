import json
import time
import csv
from datetime import datetime
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parent  
PROJECT_ROOT = SCRIPT_DIR.parent   
DATA_DIR = PROJECT_ROOT / 'data' 

from state import State
from algorithms import ALGORITHMS
from heuristics import HEURISTICS


def run_single_experiment(n, b, algorithm, heuristic='h1', n_soldiers=0, timeout=60):
    """
    Run a single experiment instance.
    
    Args:
        n: Number of missionaries/cannibals
        b: Boat capacity
        algorithm: Algorithm name
        heuristic: Heuristic name (for A*/IDA*)
        n_soldiers: Number of soldiers
        timeout: Maximum time in seconds
        
    Returns:
        Dictionary with results
    """
    # Create initial state
    if n_soldiers > 0:
        initial_state = State(n, n, 'L', n, n, n_soldiers, n_soldiers)
    else:
        initial_state = State(n, n, 'L', n, n)
    
    # Get algorithm function
    algo_func = ALGORITHMS[algorithm]
    
    # Run with timeout protection
    start_time = time.time()
    try:
        if algorithm in ['astar', 'idastar']:
            heuristic_func = HEURISTICS[heuristic]
            result = algo_func(initial_state, b, heuristic_func)
        else:
            result = algo_func(initial_state, b)
        
        elapsed = time.time() - start_time
        
        # Check timeout
        if elapsed > timeout:
            return {
                'n': n,
                'b': b,
                's': n_soldiers,
                'algorithm': algorithm,
                'heuristic': heuristic if algorithm in ['astar', 'idastar'] else 'N/A',
                'success': False,
                'timeout': True,
                'time': elapsed,
                'nodes_expanded': result.stats.get('nodes_expanded', 0),
                'solution_length': 0,
                'path_cost': 0
            }
        
        return {
            'n': n,
            'b': b,
            's': n_soldiers,
            'algorithm': algorithm,
            'heuristic': heuristic if algorithm in ['astar', 'idastar'] else 'N/A',
            'success': result.success,
            'timeout': False,
            'time': result.stats.get('time_taken', elapsed),
            'nodes_expanded': result.stats.get('nodes_expanded', 0),
            'solution_length': len(result.path) - 1 if result.success else 0,
            'path_cost': result.stats.get('path_cost', 0),
            'max_queue_size': result.stats.get('max_queue_size', 0)
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'n': n,
            'b': b,
            's': n_soldiers,
            'algorithm': algorithm,
            'heuristic': heuristic if algorithm in ['astar', 'idastar'] else 'N/A',
            'success': False,
            'timeout': False,
            'error': str(e),
            'time': elapsed,
            'nodes_expanded': 0,
            'solution_length': 0,
            'path_cost': 0
        }


def run_experiment_grid(n_values, b_values, algorithms=None, heuristics=None, 
                       s_values=None, timeout=60, output_dir=None):
    """
    Run experiments across a grid of parameters.
    
    Args:
        n_values: List of n values to test
        b_values: List of boat capacities to test
        algorithms: List of algorithms (None = all)
        heuristics: List of heuristics for A*/IDA* (None = all)
        s_values: List of soldier counts (None = [0])
        timeout: Timeout per instance in seconds
        output_dir: Directory to save results
        
    Returns:
        List of result dictionaries
    """
    if output_dir is None:
        output_dir = DATA_DIR
    else:
        output_dir = Path(output_dir)

    if algorithms is None:
        algorithms = list(ALGORITHMS.keys())
    
    if heuristics is None:
        heuristics = list(HEURISTICS.keys())
    
    if s_values is None:
        s_values = [0]
    
    results = []
    total_experiments = len(n_values) * len(b_values) * len(s_values) * len(algorithms)
    
    astar_count = sum(1 for a in algorithms if a in ['astar', 'idastar'])
    if astar_count > 0:
        total_experiments = (len(algorithms) - astar_count) * len(n_values) * len(b_values) * len(s_values)
        total_experiments += astar_count * len(heuristics) * len(n_values) * len(b_values) * len(s_values)
    
    current = 0
    
    print(f"\nRUNNING EXPERIMENT GRID")
    print(f"{'-'*60}")
    print(f"Total experiments: {total_experiments}")
    print(f"n values: {n_values}")
    print(f"b values: {b_values}")
    print(f"s values: {s_values}")
    print(f"algorithms: {algorithms}")
    if astar_count > 0:
        print(f"heuristics: {heuristics}")
    print(f"{'-'*60}\n")
    
    for n in n_values:
        for b in b_values:
            for s in s_values:
                for algo in algorithms:
                    if algo in ['astar', 'idastar']:
                        # Testing with each heuristic
                        for heur in heuristics:
                            current += 1
                            print(f"[{current}/{total_experiments}] n={n}, b={b}, s={s}, {algo}, {heur}...", end=' ')
                            
                            result = run_single_experiment(n, b, algo, heur, s, timeout)
                            results.append(result)
                            
                            status = "Yes" if result['success'] else "No"
                            print(f"{status} ({result['time']:.3f}s, {result['nodes_expanded']} nodes)")
                    else:
                        # Non-heuristic algorithms
                        current += 1
                        print(f"[{current}/{total_experiments}] n={n}, b={b}, s={s}, {algo}...", end=' ')
                        
                        result = run_single_experiment(n, b, algo, n_soldiers=s, timeout=timeout)
                        results.append(result)
                        
                        status = "Yes" if result['success'] else "No"
                        print(f"{status} ({result['time']:.3f}s, {result['nodes_expanded']} nodes)")
    
    # Saving results
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Saving as JSON
    json_path = Path(output_dir) / f"results_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {json_path}")
    
    # Saving as CSV
    csv_path = Path(output_dir) / f"results_{timestamp}.csv"
    if results:
        fieldnames = results[0].keys()
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to {csv_path}")
    
    return results


def print_summary(results):
    print("\nEXPERIMENT SUMMARY")
    print(f"{'-'*60}")

    # Grouping by algorithm
    by_algo = {}
    for r in results:
        key = r['algorithm']
        if r['algorithm'] in ['astar', 'idastar']:
            key = f"{r['algorithm']}_{r['heuristic']}"
        
        if key not in by_algo:
            by_algo[key] = []
        by_algo[key].append(r)
    
    # Statistics for each algorithm
    for algo, algo_results in sorted(by_algo.items()):
        successful = [r for r in algo_results if r['success']]
        
        print(f"\n{algo.upper()}:")
        print(f"  Success rate: {len(successful)}/{len(algo_results)} ({100*len(successful)/len(algo_results):.1f}%)")
        
        if successful:
            avg_time = sum(r['time'] for r in successful) / len(successful)
            avg_nodes = sum(r['nodes_expanded'] for r in successful) / len(successful)
            avg_length = sum(r['solution_length'] for r in successful) / len(successful)
            
            print(f"  Average time: {avg_time:.4f}s")
            print(f"  Average nodes expanded: {avg_nodes:.1f}")
            print(f"  Average solution length: {avg_length:.1f}")
            
            min_time = min(r['time'] for r in successful)
            max_time = max(r['time'] for r in successful)
            print(f"  Time range: {min_time:.4f}s - {max_time:.4f}s")


if __name__ == '__main__':
    # Example experiment configuration
    
    # Standard grid (without soldier)

    # results = run_experiment_grid(
    #     n_values=[3, 4, 5],
    #     b_values=[2, 3],
    #     s_values=[0],
    #     algorithms=['bfs', 'ucs', 'astar', 'idastar', 'bidirectional'],
    #     heuristics=['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    #     timeout=60
    # )
    # print_summary(results)
    

    # Grid with soldiers
    results_soldiers = run_experiment_grid(
        n_values=[3, 4],
        b_values=[2, 3],
        s_values=[0, 1],
        algorithms=['bfs', 'ucs', 'astar', 'idastar', 'bidirectional'],
        heuristics=[ 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
        timeout=120
    )
    print_summary(results_soldiers)
