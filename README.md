# QGOptimus - Quantum vs Classical Game Optimization

<p align="center">
  <img src="https://img.shields.io/badge/Quantum-Game%20Theory-blue" alt="Quantum Game Theory">
  <img src="https://img.shields.io/badge/Framework-FastAPI%20%2B%20React-green" alt="Framework">
  <img src="https://img.shields.io/badge/Qiskit-VQA-orange" alt="Qiskit">
</p>

QGOptimus is a research-grade platform that compares **classical** and **quantum** approaches to solving game theory problems. It uses **Variational Quantum Algorithms (VQA)** to find optimal strategies in classic games like the Prisoner's Dilemma, demonstrating how quantum entanglement can enable cooperative outcomes where classical game theory predicts conflict.

---

## Table of Contents

- [The Quantum Advantage](#the-quantum-advantage)
- [Quantum Algorithms Explained](#quantum-algorithms-explained)
  - [Parameterized Quantum Circuits](#parameterized-quantum-circuits)
  - [Variational Quantum Algorithms](#variational-quantum-algorithms)
  - [Entanglement for Strategy Correlation](#entanglement-for-strategy-correlation)
- [Project Architecture](#project-architecture)
- [Quantum Code Showcase](#quantum-code-showcase)
- [Classical Implementation](#classical-implementation)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Frontend Features](#frontend-features)
- [Supported Games](#supported-games)

---

## The Quantum Advantage

In classical game theory, the **Prisoner's Dilemma** has a dominant strategy of Defection — both players lose because they can't coordinate. However, quantum strategies using **entangled states** and **superposition** can break this deadlock.

### Classical vs Quantum Outcomes

| Aspect | Classical | Quantum |
|--------|-----------|---------|
| **Prisoner's Dilemma** | (Defect, Defect) → 1+1 | (Cooperate, Cooperate) via entanglement |
| **Strategy Space** | Discrete actions only | Continuous parameterized rotations |
| **Correlation** | None (separate decisions) | Entangled quantum state |
| **Equilibrium** | Nash equilibrium | Quantum equilibrium |

---

## Quantum Algorithms Explained

### Parameterized Quantum Circuits

The core of our quantum approach uses **parameterized quantum circuits (PQC)** where each player's strategy is encoded as quantum gate rotations:

```python
# filepath: backend/quantum/circuit.py
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
```

**Key Concepts:**
- **RY gates** encode the "strategy" (cooperation vs defection probability)
- **RZ gates** encode phase information for quantum interference
- Each player is represented by a **qubit** (quantum bit)

### Variational Quantum Algorithms

We use **VQA** — a hybrid quantum-classical approach where:
1. A quantum circuit prepares a parameterized state
2. Measurements yield a cost function (payoff)
3. Classical optimizer adjusts parameters to maximize payoff

```python
# filepath: backend/quantum/optimizer.py
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
        # ... optimization logic
```

**Supported Optimizers:**
- **COBYLA** - Constrained Optimization BY Linear Approximation
- **SPSA** - Simultaneous Perturbation Stochastic Approximation (noisy)
- **Gradient Ascent** - Simple gradient-based optimization
- **Grid Search** - Exhaustive parameter search

### Entanglement for Strategy Correlation

The quantum circuit creates **Bell states** — maximally entangled qubit pairs that allow players to coordinate without direct communication:

```python
# filepath: backend/quantum/circuit.py
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
```

**The Magic:** When players measure their entangled qubits, the outcomes are correlated — if one "defects", the other can "cooperate" in a way that benefits both, breaking the classical dilemma.

---

## Project Architecture

```
QGOptimus/
├── backend/
│   ├── main.py                    # FastAPI server
│   ├── requirements.txt           # Python dependencies
│   ├── quantum/
│   │   ├── circuit.py            # Parameterized quantum circuits
│   │   ├── optimizer.py          # VQA optimization (COBYLA, SPSA)
│   │   ├── measurement.py        # Quantum measurement & analysis
│   │   └── step_optimizer.py     # Step-by-step execution visualization
│   ├── classical/
│   │   ├── solver.py             # Classical game theory solver
│   │   └── step_solver.py        # Classical step execution
│   └── games/
│       ├── prisoners_dilemma.py  # Prisoner's Dilemma
│       ├── battle_of_sexes.py    # Battle of the Sexes
│       └── matching_pennies.py   # Matching Pennies
│
└── frontend/
    ├── src/
    │   ├── App.jsx               # Main React application
    │   ├── components/
    │   │   └── ParticleBackground.jsx  # Visual effects
    │   └── index.css
    ├── index.html
    └── package.json
```

---

## Quantum Code Showcase

### Complete Quantum Circuit Builder

```python
# filepath: backend/quantum/circuit.py
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
```

### Quantum Measurement Analysis

```python
# filepath: backend/quantum/measurement.py
class QuantumMeasurement:
    """
    Handles quantum measurements and state analysis.
    Provides probability distributions, histograms, and state analysis.
    """
    
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
```

### SPSA Optimization (Noisy Quantum Environments)

```python
# filepath: backend/quantum/optimizer.py
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
        # ... (rest of implementation)
```

---

## Classical Implementation

The classical solver uses **Nash equilibrium** computation and **mixed strategy optimization**:

```python
# filepath: backend/classical/solver.py
class ClassicalGameSolver:
    """
    Classical game theory solver using mixed strategies and optimization.
    """
    
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
            # ... (rest of implementation)
```

---

## Getting Started

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **8GB+ RAM** (for quantum simulations)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/games` | GET | List available games |
| `/run-classical` | POST | Run classical optimization |
| `/run-quantum` | POST | Run quantum optimization |
| `/compare` | POST | Compare classical vs quantum |
| `/run-classical-steps` | POST | Step-by-step classical execution |
| `/run-quantum-steps` | POST | Step-by-step quantum execution |
| `/circuit` | POST | Generate quantum circuit diagram |

### Example Request

```bash
# Run quantum optimization
curl -X POST "http://localhost:8000/run-quantum" \
  -H "Content-Type: application/json" \
  -d '{
    "game_type": "prisoners_dilemma",
    "optimizer": "cobyla",
    "max_iterations": 50,
    "shots": 1024
  }'
```

---

## Frontend Features

- **Interactive game selection** (Prisoner's Dilemma, Battle of the Sexes, Matching Pennies)
- **Step-by-step visualization** of quantum and classical execution
- **Real-time payoff tracking** with animated charts
- **Particle background effects** for visual appeal
- **Playback controls** (play, pause, speed adjustment)

---

## Supported Games

### 1. Prisoner's Dilemma
- **Classical Nash**: (Defect, Defect) → (1, 1)
- **Quantum Solution**: Cooperation via entanglement

### 2. Battle of the Sexes
- **Classical**: Coordination problem with multiple equilibria
- **Quantum**: Enhanced coordination via entangled strategies

### 3. Matching Pennies
- **Classical**: Zero-sum, no pure equilibrium
- **Quantum**: Quantum strategies can provide advantage

---

## Technologies Used

### Quantum Computing
- **Qiskit** - Quantum circuit simulation
- **Qiskit Aer** - High-performance quantum simulator

### Backend
- **FastAPI** - Modern Python web framework
- **NumPy** - Numerical computing
- **SciPy** - Scientific optimization (COBYLA, SPSA)
- **Matplotlib** - Visualization

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client

---

## License

MIT License

---

## References

1. Eisert, J., Wilkens, M., & Lewenstein, M. (1999). "Quantum games and quantum strategies"
2. McClean, J. R., et al. (2016). "The theory of variational hybrid quantum-classical algorithms"
3. Qiskit Documentation: https://qiskit.org/documentation/