import sys
sys.path.append('src')

from state import State
from algorithms import bfs, a_star
from heuristics import HEURISTICS


def demo():
    """
    Demo: Classic 3 Missionaries, 3 Cannibals problem.
    """
    print("\nCLASSIC MISSIONARIES AND CANNIBALS PROBLEM")
    print("3 Missionaries, 3 Cannibals, Boat Capacity = 2")
    print("-"*60)
    
    initial = State(3, 3, 'L', 3, 3)
    
    # Solving with BFS
    print("\nSolving with BFS...")
    result = bfs(initial, boat_capacity=2)
    result.display_solution("BFS")


if __name__ == '__main__':
    demo()