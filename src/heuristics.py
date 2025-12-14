"""
Heuristic functions for A* and IDA* algorithms.
All heuristics must be admissible (never overestimate) for optimality.
"""

import math

def h1_people_per_boat(state, boat_capacity):
    """
    H1: People-per-boat heuristic.
    
    Estimates minimum crossings if every trip fully loads the boat,
    ignoring return trips and constraints.
    
    This is admissible because it assumes:
    - Perfect packing (always fill the boat)
    - No return trips needed
    - No constraint violations
    
    Args:
        state: Current State object
        boat_capacity: Boat capacity
        
    Returns:
        Estimated minimum steps to goal
    """
    if state.has_soldiers:
        total_left = state.M_left + state.C_left + state.S_left
    else:
        total_left = state.M_left + state.C_left
    
    # Minimum trips needed to transport everyone
    return math.ceil(total_left / boat_capacity)


def h2_dominant_group(state, boat_capacity):
    """
    H2: Dominant-group heuristic.
    
    At least as many trips as needed to clear the larger remaining group.
    This accounts for the fact that we can't always pack optimally due to
    the safety constraints.
    
    This is admissible because:
    - We need at least enough trips to move the largest group
    - Moving the largest group is a lower bound on total trips
    
    Args:
        state: Current State object
        boat_capacity: Boat capacity
        
    Returns:
        Estimated minimum steps to goal
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
    
    Combines people-per-boat with boat position consideration.
    If the boat is on the wrong side (right) when people remain on left,
    we need at least one additional return trip.
    
    This is admissible because:
    - Base estimate (people per boat) is admissible
    - Boat being on wrong side only adds to the estimate
    - We only add 1 trip for boat repositioning (actual may need more)
    
    Args:
        state: Current State object
        boat_capacity: Boat capacity
        
    Returns:
        Estimated minimum steps to goal
    """
    base_estimate = h1_people_per_boat(state, boat_capacity)
    
    if state.has_soldiers:
        people_left = state.M_left + state.C_left + state.S_left
    else:
        people_left = state.M_left + state.C_left
    
    # If people remain on left but boat is on right, add penalty
    if people_left > 0 and state.boat == 'R':
        return base_estimate + 1
    
    return base_estimate


def h4_combined(state, boat_capacity):
    """
    H4: Combined heuristic (max of h1, h2).
    
    Takes the maximum of people-per-boat and dominant-group heuristics.
    Since both are admissible, their max is also admissible.
    
    This often provides tighter bounds than either heuristic alone.
    
    Args:
        state: Current State object
        boat_capacity: Boat capacity
        
    Returns:
        Estimated minimum steps to goal
    """
    return max(h1_people_per_boat(state, boat_capacity),
               h2_dominant_group(state, boat_capacity))


def h_zero(state, boat_capacity):
    """
    H0: Zero heuristic (uninformed search).
    
    Always returns 0, making A* behave like Uniform Cost Search.
    Useful for comparison purposes.
    
    Args:
        state: Current State object
        boat_capacity: Boat capacity
        
    Returns:
        0 (no heuristic guidance)
    """
    return 0


# Dictionary mapping heuristic names to functions
HEURISTICS = {
    'h0': h_zero,
    'h1': h1_people_per_boat,
    'h2': h2_dominant_group,
    'h3': h3_boat_parity,
    'h4': h4_combined
}


def get_heuristic(name):
    """
    Get heuristic function by name.
    
    Args:
        name: Heuristic name ('h0', 'h1', 'h2', 'h3', 'h4')
        
    Returns:
        Heuristic function
        
    Raises:
        ValueError: If heuristic name is invalid
    """
    if name not in HEURISTICS:
        raise ValueError(f"Unknown heuristic: {name}. Choose from {list(HEURISTICS.keys())}")
    return HEURISTICS[name]


def describe_heuristic(name):
    """
    Get a description of a heuristic.
    
    Args:
        name: Heuristic name
        
    Returns:
        String description
    """
    descriptions = {
        'h0': 'Zero heuristic (uninformed, A* becomes UCS)',
        'h1': 'People-per-boat: ceil(people_left / boat_capacity)',
        'h2': 'Dominant-group: max group size consideration',
        'h3': 'Boat-parity: adjusts for boat position',
        'h4': 'Combined: max(h1, h2)'
    }
    return descriptions.get(name, 'Unknown heuristic')