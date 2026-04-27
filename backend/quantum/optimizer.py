"""
Variational Quantum Algorithm (VQA) Optimizer
Uses COBYLA and SPSA for classical optimization of quantum parameters.
"""

import numpy as np
from typing import Callable, Tuple, Dict, Any, List, Optional
from scipy.optimize import minimize, differential_evolution
from dataclasses import dataclass
from enum import Enum


class OptimizerType(Enum):
    COBYLA = "cobyla"
    SPSA = "spsa"
    GRADIENT_ASCENT = "gradient_ascent"
    GRID_SEARCH = "grid_search"


@dataclass
class OptimizationResult:
    """Container for optimization results."""
    optimal_params: np.ndarray
    optimal_payoff: float
    history: List[float]
    converged: bool
    iterations: int


class VQAOptimizer:
    """
    Variational Quantum Algorithm optimizer using classical methods.
    Optimizes quantum game parameters to maximize player payoffs.
    """
    
    def __init__(self, optimizer_type: OptimizerType = OptimizerType.COBYLA):
        self.optimizer_type = optimizer_type
        self.history = []
        
    def optimize(self, 
                objective_func: Callable[[np.ndarray], float],
                initial_params: np.ndarray,
                bounds: Optional[List[Tuple[float, float]]] = None,
                max_iterations: int = 100,
                tolerance: float = 1e-6) -> OptimizationResult:
        """
        Run optimization to find optimal quantum parameters.
        
        Args:
            objective_func: Function to maximize (payoff)
            initial_params: Starting parameter values
            bounds: Parameter bounds [(min, max), ...]
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            OptimizationResult with optimal parameters and history
        """
        self.history = []
        
        if self.optimizer_type == OptimizerType.COBYLA:
            return self._optimize_cobyla(objective_func, initial_params, 
                                         bounds, max_iterations, tolerance)
        elif self.optimizer_type == OptimizerType.SPSA:
            return self._optimize_spsa(objective_func, initial_params,
                                       max_iterations, tolerance)
        elif self.optimizer_type == OptimizerType.GRADIENT_ASCENT:
            return self._optimize_gradient_ascent(objective_func, initial_params,
                                                   max_iterations, tolerance)
        elif self.optimizer_type == OptimizerType.GRID_SEARCH:
            return self._optimize_grid_search(objective_func, bounds,
                                               max_iterations)
        else:
            raise ValueError(f"Unknown optimizer type: {self.optimizer_type}")
    
    def _optimize_cobyla(self,
                        objective_func: Callable,
                        initial_params: np.ndarray,
                        bounds: Optional[List[Tuple[float, float]]],
                        max_iterations: int,
                        tolerance: float) -> OptimizationResult:
        """COBYLA optimization (Constrained Optimization BY Linear Approximation)."""
        
        # Convert bounds to constraints for COBYLA
        constraints = []
        if bounds:
            for i, (low, high) in enumerate(bounds):
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda p, i=i, low=low: p[i] - low
                })
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda p, i=i, high=high: high - p[i]
                })
        
        # Callback to track history
        def callback(x):
            self.history.append(objective_func(x))
            
        result = minimize(
            objective_func,
            initial_params,
            method='COBYLA',
            constraints=constraints if constraints else [],
            options={'maxiter': max_iterations, 'rhobeg': 0.5, 'tol': tolerance}
        )
        
        # Handle case where nit is not available
        iterations = getattr(result, 'nit', 0) or 0
        
        return OptimizationResult(
            optimal_params=result.x,
            optimal_payoff=-result.fun,  # Negate because we minimize
            history=self.history,
            converged=result.success,
            iterations=iterations
        )
    
    def _optimize_spsa(self,
                      objective_func: Callable,
                      initial_params: np.ndarray,
                      max_iterations: int,
                      tolerance: float) -> OptimizationResult:
        """
        Simultaneous Perturbation Stochastic Approximation (SPSA).
        Efficient for noisy objective functions.
        """
        
        def spsa_step(params, iteration, a=0.01, c=0.01):
            """Single SPSA update step."""
            # Gradient estimate using simultaneous perturbation
            delta = np.random.choice([-1, 1], size=len(params))
            
            # Perturb parameters
            params_plus = params + c * delta
            params_minus = params - c * delta
            
            # Estimate gradient
            loss_plus = objective_func(params_plus)
            loss_minus = objective_func(params_minus)
            
            gradient_estimate = (loss_plus - loss_minus) / (2 * c * delta)
            
            # Learning rate schedule
            a_k = a / (iteration + 1) ** 0.602
            
            # Update parameters
            new_params = params + a_k * gradient_estimate
            
            # Clip to valid range [0, 2π]
            new_params = np.clip(new_params, 0, 2 * np.pi)
            
            return new_params, (loss_plus + loss_minus) / 2
        
        params = initial_params.copy()
        best_params = params.copy()
        best_payoff = objective_func(params)
        
        for i in range(max_iterations):
            params, current_payoff = spsa_step(params, i)
            self.history.append(current_payoff)
            
            if current_payoff > best_payoff:
                best_payoff = current_payoff
                best_params = params.copy()
                
            # Check convergence
            if i > 10 and abs(self.history[-1] - self.history[-10]) < tolerance:
                break
                
        return OptimizationResult(
            optimal_params=best_params,
            optimal_payoff=best_payoff,
            history=self.history,
            converged=abs(self.history[-1] - self.history[-10]) < tolerance if len(self.history) > 10 else False,
            iterations=i + 1
        )
    
    def _optimize_gradient_ascent(self,
                                  objective_func: Callable,
                                  initial_params: np.ndarray,
                                  max_iterations: int,
                                  tolerance: float) -> OptimizationResult:
        """Simple gradient ascent with numerical differentiation."""
        
        params = initial_params.copy()
        best_params = params.copy()
        best_payoff = objective_func(params)
        learning_rate = 0.1
        
        for i in range(max_iterations):
            # Numerical gradient
            gradient = np.zeros_like(params)
            epsilon = 0.01
            
            for j in range(len(params)):
                params_plus = params.copy()
                params_plus[j] += epsilon
                params_minus = params.copy()
                params_minus[j] -= epsilon
                
                gradient[j] = (objective_func(params_plus) - 
                              objective_func(params_minus)) / (2 * epsilon)
            
            # Update parameters
            params = params + learning_rate * gradient
            params = np.clip(params, 0, 2 * np.pi)
            
            current_payoff = objective_func(params)
            self.history.append(current_payoff)
            
            if current_payoff > best_payoff:
                best_payoff = current_payoff
                best_params = params.copy()
                
            # Check convergence
            if i > 10 and abs(self.history[-1] - self.history[-10]) < tolerance:
                break
                
        return OptimizationResult(
            optimal_params=best_params,
            optimal_payoff=best_payoff,
            history=self.history,
            converged=abs(self.history[-1] - self.history[-10]) < tolerance if len(self.history) > 10 else False,
            iterations=i + 1
        )
    
    def _optimize_grid_search(self,
                             objective_func: Callable,
                             bounds: Optional[List[Tuple[float, float]]],
                             resolution: int = 20) -> OptimizationResult:
        """Grid search optimization."""
        
        if bounds is None:
            bounds = [(0, 2 * np.pi)] * len(self.history) if self.history else [(0, 2 * np.pi)]
            
        # Generate grid
        grids = [np.linspace(low, high, resolution) for low, high in bounds]
        
        best_payoff = float('-inf')
        best_params = None
        
        # Iterate through grid (simplified for 2 players)
        if len(bounds) == 2:
            for theta in grids[0]:
                for phi in grids[1]:
                    params = np.array([theta, phi])
                    payoff = objective_func(params)
                    self.history.append(payoff)
                    
                    if payoff > best_payoff:
                        best_payoff = payoff
                        best_params = params
        else:
            # For more parameters, use random sampling
            for _ in range(resolution * resolution):
                params = np.array([np.random.uniform(low, high) 
                                  for low, high in bounds])
                payoff = objective_func(params)
                self.history.append(payoff)
                
                if payoff > best_payoff:
                    best_payoff = payoff
                    best_params = params
                    
        return OptimizationResult(
            optimal_params=best_params,
            optimal_payoff=best_payoff,
            history=self.history,
            converged=True,
            iterations=len(self.history)
        )


class ClassicalGameOptimizer:
    """
    Classical optimizer for comparison with quantum approach.
    Uses grid search and gradient methods for mixed strategies.
    """
    
    def __init__(self):
        self.history = []
        
    def optimize_mixed_strategy(self,
                               payoff_matrix: np.ndarray,
                               player: int = 0) -> Tuple[float, float]:
        """
        Find optimal mixed strategy for a player given payoff matrix.
        
        Args:
            payoff_matrix: Payoff matrix for the game
            player: Player index (0 or 1)
            
        Returns:
            Optimal probability and expected payoff
        """
        # For 2x2 games, optimize single probability parameter
        best_p = 0
        best_payoff = float('-inf')
        
        for p in np.linspace(0, 1, 101):
            # Mixed strategy: play action 0 with prob p, action 1 with prob (1-p)
            expected_payoff = self._compute_expected_payoff(payoff_matrix, p, player)
            self.history.append(expected_payoff)
            
            if expected_payoff > best_payoff:
                best_payoff = expected_payoff
                best_p = p
                
        return best_p, best_payoff
    
    def _compute_expected_payoff(self,
                                 payoff_matrix: np.ndarray,
                                 p: float,
                                 player: int) -> float:
        """Compute expected payoff for mixed strategy."""
        
        if player == 0:
            # Player 0 plays action 0 with prob p, action 1 with prob (1-p)
            # Player 1 plays both actions with equal probability (0.5, 0.5)
            payoff = p * (0.5 * payoff_matrix[0, 0] + 0.5 * payoff_matrix[0, 1]) + \
                    (1 - p) * (0.5 * payoff_matrix[1, 0] + 0.5 * payoff_matrix[1, 1])
        else:
            # Player 1's perspective
            payoff = p * (0.5 * payoff_matrix[0, 0] + 0.5 * payoff_matrix[1, 0]) + \
                    (1 - p) * (0.5 * payoff_matrix[0, 1] + 0.5 * payoff_matrix[1, 1])
                    
        return payoff
    
    def find_nash_equilibrium(self, 
                             payoff_matrix_p0: np.ndarray,
                             payoff_matrix_p1: np.ndarray) -> Dict[str, Any]:
        """
        Find Nash equilibrium using best response analysis.
        
        Args:
            payoff_matrix_p0: Payoff matrix for player 0
            payoff_matrix_p1: Payoff matrix for player 1
            
        Returns:
            Dictionary with equilibrium strategies and payoffs
        """
        nash_equilibria = []
        
        # Check pure strategies
        for a0 in [0, 1]:
            for a1 in [0, 1]:
                # Check if this is a Nash equilibrium
                p0_payoff = payoff_matrix_p0[a0, a1]
                p1_payoff = payoff_matrix_p1[a0, a1]
                
                # Player 0's best response
                p0_best = max(payoff_matrix_p0[:, a1])
                # Player 1's best response
                p1_best = max(payoff_matrix_p1[a0, :])
                
                if p0_payoff == p0_best and p1_payoff == p1_best:
                    nash_equilibria.append({
                        'strategy': (a0, a1),
                        'payoffs': (p0_payoff, p1_payoff),
                        'type': 'pure'
                    })
                    
        return {
            'equilibria': nash_equilibria,
            'num_equilibria': len(nash_equilibria)
        }


def create_optimizer(optimizer_type: str = "cobyla") -> VQAOptimizer:
    """Factory function to create optimizer."""
    return VQAOptimizer(OptimizerType(optimizer_type))


if __name__ == "__main__":
    # Test optimizer
    optimizer = VQAOptimizer(OptimizerType.COBYLA)
    
    # Simple test function (Rastrigin-like)
    def test_func(params):
        return -np.sum(params**2 - 10*np.cos(2*np.pi*params))
    
    initial = np.array([0.5, 0.5])
    result = optimizer.optimize(test_func, initial, 
                               bounds=[(0, 2*np.pi), (0, 2*np.pi)],
                               max_iterations=50)
    
    print(f"Optimal params: {result.optimal_params}")
    print(f"Optimal payoff: {result.optimal_payoff}")
    print(f"Converged: {result.converged}")
    print(f"Iterations: {result.iterations}")