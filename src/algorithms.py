"""
Search algorithms for the Missionaries and Cannibals problem.
Implements: BFS, UCS, A*, and IDA*
"""

import heapq
import time
from collections import deque
from state import generate_successors


class SearchResult:
    """Container for search algorithm results."""
    
    def __init__(self, success, path=None, actions=None, stats=None):
        """
        Initialize search result.
        
        Args:
            success: Boolean indicating if solution was found
            path: List of State objects from start to goal
            actions: List of action descriptions
            stats: Dictionary of search statistics
        """
        self.success = success
        self.path = path or []
        self.actions = actions or []
        self.stats = stats or {}
    
    def display_solution(self, algorithm_name=""):
        """
        Display the solution path with visual step-by-step representation.
        
        Args:
            algorithm_name: Name of algorithm used
        """
        print("\n" + "="*70)
        print(f"SOLUTION FOUND BY {algorithm_name.upper()}")
        print("="*70)
        
        if not self.success:
            print("No solution found!")
            return
        
        print(f"\nSolution Length: {len(self.path) - 1} steps")
        print(f"Nodes Expanded: {self.stats.get('nodes_expanded', 'N/A')}")
        print(f"Time Taken: {self.stats.get('time_taken', 0):.4f} seconds")
        print(f"Total Cost: {self.stats.get('path_cost', 'N/A')}")
        
        print("\n" + "="*70)
        print("STEP-BY-STEP SOLUTION")
        print("="*70)
        
        # Display initial state
        self.path[0].display_state(step_num=0, action_desc="INITIAL STATE")
        
        # Display each step
        for i in range(1, len(self.path)):
            action = self.actions[i-1] if i-1 < len(self.actions) else "Unknown action"
            self.path[i].display_state(step_num=i, action_desc=action)
        
        print("\n" + "="*70)
        print("GOAL STATE REACHED!")
        print("="*70)
        
        # Display statistics
        print("\nSearch Statistics:")
        print(f"  - Algorithm: {algorithm_name}")
        print(f"  - Solution depth: {len(self.path) - 1}")
        print(f"  - Nodes expanded: {self.stats.get('nodes_expanded', 'N/A')}")
        print(f"  - Max queue size: {self.stats.get('max_queue_size', 'N/A')}")
        print(f"  - Time taken: {self.stats.get('time_taken', 0):.4f} seconds")
        if 'path_cost' in self.stats:
            print(f"  - Total cost: {self.stats['path_cost']}")
        print()


def bfs(initial_state, boat_capacity):
    """
    Breadth-First Search.
    
    Explores nodes level by level. Guarantees shortest path in terms of
    number of steps (when all step costs are equal).
    
    Args:
        initial_state: Starting State object
        boat_capacity: Boat capacity
        
    Returns:
        SearchResult object
    """
    start_time = time.time()
    
    # Queue stores: (state, path, actions)
    queue = deque([(initial_state, [initial_state], [])])
    visited = {initial_state.to_tuple()}
    
    nodes_expanded = 0
    max_queue_size = 1
    
    while queue:
        max_queue_size = max(max_queue_size, len(queue))
        
        current_state, path, actions = queue.popleft()
        nodes_expanded += 1
        
        # Check if goal
        if current_state.is_goal():
            time_taken = time.time() - start_time
            stats = {
                'nodes_expanded': nodes_expanded,
                'max_queue_size': max_queue_size,
                'time_taken': time_taken,
                'path_cost': len(path) - 1  # Number of steps
            }
            return SearchResult(True, path, actions, stats)
        
        # Expand successors
        for successor, action, cost in generate_successors(current_state, boat_capacity):
            state_tuple = successor.to_tuple()
            if state_tuple not in visited:
                visited.add(state_tuple)
                new_path = path + [successor]
                new_actions = actions + [action]
                queue.append((successor, new_path, new_actions))
    
    # No solution found
    time_taken = time.time() - start_time
    stats = {
        'nodes_expanded': nodes_expanded,
        'max_queue_size': max_queue_size,
        'time_taken': time_taken
    }
    return SearchResult(False, stats=stats)


def ucs(initial_state, boat_capacity):
    """
    Uniform-Cost Search.
    
    Expands nodes in order of path cost. Guarantees optimal solution
    when step costs vary.
    
    Args:
        initial_state: Starting State object
        boat_capacity: Boat capacity
        
    Returns:
        SearchResult object
    """
    start_time = time.time()
    
    # Priority queue stores: (cost, counter, state, path, actions)
    # Counter ensures FIFO ordering for ties
    counter = 0
    pq = [(0, counter, initial_state, [initial_state], [])]
    visited = {}  # Maps state -> best cost found so far
    
    nodes_expanded = 0
    max_queue_size = 1
    
    while pq:
        max_queue_size = max(max_queue_size, len(pq))
        
        cost, _, current_state, path, actions = heapq.heappop(pq)
        state_tuple = current_state.to_tuple()
        
        # Skip if we've found a better path to this state
        if state_tuple in visited and visited[state_tuple] < cost:
            continue
        
        visited[state_tuple] = cost
        nodes_expanded += 1
        
        # Check if goal
        if current_state.is_goal():
            time_taken = time.time() - start_time
            stats = {
                'nodes_expanded': nodes_expanded,
                'max_queue_size': max_queue_size,
                'time_taken': time_taken,
                'path_cost': cost
            }
            return SearchResult(True, path, actions, stats)
        
        # Expand successors
        for successor, action, step_cost in generate_successors(current_state, boat_capacity):
            new_cost = cost + step_cost
            state_tuple = successor.to_tuple()
            
            # Only add if we haven't seen this state or found a better path
            if state_tuple not in visited or visited[state_tuple] > new_cost:
                counter += 1
                new_path = path + [successor]
                new_actions = actions + [action]
                heapq.heappush(pq, (new_cost, counter, successor, new_path, new_actions))
    
    # No solution found
    time_taken = time.time() - start_time
    stats = {
        'nodes_expanded': nodes_expanded,
        'max_queue_size': max_queue_size,
        'time_taken': time_taken
    }
    return SearchResult(False, stats=stats)


def a_star(initial_state, boat_capacity, heuristic_func):
    """
    A* Search.
    
    Expands nodes in order of f(n) = g(n) + h(n), where g(n) is path cost
    and h(n) is heuristic estimate to goal. Guarantees optimal solution
    if heuristic is admissible.
    
    Args:
        initial_state: Starting State object
        boat_capacity: Boat capacity
        heuristic_func: Heuristic function h(state, boat_capacity)
        
    Returns:
        SearchResult object
    """
    start_time = time.time()
    
    # Priority queue stores: (f_cost, counter, g_cost, state, path, actions)
    counter = 0
    h_initial = heuristic_func(initial_state, boat_capacity)
    pq = [(h_initial, counter, 0, initial_state, [initial_state], [])]
    visited = {}  # Maps state -> best g_cost found
    
    nodes_expanded = 0
    max_queue_size = 1
    
    while pq:
        max_queue_size = max(max_queue_size, len(pq))
        
        f_cost, _, g_cost, current_state, path, actions = heapq.heappop(pq)
        state_tuple = current_state.to_tuple()
        
        # Skip if we've found a better path to this state
        if state_tuple in visited and visited[state_tuple] < g_cost:
            continue
        
        visited[state_tuple] = g_cost
        nodes_expanded += 1
        
        # Check if goal
        if current_state.is_goal():
            time_taken = time.time() - start_time
            stats = {
                'nodes_expanded': nodes_expanded,
                'max_queue_size': max_queue_size,
                'time_taken': time_taken,
                'path_cost': g_cost
            }
            return SearchResult(True, path, actions, stats)
        
        # Expand successors
        for successor, action, step_cost in generate_successors(current_state, boat_capacity):
            new_g = g_cost + step_cost
            state_tuple = successor.to_tuple()
            
            # Only add if we haven't seen this state or found a better path
            if state_tuple not in visited or visited[state_tuple] > new_g:
                counter += 1
                h_cost = heuristic_func(successor, boat_capacity)
                f = new_g + h_cost
                new_path = path + [successor]
                new_actions = actions + [action]
                heapq.heappush(pq, (f, counter, new_g, successor, new_path, new_actions))
    
    # No solution found
    time_taken = time.time() - start_time
    stats = {
        'nodes_expanded': nodes_expanded,
        'max_queue_size': max_queue_size,
        'time_taken': time_taken
    }
    return SearchResult(False, stats=stats)


def ida_star(initial_state, boat_capacity, heuristic_func, max_iterations=1000):
    """
    Iterative Deepening A* Search.
    
    Memory-efficient variant of A* that uses iterative deepening with
    f-cost thresholds instead of maintaining a priority queue.
    
    Args:
        initial_state: Starting State object
        boat_capacity: Boat capacity
        heuristic_func: Heuristic function h(state, boat_capacity)
        max_iterations: Maximum number of iterations
        
    Returns:
        SearchResult object
    """
    start_time = time.time()
    
    def search(state, g_cost, threshold, path, actions, visited_in_path, stats):
        """
        Recursive depth-limited search.
        
        Returns:
            (found, new_threshold, result_path, result_actions)
        """
        f_cost = g_cost + heuristic_func(state, boat_capacity)
        
        if f_cost > threshold:
            return False, f_cost, None, None
        
        stats['nodes_expanded'] += 1
        
        if state.is_goal():
            return True, threshold, path, actions
        
        min_threshold = float('inf')
        
        for successor, action, step_cost in generate_successors(state, boat_capacity):
            state_tuple = successor.to_tuple()
            
            # Avoid cycles in current path
            if state_tuple in visited_in_path:
                continue
            
            visited_in_path.add(state_tuple)
            new_path = path + [successor]
            new_actions = actions + [action]
            
            found, new_t, result_path, result_actions = search(
                successor, g_cost + step_cost, threshold,
                new_path, new_actions, visited_in_path, stats
            )
            
            visited_in_path.remove(state_tuple)
            
            if found:
                return True, new_t, result_path, result_actions
            
            min_threshold = min(min_threshold, new_t)
        
        return False, min_threshold, None, None
    
    # Initialize threshold with heuristic estimate
    threshold = heuristic_func(initial_state, boat_capacity)
    stats = {'nodes_expanded': 0, 'iterations': 0}
    
    for iteration in range(max_iterations):
        stats['iterations'] = iteration + 1
        visited_in_path = {initial_state.to_tuple()}
        
        found, threshold, path, actions = search(
            initial_state, 0, threshold,
            [initial_state], [], visited_in_path, stats
        )
        
        if found:
            time_taken = time.time() - start_time
            stats['time_taken'] = time_taken
            stats['path_cost'] = len(path) - 1
            return SearchResult(True, path, actions, stats)
        
        if threshold == float('inf'):
            break  # No solution exists
    
    # No solution found
    time_taken = time.time() - start_time
    stats['time_taken'] = time_taken
    return SearchResult(False, stats=stats)


# Dictionary mapping algorithm names to functions
ALGORITHMS = {
    'bfs': bfs,
    'ucs': ucs,
    'astar': a_star,
    'idastar': ida_star
}


def get_algorithm(name):
    """
    Get algorithm function by name.
    
    Args:
        name: Algorithm name ('bfs', 'ucs', 'astar', 'idastar')
        
    Returns:
        Algorithm function
        
    Raises:
        ValueError: If algorithm name is invalid
    """
    if name not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {name}. Choose from {list(ALGORITHMS.keys())}")
    return ALGORITHMS[name]