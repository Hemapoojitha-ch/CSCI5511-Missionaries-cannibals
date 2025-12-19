"""
Search algorithms for the Missionaries and Cannibals problem.
Implements: BFS, UCS, A*, IDA*, and Bidirectional Search
"""

import heapq
import time
from collections import deque
from state import generate_successors


class SearchResult:
    
    def __init__(self, success, path=None, actions=None, stats=None):
        """
        Initializing search result.
        
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
        Display the solution path with step-by-step representation.
        """
        # print(f"SOLUTION FOUND BY {algorithm_name.upper()}")
        
        if not self.success:
            print("No solution found!")
            return
        
        print("STEP-BY-STEP SOLUTION")
        print("-"*60)
        
        # Display initial state
        self.path[0].display_state(step_num=0, action_desc="INITIAL STATE")
        
        # Display each step
        for i in range(1, len(self.path)):
            action = self.actions[i-1] if i-1 < len(self.actions) else "Unknown action"
            self.path[i].display_state(step_num=i, action_desc=action)
        
        # Display statistics
        print("Search Statistics:")
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
    """
    start_time = time.time()
    
    queue = deque([(initial_state, [initial_state], [])])
    visited = {initial_state.to_tuple()}
    
    nodes_expanded = 0
    max_queue_size = 1
    
    while queue:
        max_queue_size = max(max_queue_size, len(queue))
        
        current_state, path, actions = queue.popleft()
        nodes_expanded += 1
        
        # Checking if goal
        if current_state.is_goal():
            time_taken = time.time() - start_time
            stats = {
                'nodes_expanded': nodes_expanded,
                'max_queue_size': max_queue_size,
                'time_taken': time_taken,
                'path_cost': len(path) - 1
            }
            return SearchResult(True, path, actions, stats)
        
        # Expanding successors
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
    """
    start_time = time.time()
    
    counter = 0
    pq = [(0, counter, initial_state, [initial_state], [])]
    visited = {}
    
    nodes_expanded = 0
    max_queue_size = 1
    
    while pq:
        max_queue_size = max(max_queue_size, len(pq))
        
        cost, _, current_state, path, actions = heapq.heappop(pq)
        state_tuple = current_state.to_tuple()
        
        if state_tuple in visited and visited[state_tuple] <= cost:
            continue
        
        visited[state_tuple] = cost
        nodes_expanded += 1
        
        # Checking if goal
        if current_state.is_goal():
            time_taken = time.time() - start_time
            stats = {
                'nodes_expanded': nodes_expanded,
                'max_queue_size': max_queue_size,
                'time_taken': time_taken,
                'path_cost': cost
            }
            return SearchResult(True, path, actions, stats)
        
        # Expanding successors
        for successor, action, step_cost in generate_successors(current_state, boat_capacity):
            new_cost = cost + step_cost
            state_tuple = successor.to_tuple()
            
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
    """
    start_time = time.time()
    
    counter = 0
    h_initial = heuristic_func(initial_state, boat_capacity)
    pq = [(h_initial, counter, 0, initial_state, [initial_state], [])]
    visited = {}
    
    nodes_expanded = 0
    max_queue_size = 1
    
    while pq:
        max_queue_size = max(max_queue_size, len(pq))
        
        f_cost, _, g_cost, current_state, path, actions = heapq.heappop(pq)
        state_tuple = current_state.to_tuple()
        
        if state_tuple in visited and visited[state_tuple] <= g_cost:
            continue
        
        visited[state_tuple] = g_cost
        nodes_expanded += 1
        
        # Checking if goal
        if current_state.is_goal():
            time_taken = time.time() - start_time
            stats = {
                'nodes_expanded': nodes_expanded,
                'max_queue_size': max_queue_size,
                'time_taken': time_taken,
                'path_cost': g_cost,
                'heuristic_name': heuristic_func.__name__
            }
            return SearchResult(True, path, actions, stats)
        
        # Expanding successors
        for successor, action, step_cost in generate_successors(current_state, boat_capacity):
            new_g = g_cost + step_cost
            state_tuple = successor.to_tuple()
            
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


def ida_star(initial_state, boat_capacity, heuristic_func, max_iterations=10000):
    """
    Iterative Deepening A* Search.
    """
    start_time = time.time()
    
    def search(state, g_cost, threshold, path, actions, visited_in_path, stats):
        # Recursive depth-limited search
        f_cost = g_cost + heuristic_func(state, boat_capacity)
        
        if f_cost > threshold:
            return False, f_cost, None, None
        
        stats['nodes_expanded'] += 1
        
        if state.is_goal():
            return True, threshold, path, actions
        
        min_threshold = float('inf')
        
        for successor, action, step_cost in generate_successors(state, boat_capacity):
            state_tuple = successor.to_tuple()
            
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
            break
    
    time_taken = time.time() - start_time
    stats['time_taken'] = time_taken
    return SearchResult(False, stats=stats)


def bidirectional_bfs(initial_state, boat_capacity):
    """
    Bidirectional BFS
    """
    start_time = time.time()
    
    # Building goal state
    cls = initial_state.__class__
    if hasattr(cls, "goal_state") and callable(getattr(cls, "goal_state")):
        goal_state = cls.goal_state(initial_state)
    else:
        # Fallback construction
        goal_state = cls(
            0, 0, 'R',
            initial_state.total_M, initial_state.total_C,
            0 if hasattr(initial_state, 'has_soldiers') and initial_state.has_soldiers else None,
            initial_state.total_S if hasattr(initial_state, 'total_S') else 0
        )
    
    # Checking if goal
    if initial_state.is_goal():
        return SearchResult(True, [initial_state], [], {
            "nodes_expanded": 0,
            "max_queue_size": 1,
            "time_taken": 0.0,
            "path_cost": 0
        })
    
    def key(s):
        return s.to_tuple()
    
    start_k = key(initial_state)
    goal_k = key(goal_state)
    
    # Forward and backward frontiers
    qf = deque([initial_state])
    qb = deque([goal_state])
    
    # Parent tracking
    parent_f = {start_k: None}
    parent_b = {goal_k: None}
    
    # State storage for reconstruction
    state_f = {start_k: initial_state}
    state_b = {goal_k: goal_state}
    
    nodes_expanded = 0
    max_frontier = 2
    meet_k = None
    
    def expand_one(q, parent_this, parent_other, state_this):
        nonlocal nodes_expanded, meet_k
        cur = q.popleft()
        nodes_expanded += 1
        ck = key(cur)
        
        for succ, _, _ in generate_successors(cur, boat_capacity):
            sk = key(succ)
            if sk in parent_this:
                continue
            
            parent_this[sk] = ck
            state_this[sk] = succ
            
            if sk in parent_other:
                meet_k = sk
                return
            
            q.append(succ)
    
    while qf and qb and meet_k is None:
        max_frontier = max(max_frontier, len(qf) + len(qb))
        
        # Expanding from smaller frontier
        if len(qf) <= len(qb):
            expand_one(qf, parent_f, parent_b, state_f)
        else:
            expand_one(qb, parent_b, parent_f, state_b)
    
    # No solution found
    if meet_k is None:
        time_taken = time.time() - start_time
        return SearchResult(False, stats={
            "nodes_expanded": nodes_expanded,
            "max_queue_size": max_frontier,
            "time_taken": time_taken
        })
    
    # Reconstruct path: start -> meet
    path_keys = []
    cur = meet_k
    while cur is not None:
        path_keys.append(cur)
        cur = parent_f[cur]
    path_keys.reverse()
    path1 = [state_f[k] for k in path_keys]
    
    # Reconstruct path: meet -> goal
    path_keys = []
    cur = meet_k
    while cur is not None:
        path_keys.append(cur)
        cur = parent_b[cur]
    path2 = [state_b[k] for k in path_keys][1:]  # drop duplicate meet
    
    full_path = path1 + path2
    
    # Reconstruct actions from consecutive states
    actions = []
    for i in range(len(full_path) - 1):
        actions.append(_infer_action(full_path[i], full_path[i+1]))
    
    time_taken = time.time() - start_time
    return SearchResult(True, full_path, actions, {
        "nodes_expanded": nodes_expanded,
        "max_queue_size": max_frontier,
        "time_taken": time_taken,
        "path_cost": len(full_path) - 1
    })


def _infer_action(a, b):
    'Helper Function'
    def get(attr1, attr2=None, default=0):
        if hasattr(a, attr1) and hasattr(b, attr1):
            return getattr(a, attr1), getattr(b, attr1)
        if attr2 and hasattr(a, attr2) and hasattr(b, attr2):
            return getattr(a, attr2), getattr(b, attr2)
        return default, default

    M1, M2 = get("M_left", "M_L")
    C1, C2 = get("C_left", "C_L")

    if a.boat == b.boat:
        return "Invalid move (boat didn't change sides)"

    direction = f"{a.boat}->{b.boat}"

    dm = M1 - M2  
    dc = C1 - C2

    if a.boat == 'R' and b.boat == 'L':
        dm, dc = -dm, -dc

    if getattr(a, "has_soldiers", False):
        S1, S2 = get("S_left", "S_L")
        ds = S1 - S2
        if a.boat == 'R' and b.boat == 'L':
            ds = -ds
        return f"{direction}: {abs(dm)}M, {abs(dc)}C, {abs(ds)}S"

    return f"{direction}: {abs(dm)}M, {abs(dc)}C"


# Dictionary mapping: algorithm names -> functions
ALGORITHMS = {
    'bfs': bfs,
    'ucs': ucs,
    'astar': a_star,
    'idastar': ida_star,
    'bidirectional': bidirectional_bfs,
}


def get_algorithm(name):
    """
    Get algorithm function by name.
    """
    if name not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {name}. Choose from {list(ALGORITHMS.keys())}")
    return ALGORITHMS[name]
