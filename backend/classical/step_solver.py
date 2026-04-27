"""
Step-Based Classical Game Solver
Generates execution steps for visualization of classical optimization.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ExecutionStep:
    """Represents a single execution step."""
    step: int
    active_line: int
    description: str
    parameters: Dict[str, Any]
    payoff: float
    state: Dict[str, Any]


# Code display for visualization - Prisoner's Dilemma
CLASSICAL_CODE_PD = {
    1: "def solve_classical(payoff_p0, payoff_p1):",
    2: "    # Initialize probabilities (50/50 mixed strategy)",
    3: "    p = 0.5  # Player 0 probability of cooperation",
    4: "    q = 0.5  # Player 1 probability of cooperation",
    5: "    ",
    6: "    # Compute expected payoff for current strategies",
    7: "    p0_payoff = p * (q * payoff_p0[0,0] + (1-q) * payoff_p0[0,1]) + \\",
    8: "                (1-p) * (q * payoff_p0[1,0] + (1-q) * payoff_p0[1,1])",
    9: "    p1_payoff = p * (q * payoff_p1[0,0] + (1-q) * payoff_p1[0,1]) + \\",
    10: "                (1-p) * (q * payoff_p1[1,0] + (1-q) * payoff_p1[1,1])",
    11: "    ",
    12: "    # Update probabilities using best response dynamics",
    13: "    # Player 0's best response",
    14: "    if payoff_p0[0,1] > payoff_p0[1,1]:",
    15: "        p = min(1.0, p + 0.1)  # Increase cooperation",
    16: "    else:",
    17: "        p = max(0.0, p - 0.1)  # Decrease cooperation",
    18: "    ",
    19: "    # Player 1's best response",
    20: "    if payoff_p1[1,0] > payoff_p1[0,0]:",
    21: "        q = min(1.0, q + 0.1)",
    22: "    else:",
    23: "        q = max(0.0, q - 0.1)",
    24: "    ",
    25: "    return p, q, p0_payoff + p1_payoff"
}

# Code display for visualization - Battle of Sexes
CLASSICAL_CODE_BOS = {
    1: "def solve_classical(payoff_p0, payoff_p1):",
    2: "    # Initialize probabilities (50/50 mixed strategy)",
    3: "    p = 0.5  # Player 0 probability of Opera",
    4: "    q = 0.5  # Player 1 probability of Opera",
    5: "    ",
    6: "    # Compute expected payoff for coordination",
    7: "    p0_payoff = p * (q * payoff_p0[0,0] + (1-q) * payoff_p0[0,1]) + \\",
    8: "                (1-p) * (q * payoff_p0[1,0] + (1-q) * payoff_p0[1,1])",
    9: "    p1_payoff = p * (q * payoff_p1[0,0] + (1-q) * payoff_p1[0,1]) + \\",
    10: "                (1-p) * (q * payoff_p1[1,0] + (1-q) * payoff_p1[1,1])",
    11: "    ",
    12: "    # Update probabilities toward coordination",
    13: "    # Both players prefer same outcome",
    14: "    if payoff_p0[0,0] > payoff_p0[1,1]:",
    15: "        p = min(1.0, p + 0.1)",
    16: "    else:",
    17: "        p = max(0.0, p - 0.1)",
    18: "    ",
    19: "    if payoff_p1[0,0] > payoff_p1[1,1]:",
    20: "        q = min(1.0, q + 0.1)",
    21: "    else:",
    22: "        q = max(0.0, q - 0.1)",
    23: "    ",
    24: "    return p, q, p0_payoff + p1_payoff"
}

# Code display for visualization - Matching Pennies
CLASSICAL_CODE_MP = {
    1: "def solve_classical(payoff_p0, payoff_p1):",
    2: "    # Initialize probabilities (50/50 mixed strategy)",
    3: "    p = 0.5  # Player 1 probability of Heads",
    4: "    q = 0.5  # Player 2 probability of Heads",
    5: "    ",
    6: "    # Compute expected payoff (zero-sum)",
    7: "    p0_payoff = p * (q * payoff_p0[0,0] + (1-q) * payoff_p0[0,1]) + \\",
    8: "                (1-p) * (q * payoff_p0[1,0] + (1-q) * payoff_p0[1,1])",
    9: "    p1_payoff = p * (q * payoff_p1[0,0] + (1-q) * payoff_p1[0,1]) + \\",
    10: "                (1-p) * (q * payoff_p1[1,0] + (1-q) * payoff_p1[1,1])",
    11: "    ",
    12: "    # Zero-sum game: best response is 50/50",
    13: "    # No profitable deviation exists",
    14: "    # Equilibrium is p=0.5, q=0.5",
    15: "    ",
    16: "    # Update toward equilibrium",
    17: "    p = 0.5 + (p - 0.5) * 0.9  # Converge to 0.5",
    18: "    q = 0.5 + (q - 0.5) * 0.9",
    19: "    ",
    20: "    return p, q, p0_payoff + p1_payoff"
}


class StepBasedClassicalSolver:
    """
    Step-based classical solver that generates execution steps
    for visualization purposes.
    """
    
    def __init__(self):
        self.steps: List[ExecutionStep] = []
        
    def generate_steps(self,
                       payoff_p0: np.ndarray,
                       payoff_p1: np.ndarray,
                       game_type: str,
                       max_iterations: int = 20) -> List[Dict[str, Any]]:
        """
        Generate step-by-step execution for classical optimization.
        
        Args:
            payoff_p0: Payoff matrix for player 0
            payoff_p1: Payoff matrix for player 1
            game_type: Type of game
            max_iterations: Maximum number of iterations
            
        Returns:
            List of execution steps
        """
        self.steps = []
        
        # Get appropriate code display
        code_map = {
            "prisoners_dilemma": CLASSICAL_CODE_PD,
            "battle_of_sexes": CLASSICAL_CODE_BOS,
            "matching_pennies": CLASSICAL_CODE_MP
        }
        code_display = code_map.get(game_type, CLASSICAL_CODE_PD)
        
        # Step 1: Initialize
        p, q = 0.5, 0.5
        step = ExecutionStep(
            step=1,
            active_line=3,
            description="Initialize player strategies to 50/50 mixed strategy",
            parameters={"player_0_prob": p, "player_1_prob": q},
            payoff=0.0,
            state={"p": p, "q": q, "iteration": 0}
        )
        self.steps.append(asdict(step))
        
        # Iterative optimization
        for iteration in range(max_iterations):
            # Step 2: Compute payoff
            p0_payoff = self._compute_payoff(p, q, payoff_p0)
            p1_payoff = self._compute_payoff(p, q, payoff_p1)
            total_payoff = p0_payoff + p1_payoff
            
            step = ExecutionStep(
                step=len(self.steps) + 1,
                active_line=7,
                description=f"Compute expected payoffs: P0={p0_payoff:.3f}, P1={p1_payoff:.3f}",
                parameters={
                    "player_0_prob": p,
                    "player_1_prob": q,
                    "player_0_payoff": p0_payoff,
                    "player_1_payoff": p1_payoff
                },
                payoff=total_payoff,
                state={"p": p, "q": q, "iteration": iteration, "p0_payoff": p0_payoff, "p1_payoff": p1_payoff}
            )
            self.steps.append(asdict(step))
            
            # Step 3: Update probabilities based on game type
            p_new, q_new = self._update_strategies(p, q, payoff_p0, payoff_p1, game_type)
            
            step = ExecutionStep(
                step=len(self.steps) + 1,
                active_line=14,
                description=f"Update strategies: P0={p:.3f}→{p_new:.3f}, P1={q:.3f}→{q_new:.3f}",
                parameters={
                    "player_0_prob_old": p,
                    "player_0_prob_new": p_new,
                    "player_1_prob_old": q,
                    "player_1_prob_new": q_new
                },
                payoff=total_payoff,
                state={"p_old": p, "p_new": p_new, "q_old": q, "q_new": q_new, "iteration": iteration}
            )
            self.steps.append(asdict(step))
            
            p, q = p_new, q_new
            
            # Check convergence
            if iteration > 5 and abs(p - 0.5) < 0.01 and abs(q - 0.5) < 0.01:
                break
        
        # Final step: Return result
        p0_payoff = self._compute_payoff(p, q, payoff_p0)
        p1_payoff = self._compute_payoff(p, q, payoff_p1)
        
        step = ExecutionStep(
            step=len(self.steps) + 1,
            active_line=25,
            description=f"Converged to equilibrium: P0={p:.3f}, P1={q:.3f}, Total Payoff={p0_payoff + p1_payoff:.3f}",
            parameters={
                "player_0_prob": p,
                "player_1_prob": q,
                "player_0_payoff": p0_payoff,
                "player_1_payoff": p1_payoff,
                "total_payoff": p0_payoff + p1_payoff
            },
            payoff=p0_payoff + p1_payoff,
            state={"p": p, "q": q, "converged": True}
        )
        self.steps.append(asdict(step))
        
        return self.steps
    
    def _compute_payoff(self, p: float, q: float, payoff_matrix: np.ndarray) -> float:
        """Compute expected payoff for a player given strategies."""
        return (p * (q * payoff_matrix[0, 0] + (1 - q) * payoff_matrix[0, 1]) +
                (1 - p) * (q * payoff_matrix[1, 0] + (1 - q) * payoff_matrix[1, 1]))
    
    def _update_strategies(self, p: float, q: float,
                          payoff_p0: np.ndarray, payoff_p1: np.ndarray,
                          game_type: str) -> tuple:
        """Update strategies based on game type."""
        
        if game_type == "prisoners_dilemma":
            # Both defect in Nash equilibrium
            # But we explore toward cooperation
            p_new = max(0.0, min(1.0, p + np.random.uniform(-0.1, 0.1)))
            q_new = max(0.0, min(1.0, q + np.random.uniform(-0.1, 0.1)))
            
        elif game_type == "battle_of_sexes":
            # Coordinate toward same outcome
            if payoff_p0[0, 0] > payoff_p0[1, 1]:
                p_new = min(1.0, p + 0.05)
            else:
                p_new = max(0.0, p - 0.05)
                
            if payoff_p1[0, 0] > payoff_p1[1, 1]:
                q_new = min(1.0, q + 0.05)
            else:
                q_new = max(0.0, q - 0.05)
                
        else:  # matching_pennies
            # Converge to 50/50 equilibrium
            p_new = 0.5 + (p - 0.5) * 0.9
            q_new = 0.5 + (q - 0.5) * 0.9
            
        return p_new, q_new
    
    def get_code_display(self, game_type: str) -> Dict[int, str]:
        """Get code display for the specified game type."""
        code_map = {
            "prisoners_dilemma": CLASSICAL_CODE_PD,
            "battle_of_sexes": CLASSICAL_CODE_BOS,
            "matching_pennies": CLASSICAL_CODE_MP
        }
        return code_map.get(game_type, CLASSICAL_CODE_PD)