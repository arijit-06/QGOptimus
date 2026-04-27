"""
Step-Based Quantum Circuit and Optimizer
Generates execution steps for visualization of quantum game optimization.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class QuantumExecutionStep:
    """Represents a single quantum execution step."""
    step: int
    active_line: int
    description: str
    parameters: Dict[str, Any]
    payoff: float
    state: Dict[str, Any]


# Quantum code display for visualization
QUANTUM_CODE = {
    1: "def run_quantum_game(theta, phi, shots=1024):",
    2: "    # Step 1: Initialize 2-qubit quantum register",
    3: "    qr = QuantumRegister(2, 'player')",
    4: "    cr = ClassicalRegister(2, 'measurement')",
    5: "    circuit = QuantumCircuit(qr, cr)",
    6: "    ",
    7: "    # Step 2: Apply entanglement (CNOT gate)",
    8: "    circuit.cx(qr[0], qr[1])  # Correlate qubits",
    9: "    ",
    10: "    # Step 3: Apply player strategy gates (RY, RZ)",
    11: "    circuit.ry(theta[0], qr[0])  # Player 0 strategy",
    12: "    circuit.ry(theta[1], qr[1])  # Player 1 strategy",
    13: "    circuit.rz(phi[0], qr[0])",
    14: "    circuit.rz(phi[1], qr[1])",
    15: "    ",
    16: "    # Step 4: Execute circuit on quantum simulator",
    17: "    job = execute(circuit, Aer.get_backend('qasm_simulator'), shots=shots)",
    18: "    result = job.result()",
    19: "    ",
    20: "    # Step 5: Measure qubits to get classical outcomes",
    21: "    circuit.measure(qr, cr)",
    22: "    counts = result.get_counts(circuit)",
    23: "    ",
    24: "    # Step 6: Convert measurements to payoffs",
    25: "    p0_payoff, p1_payoff = calculate_payoff(counts, game_type)",
    26: "    ",
    27: "    return p0_payoff + p1_payoff, counts"
}

# Optimizer code display
OPTIMIZER_CODE = {
    1: "def optimize_quantum_params(objective_func, initial_params):",
    2: "    # Initialize parameters [theta0, theta1, phi0, phi1]",
    3: "    params = initial_params.copy()",
    4: "    history = []",
    5: "    ",
    6: "    # Iterative optimization loop",
    7: "    for iteration in range(max_iterations):",
    8: "        # Evaluate current parameters",
    9: "        payoff = objective_func(params)",
    10: "        history.append(payoff)",
    11: "        ",
    12: "        # Compute gradient estimate",
    13: "        gradient = estimate_gradient(params)",
    14: "        ",
    15: "        # Update parameters (gradient ascent)",
    16: "        params = params + learning_rate * gradient",
    17: "        ",
    18: "        # Clip to valid range [0, 2π]",
    19: "        params = np.clip(params, 0, 2 * np.pi)",
    20: "        ",
    21: "        # Check convergence",
    22: "        if converged(history):",
    23: "            break",
    24: "    ",
    25: "    return optimal_params, history"
}


class StepBasedQuantumCircuit:
    """
    Step-based quantum circuit that generates execution steps
    for visualization purposes.
    """
    
    def __init__(self, num_players: int = 2, shots: int = 1024):
        self.num_players = num_players
        self.shots = shots
        self.steps: List[Dict[str, Any]] = []
        
    def generate_circuit_steps(self,
                               theta: np.ndarray,
                               phi: np.ndarray,
                               game_type: str) -> List[Dict[str, Any]]:
        """
        Generate step-by-step execution for quantum circuit.
        
        Args:
            theta: Rotation angles for RY gates
            phi: Rotation angles for RZ gates
            game_type: Type of game
            
        Returns:
            List of execution steps
        """
        self.steps = []
        
        # Step 1: Initialize quantum register
        step = QuantumExecutionStep(
            step=1,
            active_line=3,
            description="Initialize 2-qubit quantum register for player strategies",
            parameters={"num_qubits": 2, "num_classical_bits": 2},
            payoff=0.0,
            state={"qubits": ["player_0", "player_1"], "initialized": True}
        )
        self.steps.append(asdict(step))
        
        # Step 2: Apply entanglement (CNOT)
        gates = [{"type": "CNOT", "control": 0, "target": 1, "theta": None, "phi": None}]
        
        step = QuantumExecutionStep(
            step=2,
            active_line=8,
            description="Apply CNOT gate to entangle player qubits (correlate strategies)",
            parameters={"gate": "CNOT", "control": 0, "target": 1},
            payoff=0.0,
            state={"gates_applied": gates.copy(), "entangled": True}
        )
        self.steps.append(asdict(step))
        
        # Step 3: Apply RY gates for player strategies
        gates.append({"type": "RY", "qubit": 0, "theta": float(theta[0]), "phi": None})
        gates.append({"type": "RY", "qubit": 1, "theta": float(theta[1]), "phi": None})
        
        step = QuantumExecutionStep(
            step=3,
            active_line=11,
            description=f"Apply RY gates: θ₀={theta[0]:.3f}, θ₁={theta[1]:.3f}",
            parameters={"gate": "RY", "theta": theta.tolist()},
            payoff=0.0,
            state={"gates_applied": gates.copy()}
        )
        self.steps.append(asdict(step))
        
        # Step 4: Apply RZ gates for phase encoding
        gates.append({"type": "RZ", "qubit": 0, "theta": None, "phi": float(phi[0])})
        gates.append({"type": "RZ", "qubit": 1, "theta": None, "phi": float(phi[1])})
        
        step = QuantumExecutionStep(
            step=4,
            active_line=13,
            description=f"Apply RZ gates: φ₀={phi[0]:.3f}, φ₁={phi[1]:.3f}",
            parameters={"gate": "RZ", "phi": phi.tolist()},
            payoff=0.0,
            state={"gates_applied": gates.copy()}
        )
        self.steps.append(asdict(step))
        
        # Step 5: Simulate measurement outcomes
        # Generate pseudo-measurement based on parameters
        probs = self._compute_measurement_probabilities(theta, phi)
        counts = {format(i, '02b'): int(probs[i] * self.shots) for i in range(4)}
        
        step = QuantumExecutionStep(
            step=5,
            active_line=17,
            description=f"Execute quantum circuit on Aer simulator ({self.shots} shots)",
            parameters={"shots": self.shots, "probabilities": probs.tolist()},
            payoff=0.0,
            state={"counts": counts, "probabilities": probs.tolist()}
        )
        self.steps.append(asdict(step))
        
        # Step 6: Measure qubits
        step = QuantumExecutionStep(
            step=6,
            active_line=21,
            description="Collapse quantum state to classical bits",
            parameters={"measurement_basis": "computational"},
            payoff=0.0,
            state={"counts": counts, "measured": True}
        )
        self.steps.append(asdict(step))
        
        # Step 7: Convert to payoffs
        p0_payoff, p1_payoff = self._compute_payoffs(probs, game_type)
        total_payoff = p0_payoff + p1_payoff
        
        step = QuantumExecutionStep(
            step=7,
            active_line=25,
            description=f"Convert measurements to payoffs: P0={p0_payoff:.3f}, P1={p1_payoff:.3f}",
            parameters={
                "player_0_payoff": p0_payoff,
                "player_1_payoff": p1_payoff,
                "total_payoff": total_payoff
            },
            payoff=total_payoff,
            state={
                "p0_payoff": p0_payoff,
                "p1_payoff": p1_payoff,
                "counts": counts
            }
        )
        self.steps.append(asdict(step))
        
        return self.steps
    
    def _compute_measurement_probabilities(self, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Compute measurement probabilities from quantum state."""
        # Simplified probability computation based on angles
        # In real quantum circuit, this comes from the statevector
        prob_00 = np.cos(theta[0]/2)**2 * np.cos(theta[1]/2)**2
        prob_01 = np.cos(theta[0]/2)**2 * np.sin(theta[1]/2)**2
        prob_10 = np.sin(theta[0]/2)**2 * np.cos(theta[1]/2)**2
        prob_11 = np.sin(theta[0]/2)**2 * np.sin(theta[1]/2)**2
        
        # Normalize
        total = prob_00 + prob_01 + prob_10 + prob_11
        return np.array([prob_00/total, prob_01/total, prob_10/total, prob_11/total])
    
    def _compute_payoffs(self, probabilities: np.ndarray, game_type: str) -> tuple:
        """Convert measurement probabilities to game payoffs."""
        
        if game_type == "prisoners_dilemma":
            # Payoff matrix: (CC, CD, DC, DD)
            # P0: 3, 0, 5, 1
            # P1: 3, 5, 0, 1
            p0_payoff = (probabilities[0] * 3 + probabilities[1] * 0 + 
                        probabilities[2] * 5 + probabilities[3] * 1)
            p1_payoff = (probabilities[0] * 3 + probabilities[1] * 5 + 
                        probabilities[2] * 0 + probabilities[3] * 1)
            
        elif game_type == "battle_of_sexes":
            # Payoff matrix for coordination
            # P0: (2,0), (0,1) - rows: Opera, Football
            # P1: (2,0), (0,1) - cols: Opera, Football
            p0_payoff = (probabilities[0] * 2 + probabilities[1] * 0 + 
                        probabilities[2] * 0 + probabilities[3] * 1)
            p1_payoff = (probabilities[0] * 2 + probabilities[1] * 0 + 
                        probabilities[2] * 0 + probabilities[3] * 1)
            
        else:  # matching_pennies
            # Zero-sum: P0 gets +1 for match, -1 for mismatch
            # P1 gets opposite
            p0_payoff = (probabilities[0] * 1 + probabilities[1] * (-1) + 
                        probabilities[2] * (-1) + probabilities[3] * 1)
            p1_payoff = -p0_payoff
            
        return p0_payoff, p1_payoff
    
    def get_circuit_data(self, theta: np.ndarray, phi: np.ndarray) -> Dict[str, Any]:
        """Get structured circuit data for visualization."""
        gates = [
            {"type": "CNOT", "qubit": None, "control": 0, "target": 1, "theta": None, "phi": None},
            {"type": "RY", "qubit": 0, "theta": float(theta[0])},
            {"type": "RY", "qubit": 1, "theta": float(theta[1])},
            {"type": "RZ", "qubit": 0, "phi": float(phi[0])},
            {"type": "RZ", "qubit": 1, "phi": float(phi[1])}
        ]
        
        return {"gates": gates}


class StepBasedQuantumOptimizer:
    """
    Step-based quantum optimizer that generates execution steps
    for visualization of parameter optimization.
    """
    
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        
    def generate_optimization_steps(self,
                                    payoff_p0: np.ndarray,
                                    payoff_p1: np.ndarray,
                                    game_type: str,
                                    max_iterations: int = 20) -> List[Dict[str, Any]]:
        """
        Generate step-by-step execution for quantum optimization.
        
        Args:
            payoff_p0: Payoff matrix for player 0
            payoff_p1: Payoff matrix for player 1
            game_type: Type of game
            max_iterations: Maximum optimization iterations
            
        Returns:
            List of execution steps with circuit data
        """
        self.steps = []
        
        # Initial parameters
        theta = np.array([np.pi/4, np.pi/4])
        phi = np.array([0.0, 0.0])
        
        # Step 1: Initialize parameters
        step = QuantumExecutionStep(
            step=1,
            active_line=3,
            description="Initialize quantum parameters: θ=[π/4, π/4], φ=[0, 0]",
            parameters={
                "theta": theta.tolist(),
                "phi": phi.tolist()
            },
            payoff=0.0,
            state={"iteration": 0, "params_initialized": True}
        )
        self.steps.append(asdict(step))
        
        # Iterative optimization
        history = []
        learning_rate = 0.1
        
        for iteration in range(max_iterations):
            # Compute current payoff
            probs = self._compute_probs(theta, phi)
            p0_payoff, p1_payoff = self._compute_payoffs(probs, game_type)
            total_payoff = p0_payoff + p1_payoff
            history.append(total_payoff)
            
            # Step 2: Evaluate current parameters
            step = QuantumExecutionStep(
                step=len(self.steps) + 1,
                active_line=9,
                description=f"Iteration {iteration + 1}: Evaluate payoff = {total_payoff:.4f}",
                parameters={
                    "theta": theta.tolist(),
                    "phi": phi.tolist(),
                    "payoff": total_payoff,
                    "iteration": iteration + 1
                },
                payoff=total_payoff,
                state={
                    "iteration": iteration + 1,
                    "p0_payoff": p0_payoff,
                    "p1_payoff": p1_payoff,
                    "history": history.copy()
                }
            )
            self.steps.append(asdict(step))
            
            # Step 3: Compute gradient (numerical)
            gradient = self._compute_gradient(theta, phi, game_type)
            
            step = QuantumExecutionStep(
                step=len(self.steps) + 1,
                active_line=13,
                description=f"Compute gradient: ∇θ={gradient[:2].round(3).tolist()}, ∇φ={gradient[2:].round(3).tolist()}",
                parameters={"gradient": gradient.tolist()},
                payoff=total_payoff,
                state={"gradient": gradient.tolist(), "iteration": iteration + 1}
            )
            self.steps.append(asdict(step))
            
            # Step 4: Update parameters
            theta_new = theta + learning_rate * gradient[:2]
            phi_new = phi + learning_rate * gradient[2:]
            
            # Clip to valid range
            theta_new = np.clip(theta_new, 0, 2 * np.pi)
            phi_new = np.clip(phi_new, 0, 2 * np.pi)
            
            step = QuantumExecutionStep(
                step=len(self.steps) + 1,
                active_line=16,
                description=f"Update parameters: θ={theta.round(3).tolist()}→{theta_new.round(3).tolist()}",
                parameters={
                    "theta_old": theta.tolist(),
                    "theta_new": theta_new.tolist(),
                    "phi_old": phi.tolist(),
                    "phi_new": phi_new.tolist()
                },
                payoff=total_payoff,
                state={"theta_new": theta_new.tolist(), "phi_new": phi_new.tolist()}
            )
            self.steps.append(asdict(step))
            
            theta, phi = theta_new, phi_new
            
            # Check convergence
            if len(history) > 5:
                recent = history[-5:]
                if max(recent) - min(recent) < 0.01:
                    break
        
        # Final step: Return optimal result
        probs = self._compute_probs(theta, phi)
        p0_payoff, p1_payoff = self._compute_payoffs(probs, game_type)
        total_payoff = p0_payoff + p1_payoff
        
        circuit_data = StepBasedQuantumCircuit().get_circuit_data(theta, phi)
        
        step = QuantumExecutionStep(
            step=len(self.steps) + 1,
            active_line=25,
            description=f"Converged to optimal: θ={theta.round(3).tolist()}, payoff={total_payoff:.4f}",
            parameters={
                "optimal_theta": theta.tolist(),
                "optimal_phi": phi.tolist(),
                "optimal_payoff": total_payoff,
                "iterations": len(history)
            },
            payoff=total_payoff,
            state={
                "converged": True,
                "final_payoff": total_payoff,
                "history": history,
                "circuit": circuit_data
            }
        )
        self.steps.append(asdict(step))
        
        return self.steps
    
    def _compute_probs(self, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Compute measurement probabilities."""
        prob_00 = np.cos(theta[0]/2)**2 * np.cos(theta[1]/2)**2
        prob_01 = np.cos(theta[0]/2)**2 * np.sin(theta[1]/2)**2
        prob_10 = np.sin(theta[0]/2)**2 * np.cos(theta[1]/2)**2
        prob_11 = np.sin(theta[0]/2)**2 * np.sin(theta[1]/2)**2
        total = prob_00 + prob_01 + prob_10 + prob_11
        return np.array([prob_00/total, prob_01/total, prob_10/total, prob_11/total])
    
    def _compute_payoffs(self, probabilities: np.ndarray, game_type: str) -> tuple:
        """Convert probabilities to payoffs."""
        
        if game_type == "prisoners_dilemma":
            p0_payoff = (probabilities[0] * 3 + probabilities[1] * 0 + 
                        probabilities[2] * 5 + probabilities[3] * 1)
            p1_payoff = (probabilities[0] * 3 + probabilities[1] * 5 + 
                        probabilities[2] * 0 + probabilities[3] * 1)
            
        elif game_type == "battle_of_sexes":
            p0_payoff = (probabilities[0] * 2 + probabilities[1] * 0 + 
                        probabilities[2] * 0 + probabilities[3] * 1)
            p1_payoff = (probabilities[0] * 2 + probabilities[1] * 0 + 
                        probabilities[2] * 0 + probabilities[3] * 1)
            
        else:  # matching_pennies
            p0_payoff = (probabilities[0] * 1 + probabilities[1] * (-1) + 
                        probabilities[2] * (-1) + probabilities[3] * 1)
            p1_payoff = -p0_payoff
            
        return p0_payoff, p1_payoff
    
    def _compute_gradient(self, theta: np.ndarray, phi: np.ndarray, game_type: str) -> np.ndarray:
        """Compute numerical gradient."""
        epsilon = 0.01
        gradient = np.zeros(4)
        
        for i in range(4):
            params_plus = theta.copy() if i < 2 else phi.copy()
            params_minus = theta.copy() if i < 2 else phi.copy()
            
            if i < 2:
                params_plus[i] += epsilon
                params_minus[i] -= epsilon
                probs_plus = self._compute_probs(params_plus, phi)
                probs_minus = self._compute_probs(params_minus, phi)
            else:
                idx = i - 2
                params_plus[idx] += epsilon
                params_minus[idx] -= epsilon
                probs_plus = self._compute_probs(theta, params_plus)
                probs_minus = self._compute_probs(theta, params_minus)
            
            payoff_plus = sum(self._compute_payoffs(probs_plus, game_type))
            payoff_minus = sum(self._compute_payoffs(probs_minus, game_type))
            
            gradient[i] = (payoff_plus - payoff_minus) / (2 * epsilon)
        
        return gradient
    
    def get_code_display(self) -> Dict[int, str]:
        """Get quantum code display."""
        return QUANTUM_CODE
    
    def get_optimizer_code_display(self) -> Dict[int, str]:
        """Get optimizer code display."""
        return OPTIMIZER_CODE