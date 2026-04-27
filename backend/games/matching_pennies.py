"""
Matching Pennies Game Implementation
A zero-sum game where quantum strategies can provide advantage.
"""

import numpy as np
from typing import Dict, Any, Tuple
from dataclasses import dataclass


# Action constants
HEADS = 0
TAILS = 1

# Action names for display
ACTION_NAMES = {HEADS: "Heads", TAILS: "Tails"}


@dataclass
class MatchingPenniesPayoffs:
    """Payoff matrix for Matching Pennies."""
    # (Player 0 payoff, Player 1 payoff)
    match: Tuple[int, int] = (1, -1)   # Same outcome: P0 wins
    mismatch: Tuple[int, int] = (-1, 1)  # Different outcome: P1 wins


class MatchingPennies:
    """
    Matching Pennies game with classical and quantum strategies.
    
    A zero-sum game:
    - Players simultaneously choose Heads (H) or Tails (T)
    - If coins match (HH or TT): Player 0 wins (+1), Player 1 loses (-1)
    - If coins don't match (HT or TH): Player 0 loses (-1), Player 1 wins (+1)
    
    Classical: No pure Nash equilibrium, mixed equilibrium at (0.5, 0.5)
    Quantum: Can achieve better win rate through quantum strategies
    """
    
    def __init__(self):
        self.payoffs = MatchingPenniesPayoffs()
        self.name = "Matching Pennies"
        self.description = (
            "Two players each choose Heads (H) or Tails (T). "
            "If their choices match (both H or both T), Player 0 wins (+1). "
            "If their choices differ, Player 1 wins (+1). "
            "This is a zero-sum game - one player's gain is the other's loss."
        )
        
    def get_payoff(self, action_p0: int, action_p1: int) -> Tuple[int, int]:
        """Get payoffs for given actions."""
        if action_p0 == action_p1:  # Match
            return self.payoffs.match
        else:  # Mismatch
            return self.payoffs.mismatch
    
    def get_payoff_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get payoff matrices for both players."""
        # Player 0's payoff matrix
        p0 = np.array([
            [1, -1],  # P0: H vs H, H vs T
            [-1, 1]   # P0: T vs H, T vs T
        ])
        
        # Player 1's payoff matrix (opposite of P0 in zero-sum)
        p1 = np.array([
            [-1, 1],  # P1: H vs H, H vs T
            [1, -1]   # P1: T vs H, T vs T
        ])
        
        return p0, p1
    
    def classical_payoff_from_probabilities(self, 
                                           p_p0: float, 
                                           p_p1: float) -> Tuple[float, float]:
        """
        Calculate expected payoffs from mixed strategies.
        
        Args:
            p_p0: Probability player 0 chooses Heads
            p_p1: Probability player 1 chooses Heads
            
        Returns:
            Expected payoffs for (player_0, player_1)
        """
        # P(H,H) = p_p0 * p_p1
        # P(H,T) = p_p0 * (1-p_p1)
        # P(T,H) = (1-p_p0) * p_p1
        # P(T,T) = (1-p_p0) * (1-p_p1)
        
        p_hh = p_p0 * p_p1
        p_ht = p_p0 * (1 - p_p1)
        p_th = (1 - p_p0) * p_p1
        p_tt = (1 - p_p0) * (1 - p_p1)
        
        # P0 wins on match (HH, TT), loses on mismatch (HT, TH)
        p0_payoff = p_hh * 1 + p_ht * (-1) + p_th * (-1) + p_tt * 1
        p1_payoff = -p0_payoff  # Zero-sum
        
        return p0_payoff, p1_payoff
    
    def quantum_payoff_from_measurement(self, 
                                       measurement_result: Dict[str, float]) -> Tuple[float, float]:
        """
        Calculate expected payoffs from quantum measurement results.
        
        Args:
            measurement_result: Dict mapping state to probability
                              States: '00' (H,H), '01' (H,T), '10' (T,H), '11' (T,T)
            
        Returns:
            Expected payoffs for (player_0, player_1)
        """
        p0_payoff = 0.0
        
        # Map quantum states to payoffs
        # '00' = both Heads (match -> P0 wins)
        # '01' = P0 H, P1 T (mismatch -> P1 wins)
        # '10' = P0 T, P1 H (mismatch -> P1 wins)
        # '11' = both Tails (match -> P0 wins)
        
        state_payoffs = {
            '00': 1,   # Match: P0 wins
            '01': -1,  # Mismatch: P1 wins
            '10': -1,  # Mismatch: P1 wins
            '11': 1    # Match: P0 wins
        }
        
        for state, prob in measurement_result.items():
            if state in state_payoffs:
                p0_payoff += prob * state_payoffs[state]
                
        p1_payoff = -p0_payoff  # Zero-sum
        
        return p0_payoff, p1_payoff
    
    def get_classical_equilibrium(self) -> Dict[str, Any]:
        """Get classical Nash equilibrium."""
        return {
            'equilibria': [
                {
                    'type': 'mixed',
                    'strategy': 'Both players randomize: 50% Heads, 50% Tails',
                    'payoffs': (0, 0),
                    'explanation': 'In zero-sum games, the mixed strategy equilibrium gives expected payoff 0 for both players. Neither player can improve by changing their strategy.'
                }
            ],
            'note': 'There is no pure strategy Nash equilibrium in Matching Pennies'
        }
    
    def get_quantum_advantage_info(self) -> Dict[str, Any]:
        """Information about quantum advantage in this game."""
        return {
            'classical_equilibrium': {
                'strategy': '50% Heads, 50% Tails (both players)',
                'payoffs': (0, 0),
                'explanation': 'At equilibrium, neither player can expect to win'
            },
            'quantum_equilibrium': {
                'strategy': 'Quantum strategy with optimal entanglement',
                'description': 'Quantum strategies can give Player 0 an advantage by using entangled states and measurement in different bases.',
                'expected_advantage': 'Player 0 can achieve positive expected payoff with optimal quantum strategy'
            },
            'advantage': 'Quantum strategies can shift the expected payoff from 0 to positive for the first player',
            'mechanism': 'Quantum entanglement and superposition allow strategies that correlate better than classical random choices, giving one player an edge.',
            'note': 'In zero-sum games, quantum advantage typically benefits one player at the expense of the other'
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
        # 0 = Heads, 1 = Tails
        p0_action = int(state[0])
        p1_action = int(state[1])
        return p0_action, p1_action
    
    def get_win_rate(self, measurement_result: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate win rates from measurement results.
        
        Args:
            measurement_result: Dict mapping state to probability
            
        Returns:
            Dictionary with win rates for each player
        """
        # Match states: '00', '11' -> P0 wins
        # Mismatch states: '01', '10' -> P1 wins
        
        p0_win_prob = measurement_result.get('00', 0) + measurement_result.get('11', 0)
        p1_win_prob = measurement_result.get('01', 0) + measurement_result.get('10', 0)
        
        return {
            'player_0_win_rate': p0_win_prob,
            'player_1_win_rate': p1_win_prob,
            'tie_rate': 0  # No ties in Matching Pennies
        }


def create_game() -> MatchingPennies:
    """Factory function to create Matching Pennies game."""
    return MatchingPennies()


if __name__ == "__main__":
    # Test the game
    game = MatchingPennies()
    
    print("=== Matching Pennies ===")
    print(f"Description: {game.description}")
    print()
    
    # Test payoffs
    print("Payoff Matrix:")
    print(f"  (H,H): {game.get_payoff(HEADS, HEADS)}")
    print(f"  (H,T): {game.get_payoff(HEADS, TAILS)}")
    print(f"  (T,H): {game.get_payoff(TAILS, HEADS)}")
    print(f"  (T,T): {game.get_payoff(TAILS, TAILS)}")
    print()
    
    # Classical equilibrium
    eq = game.get_classical_equilibrium()
    print("Classical Equilibrium:")
    for e in eq['equilibria']:
        print(f"  {e['type']}: {e['strategy']}")
        print(f"  Payoffs: {e['payoffs']}")
    print()
    
    # Quantum advantage info
    adv = game.get_quantum_advantage_info()
    print("Quantum Advantage:")
    print(f"  {adv['quantum_equilibrium']['description']}")
    print(f"  {adv['advantage']}")