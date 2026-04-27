"""
Battle of the Sexes Game Implementation
A coordination game with misaligned preferences.
"""

import numpy as np
from typing import Dict, Any, Tuple
from dataclasses import dataclass


# Action constants
OPERA = 0
FOOTBALL = 1

# Action names for display
ACTION_NAMES = {OPERA: "Opera", FOOTBALL: "Football"}


@dataclass
class BattleOfSexesPayoffs:
    """Payoff matrix for Battle of the Sexes."""
    # (Player 0 payoff, Player 1 payoff)
    both_opera: Tuple[int, int] = (2, 1)
    both_football: Tuple[int, int] = (1, 2)
    mismatch: Tuple[int, int] = (0, 0)


class BattleOfSexes:
    """
    Battle of the Sexes game with classical and quantum strategies.
    
    A coordination game where both players want to coordinate but have different preferences:
    - Both choose Opera: (2, 1) - P0 happy, P1 okay
    - Both choose Football: (1, 2) - P0 okay, P1 happy
    - Mismatch: (0, 0) - both unhappy
    
    Classical: Two pure Nash equilibria (O,O) and (F,F), plus mixed strategy
    Quantum: Can achieve better coordination through entanglement
    """
    
    def __init__(self):
        self.payoffs = BattleOfSexesPayoffs()
        self.name = "Battle of the Sexes"
        self.description = (
            "A couple must decide between Opera (O) or Football (F). "
            "Player 0 prefers Opera (2,1), Player 1 prefers Football (1,2). "
            "If they coordinate, they both enjoy the activity. If they mismatch, both get 0."
        )
        
    def get_payoff(self, action_p0: int, action_p1: int) -> Tuple[int, int]:
        """Get payoffs for given actions."""
        if action_p0 == OPERA and action_p1 == OPERA:
            return self.payoffs.both_opera
        elif action_p0 == FOOTBALL and action_p1 == FOOTBALL:
            return self.payoffs.both_football
        else:
            return self.payoffs.mismatch
    
    def get_payoff_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get payoff matrices for both players."""
        # Player 0's payoff matrix (prefers Opera)
        p0 = np.array([
            [2, 0],  # P0: O vs O, O vs F
            [0, 1]   # P0: F vs O, F vs F
        ])
        
        # Player 1's payoff matrix (prefers Football)
        p1 = np.array([
            [1, 0],  # P1: O vs O, O vs F
            [0, 2]   # P1: F vs O, F vs F
        ])
        
        return p0, p1
    
    def classical_payoff_from_probabilities(self, 
                                           p_p0: float, 
                                           p_p1: float) -> Tuple[float, float]:
        """
        Calculate expected payoffs from mixed strategies.
        
        Args:
            p_p0: Probability player 0 chooses Opera
            p_p1: Probability player 1 chooses Opera
            
        Returns:
            Expected payoffs for (player_0, player_1)
        """
        # P(O,O) = p_p0 * p_p1
        # P(O,F) = p_p0 * (1-p_p1)
        # P(F,O) = (1-p_p0) * p_p1
        # P(F,F) = (1-p_p0) * (1-p_p1)
        
        p_oo = p_p0 * p_p1
        p_of = p_p0 * (1 - p_p1)
        p_fo = (1 - p_p0) * p_p1
        p_ff = (1 - p_p0) * (1 - p_p1)
        
        p0_payoff = p_oo * 2 + p_of * 0 + p_fo * 0 + p_ff * 1
        p1_payoff = p_oo * 1 + p_of * 0 + p_fo * 0 + p_ff * 2
        
        return p0_payoff, p1_payoff
    
    def quantum_payoff_from_measurement(self, 
                                       measurement_result: Dict[str, float]) -> Tuple[float, float]:
        """
        Calculate expected payoffs from quantum measurement results.
        
        Args:
            measurement_result: Dict mapping state to probability
                              States: '00' (O,O), '01' (O,F), '10' (F,O), '11' (F,F)
            
        Returns:
            Expected payoffs for (player_0, player_1)
        """
        p0_payoff = 0.0
        p1_payoff = 0.0
        
        # Map quantum states to actions
        state_payoffs = {
            '00': (2, 1),  # Both Opera
            '01': (0, 0),  # P0 Opera, P1 Football
            '10': (0, 0),  # P0 Football, P1 Opera
            '11': (1, 2)   # Both Football
        }
        
        for state, prob in measurement_result.items():
            if state in state_payoffs:
                p0, p1 = state_payoffs[state]
                p0_payoff += prob * p0
                p1_payoff += prob * p1
                
        return p0_payoff, p1_payoff
    
    def get_classical_equilibria(self) -> Dict[str, Any]:
        """Get classical Nash equilibria."""
        return {
            'equilibria': [
                {
                    'type': 'pure',
                    'strategy': (OPERA, OPERA),
                    'strategy_names': (ACTION_NAMES[OPERA], ACTION_NAMES[OPERA]),
                    'payoffs': (2, 1),
                    'explanation': 'Both go to Opera - Player 0 gets their preferred outcome'
                },
                {
                    'type': 'pure',
                    'strategy': (FOOTBALL, FOOTBALL),
                    'strategy_names': (ACTION_NAMES[FOOTBALL], ACTION_NAMES[FOOTBALL]),
                    'payoffs': (1, 2),
                    'explanation': 'Both go to Football - Player 1 gets their preferred outcome'
                },
                {
                    'type': 'mixed',
                    'strategy': 'P0: 2/3 Opera, 1/3 Football; P1: 1/3 Opera, 2/3 Football',
                    'payoffs': (2/3, 2/3),
                    'explanation': 'Mixed strategy equilibrium where each player randomizes based on their preference'
                }
            ]
        }
    
    def get_quantum_advantage_info(self) -> Dict[str, Any]:
        """Information about quantum advantage in this game."""
        return {
            'classical_equilibria': [
                {'strategy': 'Opera, Opera', 'payoffs': (2, 1)},
                {'strategy': 'Football, Football', 'payoffs': (1, 2)},
                {'strategy': 'Mixed strategy', 'payoffs': (0.67, 0.67)}
            ],
            'quantum_equilibrium': {
                'strategy': 'Superposition for fair coordination',
                'description': 'Quantum strategies can achieve fair coordination with expected payoffs (1.5, 1.5), better than mixed strategy.',
                'mechanism': 'Quantum entanglement allows players to coordinate on a fair superposition without direct communication.'
            },
            'advantage': 'Quantum can achieve fairer coordination (1.5, 1.5) vs classical mixed (0.67, 0.67)',
            'note': 'In Battle of Sexes, quantum advantage is about achieving fairer outcomes, not higher total payoff'
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
        # 0 = Opera, 1 = Football
        p0_action = int(state[0])
        p1_action = int(state[1])
        return p0_action, p1_action


def create_game() -> BattleOfSexes:
    """Factory function to create Battle of the Sexes game."""
    return BattleOfSexes()


if __name__ == "__main__":
    # Test the game
    game = BattleOfSexes()
    
    print("=== Battle of the Sexes ===")
    print(f"Description: {game.description}")
    print()
    
    # Test payoffs
    print("Payoff Matrix:")
    print(f"  (O,O): {game.get_payoff(OPERA, OPERA)}")
    print(f"  (O,F): {game.get_payoff(OPERA, FOOTBALL)}")
    print(f"  (F,O): {game.get_payoff(FOOTBALL, OPERA)}")
    print(f"  (F,F): {game.get_payoff(FOOTBALL, FOOTBALL)}")
    print()
    
    # Classical equilibria
    eq = game.get_classical_equilibria()
    print("Classical Equilibria:")
    for e in eq['equilibria']:
        print(f"  {e['type']}: {e['strategy_names']} -> {e['payoffs']}")
    print()
    
    # Quantum advantage info
    adv = game.get_quantum_advantage_info()
    print("Quantum Advantage:")
    print(f"  {adv['quantum_equilibrium']['description']}")