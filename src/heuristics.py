"""
Heuristic functions for the Missionaries and Cannibals problem.
"""

import math
from collections import deque
from state import State

def h_zero(state, boat_capacity):
    """
    H0: Zero heuristic (makes A* behave like UCS).
    """
    return 0

def h1_people_per_boat(state, boat_capacity):
    """
    H1: Number of people-per-boat heuristic.
    """
    if state.has_soldiers:
        total_left = state.M_left + state.C_left + state.S_left
    else:
        total_left = state.M_left + state.C_left
    return math.ceil(total_left / boat_capacity)

def h2_dominant_group(state, boat_capacity):
    """
    H2: Dominant-group heuristic.
    """
    if state.has_soldiers:
        max_group = max(
            math.ceil(state.M_left / boat_capacity),
            math.ceil(state.C_left / boat_capacity),
            math.ceil(state.S_left / boat_capacity)
        )
    else:
        max_group = max(
            math.ceil(state.M_left / boat_capacity),
            math.ceil(state.C_left / boat_capacity)
        )
    return max_group

def h3_boat_parity(state, boat_capacity):
    """
    H3: Boat-parity adjusted heuristic.
    """
    base_estimate = h1_people_per_boat(state, boat_capacity)
    
    if state.has_soldiers:
        people_left = state.M_left + state.C_left + state.S_left
    else:
        people_left = state.M_left + state.C_left

    if people_left > 0 and state.boat == 'R':
        return base_estimate + 1
    
    return base_estimate

def h4_formula_based(state, boat_capacity):
    """
    H4: Formula-based estimate.
    """
    if state.has_soldiers:
        total_left = state.M_left + state.C_left + state.S_left
    else:
        total_left = state.M_left + state.C_left
    
    if total_left == 0:
        return 1 if state.boat == 'L' else 0
    
    if total_left <= boat_capacity:
        return 1 if state.boat == 'L' else 2
    
    if boat_capacity <= 1:
        return 2 * total_left - 1
    
    trips = 2 * math.ceil(total_left / (boat_capacity - 1)) - 1
    
    if state.boat == 'R' and total_left > 0:
        trips += 1
    
    return trips

def h5_tight_lower_bound(state, boat_capacity):
    """
    H5: Tight lower bound heuristic.
    """
    if state.has_soldiers:
        total_left = state.M_left + state.C_left + state.S_left
    else:
        total_left = state.M_left + state.C_left
 
    if total_left == 0:
        
        if state.boat == 'R':
            return 0
        else:
            return 1

    if total_left <= boat_capacity:
        if state.boat == 'L':
            return 1 
        else:
            return 2  
        
    if boat_capacity == 1:
        return total_left * 2 - 1

    first_trip = boat_capacity
    remaining_after_first = total_left - first_trip
    
    if remaining_after_first <= 0:
        if state.boat == 'L':
            return 1
        else:
            return 2  
    net_per_round_trip = boat_capacity - 1
    round_trips_needed = math.ceil(remaining_after_first / net_per_round_trip)
    total_trips = 1 + (round_trips_needed * 2) - 1
    
    if state.boat == 'R' and total_left > 0:
        total_trips += 1  
    
    return total_trips

_PDB_CACHE = {}

def _pdb_is_legal(M_left, C_left, S_left, total_M, total_C, total_S, has_soldiers):
    """Check if a state configuration is legal."""
    if not (0 <= M_left <= total_M and 0 <= C_left <= total_C):
        return False
    
    M_right = total_M - M_left
    C_right = total_C - C_left
    
    if has_soldiers:
        if not (0 <= S_left <= total_S):
            return False
        S_right = total_S - S_left
        
        # Left bank: M > 0 and S == 0 requires M >= C
        if M_left > 0 and S_left == 0 and M_left < C_left:
            return False
        # Right bank: M > 0 and S == 0 requires M >= C
        if M_right > 0 and S_right == 0 and M_right < C_right:
            return False
    else:
        # Standard rules: M > 0 requires M >= C on each bank
        if M_left > 0 and M_left < C_left:
            return False
        if M_right > 0 and M_right < C_right:
            return False
    
    return True


def _build_pdb(total_M, total_C, total_S, boat_capacity, has_soldiers):
    """
    Building pattern database using backward BFS from goal state.
    """
    b = boat_capacity

    # Generating all valid moves
    moves = []
    for m in range(b + 1):
        for c in range(b + 1):
            if has_soldiers:
                for s in range(b + 1):
                    if 1 <= m + c + s <= b:
                        moves.append((m, c, s))
            else:
                if 1 <= m + c <= b:
                    moves.append((m, c, 0))
    
    # Creating goal state object
    if has_soldiers:
        goal_state = State(0, 0, 'R', total_M, total_C, 0, total_S)
        goal = (0, 0, 0, 'R')
    else:
        goal_state = State(0, 0, 'R', total_M, total_C)
        goal = (0, 0, 'R')
    
    # Checking if goal is legal 
    if not goal_state.is_legal():
        return {}
    
    # BFS backward from goal
    queue = deque([goal])
    distance = {goal: 0}
    
    while queue:
        current = queue.popleft()
        d = distance[current]
        
        if has_soldiers:
            M_left, C_left, S_left, boat = current
        else:
            M_left, C_left, boat = current
            S_left = 0
        
        # Generating predecessors
        for dm, dc, ds in moves:
            if boat == 'R':
                new_M = M_left + dm
                new_C = C_left + dc
                new_S = S_left + ds
                new_boat = 'L'
            else:
                new_M = M_left - dm
                new_C = C_left - dc
                new_S = S_left - ds
                new_boat = 'R'
        
            if not (0 <= new_M <= total_M and 0 <= new_C <= total_C):
                continue
            if has_soldiers and not (0 <= new_S <= total_S):
                continue
            
            if has_soldiers:
                temp_state = State(new_M, new_C, new_boat, total_M, total_C, new_S, total_S)
                pred = (new_M, new_C, new_S, new_boat)
            else:
                temp_state = State(new_M, new_C, new_boat, total_M, total_C)
                pred = (new_M, new_C, new_boat)
            
            # Check if temp state is valid and not visited
            if temp_state.is_legal() and pred not in distance:
                distance[pred] = d + 1
                queue.append(pred)
    
    return distance

def h_pdb(state, boat_capacity):
    """
    H6: Pattern Database heuristic.
    """
    total_M = state.total_M
    total_C = state.total_C
    total_S = state.total_S if state.has_soldiers else 0
    
    cache_key = (total_M, total_C, total_S, boat_capacity, state.has_soldiers)
    
    # Building PDB if not cached
    if cache_key not in _PDB_CACHE:
        _PDB_CACHE[cache_key] = _build_pdb(
            total_M, total_C, total_S, boat_capacity, state.has_soldiers
        )
    
    pdb = _PDB_CACHE[cache_key]
    
    if state.has_soldiers:
        key = (state.M_left, state.C_left, state.S_left, state.boat)
    else:
        key = (state.M_left, state.C_left, state.boat)
    
    return pdb.get(key, 0)

# Dictionary mapping: Heuristic names -> functions
HEURISTICS = {
    'h0': h_zero,
    'h1': h1_people_per_boat,
    'h2': h2_dominant_group,
    'h3': h3_boat_parity,          
    'h4': h4_formula_based,     
    'h5': h5_tight_lower_bound,                     
    'h6': h_pdb,                   
}

def get_heuristic(name):
    """
    Get heuristic function by name.
    """
    if name not in HEURISTICS:
        raise ValueError(f"Unknown heuristic: {name}. Choose from {list(HEURISTICS.keys())}")
    return HEURISTICS[name]

def describe_heuristic(name):
    """
    Get description of heuristic.
    """
    descriptions = {
        'h0': 'Zero heuristic',
        'h1': 'People-per-boat',
        'h2': 'Dominant-group',
        'h3': 'Boat Parity',
        'h4': 'Formula-based',
        'h5': 'Tight lower bound',
        'h6': 'Pattern database',
    }
    return descriptions.get(name, 'Unknown heuristic')

def compare_heuristics(state, boat_capacity, heuristic_names=None):
    """
    Compare multiple heuristics on a given state.
    """
    if heuristic_names is None:
        heuristic_names = list(HEURISTICS.keys())
    
    results = {}
    for name in heuristic_names:
        if name in HEURISTICS:
            try:
                value = HEURISTICS[name](state, boat_capacity)
                results[name] = value
            except Exception as e:
                results[name] = f"Error: {e}"
    
    return results