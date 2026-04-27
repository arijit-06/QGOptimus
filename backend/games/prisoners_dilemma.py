"""
Prisoner's Dilemma Game Implementation
Classical and Quantum strategies for the classic game theory problem.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass


# Action constants
COOPERATE = 0
DEFECT = 1

# Action names for display
ACTION_NAMES = {COOPERATE: "Cooperate", DEFECT: "Defect"}


@dataclass
class PrisonersDilemmaPayoffs:
    """Payoff matrix for Prisoner's Dilemma."""
    # (Player 0 payoff, Player 1 payoff)
    both_cooperate: Tuple[int, int] = (3, 3)
    p0_cooperate_p1_defect: Tuple[int, int] = (0, 5)
    p0_defect_p1_cooperate: Tuple[int, int] = (5, 0)
    both_defect: Tuple[int, int] = (1, 1)


class PrisonersDilemma:
    """
    Prisoner's Dilemma game with classical and quantum strategies.
    
    The dilemma: Each player chooses to Cooperate (C) or Defect (D).
    - Both C: Reward (3, 3)
    - Both D: Punishment (1, 1)
    - One C, one D: Defector gets Temptation (5), Cooperator gets Sucker (0)
    
    Classical Nash Equilibrium: (D, D) - both defect
    Quantum Equilibrium: (C, C) - cooperation via quantum strategies
    """
    
    def __init__(self):
        self.payoffs = PrisonersDilemmaPayoffs()
        self.name = "Prisoner's Dilemma"
        self.description = (
            "Two prisoners are separated and must choose to Cooperate or Defect. "
            "If both cooperate, they get 3 years each. If both defect, 1 year each. "
            "If one defects and other cooperates, defector goes free (0) and cooperator gets 5 years."
        )
        
    def get_payoff(self, action_p0: int, action_p1: int) -> Tuple[int, int]:
        """Get payoffs for given actions."""
        if action_p0 == COOPERATE and action_p1 == COOPERATE:
            return self.payoffs.both_cooperate
        elif action_p0 == COOPERATE and action_p1 == DEFECT:
            return self.payoffs.p0_cooperate_p1_defect
        elif action_p0 == DEFECT and action_p1 == COOPERATE:
            return self.payoffs.p0_defect_p1_cooperate
        else:
            return self.payoffs.both_defect
    
    def get_payoff_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get payoff matrices for both players."""
        # Player 0's payoff matrix
        p0 = np.array([
            [3, 0],  # P0: C vs C, C vs D
            [5, 1]   # P0: D vs C, D vs D
        ])
        
        # Player 1's payoff matrix
        p1 = np.array([
            [3, 5],  # P1: C vs C, C vs D
            [0, 1]   # P1: D vs C, D vs D
        ])
        
        return p0, p1
    
    def classical_payoff_from_probabilities(self, 
                                           p_p0: float, 
                                           p_p1: float) -> Tuple[float, float]:
        """
        Calculate expected payoffs from mixed strategies.
        
        Args:
            p_p0: Probability player 0 cooperates
            p_p1: Probability player 1 cooperates
            
        Returns:
            Expected payoffs for (player_0, player_1)
        """
        # P(C,C) = p_p0 * p_p1
        # P(C,D) = p_p0 * (1-p_p1)
        # P(D,C) = (1-p_p0) * p_p1
        # P(D,D) = (1-p_p0) * (1-p_p1)
        
        p_cc = p_p0 * p_p1
        p_cd = p_p0 * (1 - p_p1)
        p_dc = (1 - p_p0) * p_p1
        p_dd = (1 - p_p0) * (1 - p_p1)
        
        p0_payoff = p_cc * 3 + p_cd * 0 + p_dc * 5 + p_dd * 1
        p1_payoff = p_cc * 3 + p_cd * 5 + p_dc * 0 + p_dd * 1
        
        return p0_payoff, p1_payoff
    
    def quantum_payoff_from_measurement(self, 
                                       measurement_result: Dict[str, float]) -> Tuple[float, float]:
        """
        Calculate expected payoffs from quantum measurement results.
        
        Args:
            measurement_result: Dict mapping state to probability
                              States: '00' (C,C), '01' (C,D), '10' (D,C), '11' (D,D)
            
        Returns:
            Expected payoffs for (player_0, player_1)
        """
        p0_payoff = 0.0
        p1_payoff = 0.0
        
        # Map quantum states to actions
        # '00' = both cooperate
        # '01' = P0 cooperates, P1 defects
        # '10' = P0 defects, P1 cooperates
        # '11' = both defect
        
        state_payoffs = {
            '00': (3, 3),
            '01': (0, 5),
            '10': (5, 0),
            '11': (1, 1)
        }
        
        for state, prob in measurement_result.items():
            if state in state_payoffs:
                p0, p1 = state_payoffs[state]
                p0_payoff += prob * p0
                p1_payoff += prob * p1
                
        return p0_payoff, p1_payoff
    
    def get_classical_equilibrium(self) -> Dict[str, Any]:
        """Get classical Nash equilibrium."""
        return {
            'type': 'pure',
            'strategy': (DEFECT, DEFECT),
            'strategy_names': (ACTION_NAMES[DEFECT], ACTION_NAMES[DEFECT]),
            'payoffs': (1, 1),
            'explanation': 'In classical game theory, (D,D) is the Nash equilibrium - each player defects as it minimizes their individual risk.'
        }
    
    def get_quantum_advantage_info(self) -> Dict[str, Any]:
        """Information about quantum advantage in this game."""
        return {
            'classical_equilibrium': {
                'strategy': 'Defect, Defect',
                'payoffs': (1, 1)
            },
            'quantum_equilibrium': {
                'strategy': 'Cooperation via quantum entanglement',
                'payoffs': (3, 3),
                'description': 'Using quantum strategies (superposition and entanglement), players can achieve the Pareto-optimal (C,C) outcome.'
            },
            'advantage': 'Quantum strategy can achieve mutual cooperation (3,3) vs classical defection (1,1)',
            'mechanism': 'Quantum entanglement creates correlations that allow coordinated cooperation without direct communication.'
        }
    
    def get_action_from_measurement(self, state: str) -> Tuple[int, int]:
        """
        Convert quantum measurement state to player actions.
        
        Args:
            state: Quantum state string (e.g., '00', '01', '10', '11')
            
        Returns:
            Tuple of (player_0_action, player_1_action)
        """
        # First bit = player 0, second bit = player 1
        # 0 = Cooperate, 1 = Defect
        p0_action = int(state[0])
        p1_action = int(state[1])
        return p0_action, p1_action


def create_game() -> PrisonersDilemma:
    """Factory function to create Prisoner's Dilemma game."""
    return PrisonersDilemma()


if __name__ == "__main__":
    # Test the game
    game = PrisonersDilemma()
    
    print("=== Prisoner's Dilemma ===")
    print(f"Description: {game.description}")
    print()
    
    # Test payoffs
    print("Payoff Matrix:")
    print(f"  (C,C): {game.get_payoff(COOPERATE, COOPERATE)}")
    print(f"  (C,D): {game.get_payoff(COOPERATE, DEFECT)}")
    print(f"  (D,C): {game.get_payoff(DEFECT, COOPERATE)}")
    print(f"  (D,D): {game.get_payoff(DEFECT, DEFECT)}")
    print()
    
    # Classical equilibrium
    eq = game.get_classical_equilibrium()
    print(f"Classical Equilibrium: {eq['strategy_names']}")
    print(f"Payoffs: {eq['payoffs']}")
    print()
    
    # Quantum advantage info
    adv = game.get_quantum_advantage_info()
    print("Quantum Advantage:")
    print(f"  Classical: {adv['classical_equilibrium']['strategy']} -> {adv['classical_equilibrium']['payoffs']}")
    print(f"  Quantum: {adv['quantum_equilibrium']['strategy']} -> {adv['quantum_equilibrium']['payoffs']}")