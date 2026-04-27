"""
Quantum Measurement and State Analysis
Handles measurement, probability distributions, and visualization.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class MeasurementResult:
    """Container for measurement results."""
    counts: Dict[str, int]
    probabilities: Dict[str, float]
    expectation_values: Dict[str, float]
    entropy: float


class QuantumMeasurement:
    """
    Handles quantum measurements and state analysis.
    Provides probability distributions, histograms, and state analysis.
    """
    
    def __init__(self, shots: int = 1024):
        self.shots = shots
        
    def measure(self, counts: Dict[str, int]) -> MeasurementResult:
        """
        Process measurement counts into probabilities and analysis.
        
        Args:
            counts: Raw measurement counts from Qiskit
            
        Returns:
            MeasurementResult with processed data
        """
        total = sum(counts.values())
        probabilities = {state: count / total for state, count in counts.items()}
        
        # Calculate expectation values for Pauli operators
        expectation_values = self._calculate_expectation_values(probabilities)
        
        # Calculate von Neumann entropy
        entropy = self._calculate_entropy(probabilities)
        
        return MeasurementResult(
            counts=counts,
            probabilities=probabilities,
            expectation_values=expectation_values,
            entropy=entropy
        )
    
    def _calculate_expectation_values(self, 
                                      probabilities: Dict[str, float]) -> Dict[str, float]:
        """Calculate expectation values for Z basis measurements."""
        
        exp_z = 0.0
        exp_x = 0.0
        exp_y = 0.0
        
        for state, prob in probabilities.items():
            # Z expectation: |0> -> +1, |1> -> -1
            z_value = 1 if state == '0' * len(state) else -1
            exp_z += prob * z_value
            
            # For X and Y, we need to consider superposition states
            # This is simplified - full calculation would require statevector
            
        return {
            'Z': exp_z,
            'X': exp_x,
            'Y': exp_y
        }
    
    def _calculate_entropy(self, probabilities: Dict[str, float]) -> float:
        """Calculate Shannon entropy of measurement distribution."""
        entropy = 0.0
        for prob in probabilities.values():
            if prob > 0:
                entropy -= prob * np.log2(prob)
        return entropy
    
    def get_probability_histogram(self, 
                                  probabilities: Dict[str, float],
                                  title: str = "Measurement Probabilities") -> str:
        """
        Generate probability histogram as base64 PNG.
        
        Args:
            probabilities: State -> probability mapping
            title: Plot title
            
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        states = list(probabilities.keys())
        probs = list(probabilities.values())
        
        # Sort states for consistent display
        sorted_indices = np.argsort([int(s, 2) for s in states])
        states = [states[i] for i in sorted_indices]
        probs = [probs[i] for i in sorted_indices]
        
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(states)))
        
        bars = ax.bar(states, probs, color=colors, edgecolor='black', linewidth=1.2)
        
        ax.set_xlabel('Quantum State', fontsize=12)
        ax.set_ylabel('Probability', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(probs) * 1.2 if probs else 1)
        
        # Add value labels on bars
        for bar, prob in zip(bars, probs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{prob:.3f}',
                   ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_base64
    
    def get_convergence_plot(self,
                            history: List[float],
                            title: str = "Optimization Convergence") -> str:
        """
        Generate convergence plot as base64 PNG.
        
        Args:
            history: List of payoff values over iterations
            title: Plot title
            
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        iterations = range(1, len(history) + 1)
        
        ax.plot(iterations, history, 'b-', linewidth=2, label='Payoff')
        ax.fill_between(iterations, history, alpha=0.3)
        
        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Payoff', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Mark optimal point
        if history:
            max_idx = np.argmax(history)
            ax.scatter([max_idx + 1], [history[max_idx]], 
                      color='red', s=100, zorder=5, label='Optimal')
            ax.annotate(f'Max: {history[max_idx]:.3f}',
                       xy=(max_idx + 1, history[max_idx]),
                       xytext=(max_idx + 5, history[max_idx]),
                       arrowprops=dict(arrowstyle='->', color='red'),
                       fontsize=10)
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_base64
    
    def get_comparison_plot(self,
                           classical_payoff: float,
                           quantum_payoff: float,
                           game_name: str = "Game") -> str:
        """
        Generate comparison plot between classical and quantum results.
        
        Args:
            classical_payoff: Classical optimal payoff
            quantum_payoff: Quantum optimal payoff
            game_name: Name of the game
            
        Returns:
            Base64 encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        methods = ['Classical', 'Quantum']
        payoffs = [classical_payoff, quantum_payoff]
        colors = ['#3498db', '#e74c3c']
        
        bars = ax.bar(methods, payoffs, color=colors, edgecolor='black', 
                     linewidth=1.5, width=0.6)
        
        ax.set_ylabel('Payoff', fontsize=12)
        ax.set_title(f'{game_name}: Classical vs Quantum', 
                    fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar, payoff in zip(bars, payoffs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{payoff:.3f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Add advantage indicator
        if quantum_payoff > classical_payoff:
            advantage = ((quantum_payoff - classical_payoff) / 
                        abs(classical_payoff) * 100) if classical_payoff != 0 else 0
            ax.text(0.5, max(payoffs) * 0.9,
                   f'Quantum Advantage: +{advantage:.1f}%',
                   ha='center', fontsize=11, color='green',
                   fontweight='bold')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_base64
    
    def get_bloch_sphere_plot(self,
                             bloch_coords: List[Dict[str, float]],
                             player_names: List[str] = None) -> str:
        """
        Generate Bloch sphere visualization.
        
        Args:
            bloch_coords: List of {x, y, z} coordinates for each qubit
            player_names: Names for each player
            
        Returns:
            Base64 encoded PNG image
        """
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw Bloch sphere wireframe
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x_sphere = np.outer(np.cos(u), np.sin(v))
        y_sphere = np.outer(np.sin(u), np.sin(v))
        z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
        
        ax.plot_wireframe(x_sphere, y_sphere, z_sphere, 
                         color='gray', alpha=0.2, linewidth=0.5)
        
        # Draw axes
        ax.quiver(0, 0, 0, 1.5, 0, 0, color='red', alpha=0.5, arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 1.5, 0, color='green', alpha=0.5, arrow_length_ratio=0.1)
        ax.quiver(0, 0, 0, 0, 0, 1.5, color='blue', alpha=0.5, arrow_length_ratio=0.1)
        
        ax.text(1.6, 0, 0, 'X', color='red', fontsize=12)
        ax.text(0, 1.6, 0, 'Y', color='green', fontsize=12)
        ax.text(0, 0, 1.6, 'Z', color='blue', fontsize=12)
        
        # Plot qubit states
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6']
        for i, coords in enumerate(bloch_coords):
            name = player_names[i] if player_names else f'Player {i}'
            ax.quiver(0, 0, 0, coords['x'], coords['y'], coords['z'],
                     color=colors[i % len(colors)], arrow_length_ratio=0.1,
                     linewidth=3, label=name)
            ax.scatter([coords['x']], [coords['y']], [coords['z']],
                      color=colors[i % len(colors)], s=100)
        
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_zlim([-1.5, 1.5])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Bloch Sphere Representation', fontsize=14, fontweight='bold')
        ax.legend()
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return img_base64
    
    def analyze_quantum_advantage(self,
                                  classical_result: Dict,
                                  quantum_result: Dict) -> Dict[str, Any]:
        """
        Analyze and quantify quantum advantage.
        
        Args:
            classical_result: Classical optimization result
            quantum_result: Quantum optimization result
            
        Returns:
            Dictionary with advantage metrics
        """
        classical_payoff = classical_result.get('optimal_payoff', 0)
        quantum_payoff = quantum_result.get('optimal_payoff', 0)
        
        if classical_payoff == 0:
            advantage_percent = 0 if quantum_payoff == 0 else 100
        else:
            advantage_percent = ((quantum_payoff - classical_payoff) / 
                                abs(classical_payoff) * 100)
        
        return {
            'classical_payoff': classical_payoff,
            'quantum_payoff': quantum_payoff,
            'advantage': quantum_payoff - classical_payoff,
            'advantage_percent': advantage_percent,
            'has_advantage': quantum_payoff > classical_payoff,
            'explanation': self._generate_advantage_explanation(
                classical_payoff, quantum_payoff
            )
        }
    
    def _generate_advantage_explanation(self,
                                        classical: float,
                                        quantum: float) -> str:
        """Generate human-readable explanation of quantum advantage."""
        
        if quantum > classical:
            return (f"Quantum strategy achieves payoff {quantum:.3f} vs "
                   f"classical {classical:.3f}, demonstrating quantum advantage "
                   f"through quantum entanglement and superposition.")
        elif quantum == classical:
            return ("Quantum and classical strategies achieve equivalent payoffs. "
                   "This game may not show quantum advantage.")
        else:
            return (f"Classical strategy outperforms quantum in this case. "
                   f"Classical: {classical:.3f}, Quantum: {quantum:.3f}")


def create_measurement(shots: int = 1024) -> QuantumMeasurement:
    """Factory function to create measurement handler."""
    return QuantumMeasurement(shots)


if __name__ == "__main__":
    # Test measurement
    measurement = QuantumMeasurement(shots=1000)
    
    # Test counts
    test_counts = {'00': 512, '01': 256, '10': 128, '11': 104}
    result = measurement.measure(test_counts)
    
    print("Counts:", result.counts)
    print("Probabilities:", result.probabilities)
    print("Entropy:", result.entropy)
    
    # Test histogram generation
    hist = measurement.get_probability_histogram(result.probabilities)
    print(f"\nHistogram generated: {len(hist)} characters")