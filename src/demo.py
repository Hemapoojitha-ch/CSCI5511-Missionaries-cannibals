"""
Demo script to showcase visual solution output.
"""

import sys
sys.path.append('src')

from state import State
from algorithms import bfs, a_star
from heuristics import h1_people_per_boat, h2_dominant_group

def demo_basic():
    """Demo basic 3M3C problem with BFS."""
    print("\n" + "="*70)
    print("DEMO 1: Classic 3 Missionaries, 3 Cannibals (BFS)")
    print("="*70)
    
    initial = State(3, 3, 'L', 3, 3)
    result = bfs(initial, boat_capacity=2)
    result.display_solution("BFS")


def demo_astar():
    """Demo with A* and different heuristics."""
    print("\n" + "="*70)
    print("DEMO 2: 4 Missionaries, 4 Cannibals with A* (h2 heuristic)")
    print("="*70)
    
    initial = State(4, 4, 'L', 4, 4)
    result = a_star(initial, boat_capacity=3, heuristic_func=h2_dominant_group)
    result.display_solution("A* with h2")


def demo_soldiers():
    """Demo with soldiers (3-group variant)."""
    print("\n" + "="*70)
    print("DEMO 3: 3M, 3C, 2S with Soldiers (A* with h1)")
    print("="*70)
    
    initial = State(3, 3, 'L', 3, 3, soldiers_left=2, total_soldiers=2)
    result = a_star(initial, boat_capacity=2, heuristic_func=h1_people_per_boat)
    result.display_solution("A* with h1 (Soldier Variant)")


def demo_comparison():
    """Demo comparing multiple algorithms on same instance."""
    print("\n" + "="*70)
    print("DEMO 4: Algorithm Comparison on Same Problem")
    print("="*70)
    
    n, b = 3, 2
    initial = State(n, n, 'L', n, n)
    
    algorithms = [
        ("BFS", lambda: bfs(initial, b)),
        ("A* (h1)", lambda: a_star(initial, b, h1_people_per_boat)),
        ("A* (h2)", lambda: a_star(initial, b, h2_dominant_group))
    ]
    
    results = []
    for name, algo_func in algorithms:
        result = algo_func()
        results.append((name, result))
    
    # Show only statistics comparison
    print(f"\n{'Algorithm':<15} {'Steps':<8} {'Nodes':<12} {'Time (s)':<12} {'Cost':<8}")
    print("-"*60)
    for name, result in results:
        steps = len(result.path) - 1 if result.success else "N/A"
        nodes = result.stats.get('nodes_expanded', 'N/A')
        time_val = f"{result.stats.get('time_taken', 0):.4f}"
        cost = result.stats.get('path_cost', 'N/A')
        print(f"{name:<15} {steps:<8} {nodes:<12} {time_val:<12} {cost:<8}")


if __name__ == '__main__':
    # Run all demos
    demo_basic()
    
    input("\nPress Enter to continue to next demo...")
    demo_astar()
    
    input("\nPress Enter to continue to next demo...")
    demo_soldiers()
    
    input("\nPress Enter to continue to comparison demo...")
    demo_comparison()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print("\nTo run your own problems:")
    print("  python src/main.py -n 3 -b 2 -a bfs")
    print("  python src/main.py -n 5 -b 3 -a astar -H h3")
    print("  python src/main.py -n 3 -b 2 -s 2 -a astar")
    print("\nFor full comparison:")
    print("  python src/main.py -n 4 -b 2 --compare")
    print()