"""
Quantum Circuit Implementation for Game Theory
Uses Qiskit to build parameterized quantum circuits for game strategies.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from typing import Tuple, Dict, Any, Optional
import base64
from io import BytesIO


class QuantumGameCircuit:
    """
    Quantum circuit for game theory applications.
    Each player is represented by a qubit, and strategies are 
    parameterized by quantum gates (RY, RZ).
    """
    
    def __init__(self, num_players: int = 2, shots: int = 1024):
        """
        Initialize the quantum game circuit.
        
        Args:
            num_players: Number of players (qubits)
            shots: Number of measurement shots
        """
        self.num_players = num_players
        self.shots = shots
        self.theta = ParameterVector('theta', num_players)  # RY angles
        self.phi = ParameterVector('phi', num_players)      # RZ angles
        
    def create_initial_state(self) -> QuantumCircuit:
        """
        Create the initial entangled state using Bell state.
        This represents the quantum correlation between players.
        """
        qc = QuantumCircuit(self.num_players)
        
        # Start with Hadamard on first qubit for superposition
        qc.h(0)
        
        # Create entanglement (Bell state) between all qubits
        for i in range(1, self.num_players):
            qc.cx(0, i)
            
        return qc
    
    def apply_strategy_gates(self, qc: QuantumCircuit, 
                            theta_params: np.ndarray, 
                            phi_params: np.ndarray) -> QuantumCircuit:
        """
        Apply player strategy gates using RY and RZ rotations.
        
        Args:
            qc: Quantum circuit to modify
            theta_params: RY rotation angles for each player
            phi_params: RZ rotation angles for each player
            
        Returns:
            Modified quantum circuit
        """
        for i in range(self.num_players):
            # Apply RY gate for strategy parameter
            qc.ry(theta_params[i], i)
            # Apply RZ gate for phase parameter
            qc.rz(phi_params[i], i)
            
        return qc
    
    def apply_entanglement_layer(self, qc: QuantumCircuit) -> QuantumCircuit:
        """
        Apply additional entanglement layer between qubits.
        Uses CNOT gates in a ring pattern.
        """
        for i in range(self.num_players):
            qc.cx(i, (i + 1) % self.num_players)
        return qc
    
    def build_circuit(self, theta_params: np.ndarray, 
                     phi_params: np.ndarray) -> QuantumCircuit:
        """
        Build the complete quantum circuit for the game.
        
        Pipeline:
        1. Initialize entangled state
        2. Apply player strategy gates
        3. Apply disentangling (reverse entanglement)
        
        Args:
            theta_params: RY angles for each player
            phi_params: RZ angles for each player
            
        Returns:
            Complete quantum circuit
        """
        qc = self.create_initial_state()
        
        # Apply entanglement layer
        qc = self.apply_entanglement_layer(qc)
        
        # Apply player strategy gates
        qc = self.apply_strategy_gates(qc, theta_params, phi_params)
        
        # Apply disentangling (reverse the entanglement)
        for i in range(self.num_players - 1, 0, -1):
            qc.cx(0, i)
        qc.h(0)
        
        return qc
    
    def get_circuit_diagram(self, theta_params: np.ndarray, 
                           phi_params: np.ndarray) -> str:
        """
        Generate ASCII circuit diagram.
        """
        qc = self.build_circuit(theta_params, phi_params)
        return qc.draw(output='text', fold=80)
    
    def get_mpl_circuit(self, theta_params: np.ndarray, 
                       phi_params: np.ndarray) -> str:
        """
        Generate matplotlib circuit diagram as base64 PNG.
        """
        import matplotlib.pyplot as plt
        
        qc = self.build_circuit(theta_params, phi_params)
        
        fig = qc.draw(output='mpl', style={'backgroundcolor': '#ffffff'})
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_base64
    
    def simulate(self, theta_params: np.ndarray, 
                phi_params: np.ndarray,
                backend: Optional[Any] = None) -> Dict[str, Any]:
        """
        Run quantum simulation and return measurement results.
        
        Args:
            theta_params: RY angles for each player
            phi_params: RZ angles for each player
            backend: Qiskit backend (default: Aer simulator)
            
        Returns:
            Dictionary with measurement counts, probabilities, statevector
        """
        from qiskit_aer import AerSimulator
        
        if backend is None:
            backend = AerSimulator()
            
        qc = self.build_circuit(theta_params, phi_params)
        qc.measure_all()
        
        # Run simulation
        result = backend.run(qc, shots=self.shots).result()
        counts = result.get_counts()
        
        # Get statevector for analysis
        qc_no_measure = self.build_circuit(theta_params, phi_params)
        statevector = Statevector(qc_no_measure)
        
        # Calculate probabilities
        probs = {}
        for state, count in counts.items():
            probs[state] = count / self.shots
            
        return {
            'counts': counts,
            'probabilities': probs,
            'statevector': statevector,
            'num_qubits': self.num_players
        }
    
    def get_bloch_coordinates(self, theta: float, phi: float) -> Dict[str, float]:
        """
        Calculate Bloch sphere coordinates from angles.
        
        Args:
            theta: RY angle
            phi: RZ angle
            
        Returns:
            Dictionary with x, y, z coordinates
        """
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)
        
        return {'x': x, 'y': y, 'z': z}
    
    def get_state_analysis(self, theta_params: np.ndarray, 
                          phi_params: np.ndarray) -> Dict[str, Any]:
        """
        Analyze the quantum state and return Bloch coordinates for each player.
        """
        qc = self.build_circuit(theta_params, phi_params)
        statevector = Statevector(qc)
        
        bloch_coords = []
        for i in range(self.num_players):
            # Calculate expectation values
            x_exp = statevector.expectation_value(
                f"I{'-' * i}X{'-' * (self.num_players - i - 1)}"
            )
            y_exp = statevector.expectation_value(
                f"I{'-' * i}Y{'-' * (self.num_players - i - 1)}"
            )
            z_exp = statevector.expectation_value(
                f"I{'-' * i}Z{'-' * (self.num_players - i - 1)}"
            )
            
            bloch_coords.append({
                'player': i,
                'x': float(x_exp),
                'y': float(y_exp),
                'z': float(z_exp)
            })
            
        return {
            'bloch_coordinates': bloch_coords,
            'statevector': statevector
        }


class ParameterizedGameCircuit(QuantumGameCircuit):
    """
    Extended circuit with additional variational layers for VQA.
    """
    
    def __init__(self, num_players: int = 2, shots: int = 1024, 
                 num_layers: int = 2):
        super().__init__(num_players, shots)
        self.num_layers = num_layers
        
    def build_vqa_circuit(self, params: np.ndarray) -> QuantumCircuit:
        """
        Build variational quantum circuit with multiple layers.
        
        Args:
            params: Flattened parameter array [theta0, phi0, theta1, phi1, ...] 
                   for each layer
        """
        qc = QuantumCircuit(self.num_players)
        
        # Initial state
        qc.h(range(self.num_players))
        
        param_idx = 0
        for layer in range(self.num_layers):
            # Entanglement layer
            for i in range(self.num_players):
                qc.cx(i, (i + 1) % self.num_players)
            
            # Parameterized gates for each qubit
            for i in range(self.num_players):
                theta = params[param_idx] if param_idx < len(params) else 0
                phi = params[param_idx + 1] if param_idx + 1 < len(params) else 0
                param_idx += 2
                
                qc.ry(theta, i)
                qc.rz(phi, i)
                
        return qc


def create_game_circuit(game_type: str, num_players: int = 2) -> QuantumGameCircuit:
    """
    Factory function to create appropriate circuit for game type.
    """
    return QuantumGameCircuit(num_players=num_players)


if __name__ == "__main__":
    # Test the circuit
    circuit = QuantumGameCircuit(num_players=2)
    
    # Test parameters
    theta = np.array([np.pi/4, np.pi/4])
    phi = np.array([0, 0])
    
    # Build and display circuit
    print("Quantum Game Circuit:")
    print(circuit.get_circuit_diagram(theta, phi))
    
    # Run simulation
    result = circuit.simulate(theta, phi)
    print("\nMeasurement Results:")
    print(result['counts'])
    print("\nProbabilities:")
    print(result['probabilities'])