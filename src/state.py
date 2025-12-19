"""
State representation for the Missionaries and Cannibals problem.
"""

class State:
    """
    Represents a state in the river-crossing puzzle.
    
    For 2-group variant: (M_left, C_left, boat_side)
    For 3-group variant: (M_left, C_left, S_left, boat_side)
    
    Boat side: 'L' (left) or 'R' (right)
    """
    
    def __init__(self, missionaries_left, cannibals_left, boat_side, 
                 total_missionaries, total_cannibals, soldiers_left=None, total_soldiers=0):
        """
        Initialize a state.
        
        Args:
            missionaries_left: Number of missionaries on left bank
            cannibals_left: Number of cannibals on left bank
            boat_side: 'L' or 'R' specifies boat location
            total_missionaries: Total missionaries in problem
            total_cannibals: Total cannibals in problem
            soldiers_left: Number of soldiers on left
            total_soldiers: Total soldiers in problem
        """
        self.M_left = missionaries_left
        self.C_left = cannibals_left
        self.S_left = soldiers_left
        self.boat = boat_side
        
        self.total_M = total_missionaries
        self.total_C = total_cannibals
        self.total_S = total_soldiers
        
        # Calculating right bank 
        self.M_right = total_missionaries - missionaries_left
        self.C_right = total_cannibals - cannibals_left
        self.S_right = total_soldiers - soldiers_left if soldiers_left is not None else 0
        
        # Checking if soldiers are included in the problem
        self.has_soldiers = soldiers_left is not None
    

    def is_legal(self):
        """
        Check if the current state is legal.
        
        2-group rule: On each bank, if missionaries > 0, then missionaries >= cannibals
        3-group rule: On each bank, if missionaries > 0 and soldiers == 0, then missionaries >= cannibals
        """
        if self.has_soldiers:
            # Checking Left bank
            if self.M_left > 0 and self.S_left == 0 and self.M_left < self.C_left:
                return False
            # Checking Right bank
            if self.M_right > 0 and self.S_right == 0 and self.M_right < self.C_right:
                return False
        else:
            if self.M_left > 0 and self.M_left < self.C_left:
                return False
            if self.M_right > 0 and self.M_right < self.C_right:
                return False
        
        return True
    

    def is_goal(self):
        """
        Check if this is the goal state. 
        """
        if self.has_soldiers:
            return self.M_left == 0 and self.C_left == 0 and self.S_left == 0 and self.boat == 'R'
        else:
            return self.M_left == 0 and self.C_left == 0 and self.boat == 'R'
    

    def __hash__(self):
        """
        Helper Function.
        """
        if self.has_soldiers:
            return hash((self.M_left, self.C_left, self.S_left, self.boat))
        return hash((self.M_left, self.C_left, self.boat))
    
    def __eq__(self, other):
        """
        Helper function - Checking if two states are identical.
        """
        if not isinstance(other, State):
            return False
        if self.has_soldiers:
            return (self.M_left == other.M_left and 
                    self.C_left == other.C_left and 
                    self.S_left == other.S_left and 
                    self.boat == other.boat)
        return (self.M_left == other.M_left and 
                self.C_left == other.C_left and 
                self.boat == other.boat)
    
    def __lt__(self, other):
        """
        Helper function - Less than comparison for priority queue.
        """
        if self.has_soldiers:
            return (self.M_left, self.C_left, self.S_left, self.boat) < \
                   (other.M_left, other.C_left, other.S_left, other.boat)
        return (self.M_left, self.C_left, self.boat) < (other.M_left, other.C_left, other.boat)
    
    def __repr__(self):
        """
        Helper function - String Represenatation.
        """
        if self.has_soldiers:
            return f"State(M={self.M_left}, C={self.C_left}, S={self.S_left}, boat={self.boat})"
        return f"State(M={self.M_left}, C={self.C_left}, boat={self.boat})"
    
    def to_tuple(self):
        """
        Helper function.
        """
        if self.has_soldiers:
            return (self.M_left, self.C_left, self.S_left, self.boat)
        return (self.M_left, self.C_left, self.boat)
    
    def display_side(self, side):
        """
        Display one side of the river with symbols.
        
        Returns:
            String representation of that bank
        """
        if side == 'L':
            m_count = self.M_left
            c_count = self.C_left
            s_count = self.S_left if self.has_soldiers else 0
        else:
            m_count = self.M_right
            c_count = self.C_right
            s_count = self.S_right if self.has_soldiers else 0
        
        # Using symbols: M=👨, C=👹, S=🛡️
        display = ""
        display += "👨" * m_count
        display += " " if m_count > 0 and c_count > 0 else ""
        display += "👹" * c_count
        
        if self.has_soldiers:
            display += " " if (m_count > 0 or c_count > 0) and s_count > 0 else ""
            display += "🛡️" * s_count
        
        return display if display else "(empty)"
    
    def display_boat(self):
        """
        Display boat position.
        """
        if self.boat == 'L':
            return "🚣"
        else:
            return "     " 
    
    def display_state(self, step_num=None, action_desc=""):
        """
        Display the current state.
        
        Args:
            step_num: Step number to display
            action_desc: Description of the action that led to this state
        """
        header = ""
        if step_num is not None:
            header = f"Step {step_num}"
            if action_desc:
                header += f": {action_desc}"
            header += f"\n{'-'*60}"
            print(header)
        
        left_display = self.display_side('L')
        right_display = self.display_side('R')
        boat_display = self.display_boat() if self.boat == 'L' else "     "
        boat_right = "     🚣" if self.boat == 'R' else ""
        
        # Creating visual representation
        print(f"\nLeft Bank{' '*10}River{' '*10}Right Bank")
        print(f"{'-'*20}  ~~~~  {'-'*20}")
        print(f"{left_display:20}  {boat_display}~~~~{boat_right:6}  {right_display:20}")
        print(f"{'-'*20}  ~~~~  {'-'*20}")
        
        # Display Missionaries and Cannibals count on both banks
        if self.has_soldiers:
            print(f"Left: {self.M_left}M, {self.C_left}C, {self.S_left}S  |  " +
                  f"Right: {self.M_right}M, {self.C_right}C, {self.S_right}S")
        else:
            print(f"Left: {self.M_left}M, {self.C_left}C  |  Right: {self.M_right}M, {self.C_right}C")
        
        print()
        if self.is_goal():
            print(f"Status: Goal State Reached!\n")
        print(f'-'*60)


def generate_successors(state, boat_capacity):
    """
    Generate all legal successor states from the current state.
    
    Args:
        state: Current State object
        boat_capacity: Maximum people that can fit in boat
        
    Returns:
        List of (successor_state, action_description, cost) tuples
    """
    successors = []
    
    # Determining direction
    if state.boat == 'L':
        # Boat moving from left to right
        moving_from = 'L'
        moving_to = 'R'
    else:
        # Boat moving from right to left
        moving_from = 'R'
        moving_to = 'L'
    
    # Available people on the boat's current side
    if moving_from == 'L':
        available_M = state.M_left
        available_C = state.C_left
        available_S = state.S_left if state.has_soldiers else 0
    else:
        available_M = state.M_right
        available_C = state.C_right
        available_S = state.S_right if state.has_soldiers else 0
    
    # Generating all possible moves
    # At least 1 person must be in the boat
    max_range = boat_capacity + 1
    
    if state.has_soldiers:
        # 3-group variant: try all combinations of M, C, S
        for m in range(available_M + 1):
            for c in range(available_C + 1):
                for s in range(available_S + 1):
                    total_people = m + c + s
                    
                    # Must have at least 1 person and not exceed capacity
                    if total_people < 1 or total_people > boat_capacity:
                        continue
                    
                    # Creating new state
                    if moving_from == 'L':
                        new_M_left = state.M_left - m
                        new_C_left = state.C_left - c
                        new_S_left = state.S_left - s
                    else:
                        new_M_left = state.M_left + m
                        new_C_left = state.C_left + c
                        new_S_left = state.S_left + s
                    
                    new_state = State(new_M_left, new_C_left, moving_to,
                                     state.total_M, state.total_C,
                                     new_S_left, state.total_S)
                    
                    # Only adding if legal
                    if new_state.is_legal():
                        action = f"Move {m}M, {c}C, {s}S from {moving_from} to {moving_to}"
                        cost = total_people  
                        successors.append((new_state, action, cost))
    else:
        # 2-group variant: try all combinations of M and C
        for m in range(available_M + 1):
            for c in range(available_C + 1):
                total_people = m + c
                
                # Must have at least 1 person and not exceed capacity
                if total_people < 1 or total_people > boat_capacity:
                    continue
                
                # Creating new state
                if moving_from == 'L':
                    new_M_left = state.M_left - m
                    new_C_left = state.C_left - c
                else:
                    new_M_left = state.M_left + m
                    new_C_left = state.C_left + c
                
                new_state = State(new_M_left, new_C_left, moving_to,
                                 state.total_M, state.total_C)
                
                # Only adding if legal
                if new_state.is_legal():
                    action = f"Move {m}M, {c}C from {moving_from} to {moving_to}"
                    cost = total_people  
                    successors.append((new_state, action, cost))
    
    return successors