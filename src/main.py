"""
Main program for Missionaries and Cannibals problem solver.
"""

import argparse
import sys
from state import State
from algorithms import get_algorithm, ALGORITHMS
from heuristics import get_heuristic, HEURISTICS, describe_heuristic


def solve_problem(n_missionaries, n_cannibals, boat_capacity, 
                  algorithm='bfs', heuristic='h1',
                  n_soldiers=0, verbose=True):
    """
    Args:
        n_missionaries: Number of missionaries
        n_cannibals: Number of cannibals
        boat_capacity: Boat capacity
        algorithm: Algorithm to use ('bfs', 'ucs', 'astar', 'idastar', 'bidirectional')
        heuristic: Heuristic for A*/IDA* ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
        n_soldiers: Number of soldiers (0 for standard 2-group variant)
        verbose: Whether to display detailed output
    """
    # Creating initial state
    if n_soldiers > 0:
        initial_state = State(n_missionaries, n_cannibals, 'L',
                            n_missionaries, n_cannibals,
                            n_soldiers, n_soldiers)
        variant = f"3-group ({n_missionaries}M, {n_cannibals}C, {n_soldiers}S)"
    else:
        initial_state = State(n_missionaries, n_cannibals, 'L',
                            n_missionaries, n_cannibals)
        variant = f"2-group ({n_missionaries}M, {n_cannibals}C)"
    
    if verbose:
        print()
        print(f"MISSIONARIES AND CANNIBALS PROBLEM - {variant}")
        print("-"*60)
        print(f"Boat Capacity: {boat_capacity}")
        print(f"Algorithm: {algorithm.upper()}")
        if algorithm in ['astar', 'idastar']:
            print(f"Heuristic: {heuristic} - {describe_heuristic(heuristic)}")
        print("-"*60)
    
    # Get algorithm function
    algo_func = get_algorithm(algorithm)
    
    # Run search
    if algorithm in ['astar', 'idastar']:
        heuristic_func = get_heuristic(heuristic)
        result = algo_func(initial_state, boat_capacity, heuristic_func)
    else:
        result = algo_func(initial_state, boat_capacity)
    
    # Display results
    if verbose:
        result.display_solution(algorithm)
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Solve the Missionaries and Cannibals river-crossing puzzle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Problem parameters
    parser.add_argument('-n', '--missionaries', type=int, default=3,
                       help='Number of missionaries (and cannibals)')
    parser.add_argument('-b', '--boat', type=int, default=2,
                       help='Boat capacity')
    parser.add_argument('-s', '--soldiers', type=int, default=0,
                       help='Number of soldiers (0 for standard variant)')
    
    # Algorithm selection
    parser.add_argument('-a', '--algorithm', choices=list(ALGORITHMS.keys()),
                       default='bfs', help='Search algorithm to use')
    parser.add_argument('-H', '--heuristic', choices=list(HEURISTICS.keys()),
                       default='h1', help='Heuristic for A*/IDA*')
    
    # Comparison
    parser.add_argument('--compare', action='store_true',
                       help='Run all algorithms and compare')
    parser.add_argument('--compare-heuristics', action='store_true',
                       help='Compare all heuristics with A*')
    
    # Output control
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Suppress detailed output')
    
    args = parser.parse_args()
    
    n = args.missionaries
    b = args.boat
    s = args.soldiers
    
    if args.compare:
        # Compare all algorithms
        print("\nCOMPARING ALL ALGORITHMS")
        print("-"*60)
        
        results = {}
        for algo in ALGORITHMS.keys():
            print(f"\n>>> Running {algo.upper()}...")
            if algo in ['astar', 'idastar']:
                result = solve_problem(n, n, b, algo, args.heuristic, s, verbose=not args.quiet)
            else:
                result = solve_problem(n, n, b, algo, n_soldiers=s, verbose=not args.quiet)
            results[algo] = result
        
        # Comparison Summary
        print("COMPARISON SUMMARY")
        print("-"*60)
        print(f"{'Algorithm':<12} {'Success':<10} {'Steps':<8} {'Nodes':<10} {'Time (s)':<12} {'Cost':<8}")
        print("-"*60)
        
        for algo, result in results.items():
            success = "Yes" if result.success else "No"
            steps = len(result.path) - 1 if result.success else "N/A"
            nodes = result.stats.get('nodes_expanded', 'N/A')
            time_val = f"{result.stats.get('time_taken', 0):.4f}"
            cost = result.stats.get('path_cost', 'N/A')
            
            print(f"{algo:<13} {success:<10} {steps:<8} {nodes:<10} {time_val:<12} {cost:<8}")
        
    elif args.compare_heuristics:
        # Compare all heuristics with A*
        print("\nCOMPARING HEURISTICS (A* Algorithm)")
        print("-"*60)
        
        results = {}
        for heur in HEURISTICS.keys():
            print(f"\n\n>>> Running A* with {heur}...")
            result = solve_problem(n, n, b, 'astar', heur, s, verbose=not args.quiet)
            results[heur] = result
        
        # Comparison Summary
        print("\nHEURISTIC COMPARISON SUMMARY")
        print("-"*60)
        print(f"{'Heuristic':<12} {'Success':<10} {'Steps':<8} {'Nodes':<10} {'Time (s)':<12}")
        print("-"*60)
        
        for heur, result in results.items():
            success = "Yes" if result.success else "No"
            steps = len(result.path) - 1 if result.success else "N/A"
            nodes = result.stats.get('nodes_expanded', 'N/A')
            time_val = f"{result.stats.get('time_taken', 0):.4f}"
            
            desc = describe_heuristic(heur)
            print(f"{heur:<12} {success:<10} {steps:<8} {nodes:<10} {time_val:<12}")
            print(f"  └─ {desc}")
        
    else:
        # Single algorithm run
        result = solve_problem(n, n, b, args.algorithm, args.heuristic, s, 
                              verbose=not args.quiet)
        
        if not result.success:
            sys.exit(1)


if __name__ == '__main__':
    main()