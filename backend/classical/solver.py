"""
Classical Game Theory Solver
Implements classical game theory strategies and Nash equilibrium finding.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class GameType(Enum):
    PRISONERS_DILEMMA = "prisoners_dilemma"
    BATTLE_OF_SEXES = "battle_of_sexes"
    MATCHING_PENNIES = "matching_pennies"


@dataclass
class ClassicalStrategy:
    """Represents a classical mixed strategy."""
    player: int
    probabilities: Dict[int, float]  # action -> probability
    expected_payoff: float


@dataclass
class NashEquilibrium:
    """Represents a Nash equilibrium."""
    strategies: List[ClassicalStrategy]
    payoffs: Tuple[float, float]
    equilibrium_type: str  # 'pure' or 'mixed'


class ClassicalGameSolver:
    """
    Classical game theory solver using mixed strategies and optimization.
    """
    
    def __init__(self):
        self.history = []
        
    def solve_game(self, 
                  payoff_matrix_p0: np.ndarray,
                  payoff_matrix_p1: np.ndarray,
                  game_type: GameType) -> Dict[str, Any]:
        """
        Solve a game using classical methods.
        
        Args:
            payoff_matrix_p0: Payoff matrix for player 0
            payoff_matrix_p1: Payoff matrix for player 1
            game_type: Type of game
            
        Returns:
            Dictionary with equilibrium strategies and payoffs
        """
        # Find Nash equilibrium
        nash_eq = self._find_nash_equilibrium(payoff_matrix_p0, payoff_matrix_p1)
        
        # Find optimal mixed strategies
        mixed_strategies = self._find_optimal_mixed_strategies(
            payoff_matrix_p0, payoff_matrix_p1
        )
        
        return {
            'nash_equilibrium': nash_eq,
            'optimal_mixed_strategies': mixed_strategies,
            'game_type': game_type.value
        }
    
    def _find_nash_equilibrium(self,
                               payoff_p0: np.ndarray,
                               payoff_p1: np.ndarray) -> List[Dict[str, Any]]:
        """Find all Nash equilibria (pure and mixed)."""
        
        equilibria = []
        n = payoff_p0.shape[0]  # Number of actions
        m = payoff_p0.shape[1]  # Number of opponent actions
        
        # Check pure strategy equilibria
        for i in range(n):
            for j in range(m):
                p0_payoff = payoff_p0[i, j]
                p1_payoff = payoff_p1[i, j]
                
                # Check if player 0's best response
                p0_best = max(payoff_p0[:, j])
                # Check if player 1's best response
                p1_best = max(payoff_p1[i, :])
                
                if p0_payoff == p0_best and p1_payoff == p1_best:
                    equilibria.append({
                        'type': 'pure',
                        'strategies': [i, j],
                        'payoffs': (float(p0_payoff), float(p1_payoff))
                    })
        
        # Find mixed strategy equilibrium for 2x2 games
        if n == 2 and m == 2:
            mixed_eq = self._find_mixed_equilibrium_2x2(payoff_p0, payoff_p1)
            if mixed_eq:
                equilibria.append(mixed_eq)
                
        return equilibria
    
    def _find_mixed_equilibrium_2x2(self,
                                    payoff_p0: np.ndarray,
                                    payoff_p1: np.ndarray) -> Optional[Dict]:
        """
        Find mixed strategy Nash equilibrium for 2x2 games.
        """
        
        # Player 0's payoff matrix
        # a b
        # c d
        a, b = payoff_p0[0, 0], payoff_p0[0, 1]
        c, d = payoff_p0[1, 0], payoff_p0[1, 1]
        
        # Player 1's payoff matrix
        e, f = payoff_p1[0, 0], payoff_p1[0, 1]
        g, h = payoff_p1[1, 0], payoff_p1[1, 1]
        
        # Check if there's a mixed equilibrium
        # Player 0 indifferent between actions when:
        # p * a + (1-p) * c = p * b + (1-p) * d
        # where p is prob of playing action 0
        
        # Solve for p (Player 0's probability of playing action 0)
        if a + d != b + c:
            p = (d - c) / (a + d - b - c)
            
            if 0 <= p <= 1:
                # Player 1 indifferent when:
                # q * e + (1-q) * g = q * f + (1-q) * h
                if e + h != f + g:
                    q = (h - g) / (e + h - f - g)
                    
                    if 0 <= q <= 1:
                        # Calculate payoffs at equilibrium
                        p0_payoff = p * (q * a + (1-q) * b) + (1-p) * (q * c + (1-q) * d)
                        p1_payoff = p * (q * e + (1-q) * f) + (1-p) * (q * g + (1-q) * h)
                        
                        return {
                            'type': 'mixed',
                            'strategies': {
                                'player_0': {'action_0': float(p), 'action_1': float(1-p)},
                                'player_1': {'action_0': float(q), 'action_1': float(1-q)}
                            },
                            'payoffs': (float(p0_payoff), float(p1_payoff))
                        }
        
        return None
    
    def _find_optimal_mixed_strategies(self,
                                       payoff_p0: np.ndarray,
                                       payoff_p1: np.ndarray) -> Dict[str, Any]:
        """
        Find optimal mixed strategies using grid search.
        """
        
        best_payoff_p0 = float('-inf')
        best_payoff_p1 = float('-inf')
        best_p = 0.5
        best_q = 0.5
        
        # Grid search over probability space
        resolution = 101
        for p in np.linspace(0, 1, resolution):
            for q in np.linspace(0, 1, resolution):
                # Expected payoffs
                p0_payoff = 0
                p1_payoff = 0
                
                for a0 in [0, 1]:
                    for a1 in [0, 1]:
                        prob = (p if a0 == 0 else (1-p)) * (q if a1 == 0 else (1-q))
                        p0_payoff += prob * payoff_p0[a0, a1]
                        p1_payoff += prob * payoff_p1[a0, a1]
                
                self.history.append((p0_payoff, p1_payoff))
                
                # Use max-min strategy (conservative)
                if p0_payoff > best_payoff_p0:
                    best_payoff_p0 = p0_payoff
                    best_p = p
                    
                if p1_payoff > best_payoff_p1:
                    best_payoff_p1 = p1_payoff
                    best_q = q
        
        return {
            'player_0': {
                'probability_action_0': float(best_p),
                'probability_action_1': float(1 - best_p),
                'expected_payoff': float(best_payoff_p0)
            },
            'player_1': {
                'probability_action_0': float(best_q),
                'probability_action_1': float(1 - best_q),
                'expected_payoff': float(best_payoff_p1)
            }
        }
    
    def compute_expected_payoff(self,
                               payoff_matrix: np.ndarray,
                               strategy_p0: np.ndarray,
                               strategy_p1: np.ndarray) -> Tuple[float, float]:
        """
        Compute expected payoffs for both players given mixed strategies.
        
        Args:
            payoff_matrix: Payoff matrix
            strategy_p0: Player 0's strategy (probabilities for each action)
            strategy_p1: Player 1's strategy
            
        Returns:
            Tuple of (player_0_payoff, player_1_payoff)
        """
        p0_payoff = 0.0
        p1_payoff = 0.0
        
        for a0 in range(len(strategy_p0)):
            for a1 in range(len(strategy_p1)):
                prob = strategy_p0[a0] * strategy_p1[a1]
                p0_payoff += prob * payoff_matrix[0][a0, a1]
                p1_payoff += prob * payoff_matrix[1][a0, a1]
                
        return p0_payoff, p1_payoff
    
    def get_dominant_strategy(self,
                             payoff_matrix: np.ndarray) -> Optional[int]:
        """
        Find dominant strategy if it exists.
        
        Args:
            payoff_matrix: Player's payoff matrix
            
        Returns:
            Index of dominant strategy or None
        """
        n_actions = payoff_matrix.shape[1]
        
        for action in range(n_actions):
            is_dominant = True
            for other_action in range(n_actions):
                if action != other_action:
                    # Check if this action is better for ALL opponent actions
                    for opp_action in range(payoff_matrix.shape[0]):
                        if payoff_matrix[opp_action, action] < payoff_matrix[opp_action, other_action]:
                            is_dominant = False
                            break
                if not is_dominant:
                    break
                    
            if is_dominant:
                return action
                
        return None


class GamePayoffCalculator:
    """
    Calculates payoffs for different game outcomes.
    """
    
    @staticmethod
    def prisoners_dilemma(action_p0: int, action_p1: int) -> Tuple[int, int]:
        """
        Prisoner's Dilemma payoff:
        - Both cooperate (C,C): 3, 3
        - P0 cooperates, P1 defects: 0, 5
        - P0 defects, P1 cooperates: 5, 0
        - Both defect (D,D): 1, 1
        """
        if action_p0 == 0 and action_p1 == 0:  # C, C
            return (3, 3)
        elif action_p0 == 0 and action_p1 == 1:  # C, D
            return (0, 5)
        elif action_p0 == 1 and action_p1 == 0:  # D, C
            return (5, 0)
        else:  # D, D
            return (1, 1)
    
    @staticmethod
    def battle_of_sexes(action_p0: int, action_p1: int) -> Tuple[int, int]:
        """
        Battle of the Sexes payoff:
        - Both choose Opera (O,O): 2, 1
        - Both choose Football (F,F): 1, 2
        - Mismatched (O,F) or (F,O): 0, 0
        """
        if action_p0 == 0 and action_p1 == 0:  # O, O
            return (2, 1)
        elif action_p0 == 1 and action_p1 == 1:  # F, F
            return (1, 2)
        else:  # Mismatch
            return (0, 0)
    
    @staticmethod
    def matching_pennies(action_p0: int, action_p1: int) -> Tuple[int, int]:
        """
        Matching Pennies payoff (zero-sum):
        - Same (H,H) or (T,T): P0 wins (+1), P1 loses (-1)
        - Different (H,T) or (T,H): P0 loses (-1), P1 wins (+1)
        """
        if action_p0 == action_p1:  # Match
            return (1, -1)
        else:  # Mismatch
            return (-1, 1)
    
    @staticmethod
    def get_payoff_matrices(game_type: GameType) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get payoff matrices for a game type.
        
        Returns:
            Tuple of (payoff_matrix_p0, payoff_matrix_p1)
        """
        if game_type == GameType.PRISONERS_DILEMMA:
            # Player 0's payoff
            p0 = np.array([[3, 0], [5, 1]])
            # Player 1's payoff
            p1 = np.array([[3, 5], [0, 1]])
            return p0, p1
            
        elif game_type == GameType.BATTLE_OF_SEXES:
            p0 = np.array([[2, 0], [0, 1]])
            p1 = np.array([[1, 0], [0, 2]])
            return p0, p1
            
        elif game_type == GameType.MATCHING_PENNIES:
            p0 = np.array([[1, -1], [-1, 1]])
            p1 = np.array([[-1, 1], [1, -1]])
            return p0, p1
            
        else:
            raise ValueError(f"Unknown game type: {game_type}")


def create_solver() -> ClassicalGameSolver:
    """Factory function to create classical solver."""
    return ClassicalGameSolver()


if __name__ == "__main__":
    # Test classical solver
    solver = ClassicalGameSolver()
    calculator = GamePayoffCalculator()
    
    # Test Prisoner's Dilemma
    p0, p1 = calculator.get_payoff_matrices(GameType.PRISONERS_DILEMMA)
    result = solver.solve_game(p0, p1, GameType.PRISONERS_DILEMMA)
    
    print("Prisoner's Dilemma - Classical Solution:")
    print(f"Nash Equilibria: {result['nash_equilibrium']}")
    print(f"Optimal Mixed: {result['optimal_mixed_strategies']}")
    
    # Test Battle of Sexes
    p0, p1 = calculator.get_payoff_matrices(GameType.BATTLE_OF_SEXES)
    result = solver.solve_game(p0, p1, GameType.BATTLE_OF_SEXES)
    
    print("\nBattle of Sexes - Classical Solution:")
    print(f"Nash Equilibria: {result['nash_equilibrium']}")
    
    # Test Matching Pennies
    p0, p1 = calculator.get_payoff_matrices(GameType.MATCHING_PENNIES)
    result = solver.solve_game(p0, p1, GameType.MATCHING_PENNIES)
    
    print("\nMatching Pennies - Classical Solution:")
    print(f"Nash Equilibria: {result['nash_equilibrium']}")