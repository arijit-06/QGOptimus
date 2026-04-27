"""
FastAPI Backend for Quantum vs Classical Game Optimization
Main application with all API endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import numpy as np
import json

# Import quantum modules
from quantum.circuit import QuantumGameCircuit
from quantum.optimizer import VQAOptimizer, OptimizerType, ClassicalGameOptimizer
from quantum.measurement import QuantumMeasurement
from quantum.step_optimizer import StepBasedQuantumCircuit, StepBasedQuantumOptimizer

# Import classical solver
from classical.solver import ClassicalGameSolver, GamePayoffCalculator, GameType
from classical.step_solver import StepBasedClassicalSolver

# Import games
from games.prisoners_dilemma import PrisonersDilemma, COOPERATE, DEFECT
from games.battle_of_sexes import BattleOfSexes, OPERA, FOOTBALL
from games.matching_pennies import MatchingPennies, HEADS, TAILS


app = FastAPI(
    title="QGOptimus - Quantum Game Optimization",
    description="Compare classical and quantum strategies for game theory",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class GameRequest(BaseModel):
    game_type: str
    optimizer: str = "cobyla"
    max_iterations: int = 50
    shots: int = 1024


class CompareRequest(BaseModel):
    game_type: str
    shots: int = 1024


class CircuitRequest(BaseModel):
    game_type: str
    theta: List[float]
    phi: List[float]


# Game factory
def get_game(game_type: str):
    """Factory function to get game instance."""
    games = {
        "prisoners_dilemma": PrisonersDilemma(),
        "battle_of_sexes": BattleOfSexes(),
        "matching_pennies": MatchingPennies()
    }
    
    if game_type not in games:
        raise HTTPException(status_code=400, detail=f"Unknown game type: {game_type}")
    
    return games[game_type]


def get_game_type_enum(game_type: str) -> GameType:
    """Convert string to GameType enum."""
    mapping = {
        "prisoners_dilemma": GameType.PRISONERS_DILEMMA,
        "battle_of_sexes": GameType.BATTLE_OF_SEXES,
        "matching_pennies": GameType.MATCHING_PENNIES
    }
    return mapping.get(game_type)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "QGOptimus API",
        "version": "1.0.0",
        "description": "Quantum vs Classical Game Optimization",
        "endpoints": {
            "/games": "List available games",
            "/run-classical": "Run classical optimization",
            "/run-quantum": "Run quantum optimization",
            "/compare": "Compare classical vs quantum",
            "/get-circuit": "Get quantum circuit diagram"
        }
    }


@app.get("/games")
async def list_games():
    """List all available games."""
    games = [
        {
            "id": "prisoners_dilemma",
            "name": "Prisoner's Dilemma",
            "description": "Classic cooperation vs defection game",
            "classical_equilibrium": "(D, D) - both defect",
            "quantum_advantage": "Can achieve (C, C) - mutual cooperation"
        },
        {
            "id": "battle_of_sexes",
            "name": "Battle of the Sexes",
            "description": "Coordination game with different preferences",
            "classical_equilibrium": "(O, O) or (F, F) - two pure equilibria",
            "quantum_advantage": "Fairer coordination through entanglement"
        },
        {
            "id": "matching_pennies",
            "name": "Matching Pennies",
            "description": "Zero-sum game",
            "classical_equilibrium": "50/50 mixed strategy",
            "quantum_advantage": "First player can gain positive expected payoff"
        }
    ]
    return {"games": games}


@app.post("/run-classical")
async def run_classical(request: GameRequest):
    """Run classical game optimization."""
    try:
        game = get_game(request.game_type)
        game_type_enum = get_game_type_enum(request.game_type)
        
        # Get payoff matrices
        calculator = GamePayoffCalculator()
        p0, p1 = calculator.get_payoff_matrices(game_type_enum)
        
        # Solve using classical solver
        solver = ClassicalGameSolver()
        result = solver.solve_game(p0, p1, game_type_enum)
        
        # Get equilibrium info
        if request.game_type == "prisoners_dilemma":
            equilibrium_info = game.get_classical_equilibrium()
        elif request.game_type == "battle_of_sexes":
            equilibrium_info = game.get_classical_equilibria()
        else:
            equilibrium_info = game.get_classical_equilibrium()
        
        return {
            "game": request.game_type,
            "game_name": game.name,
            "result": result,
            "equilibrium_info": equilibrium_info,
            "description": game.description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-quantum")
async def run_quantum(request: GameRequest):
    """Run quantum game optimization using VQA."""
    try:
        game = get_game(request.game_type)
        
        # Initialize quantum components
        circuit = QuantumGameCircuit(num_players=2, shots=request.shots)
        optimizer = VQAOptimizer(OptimizerType(request.optimizer))
        measurement = QuantumMeasurement(shots=request.shots)
        
        # Define objective function for optimization
        def objective_function(params):
            """Maximize sum of player payoffs."""
            theta = params[:2]
            phi = params[2:]
            
            # Run quantum simulation
            result = circuit.simulate(theta, phi)
            
            # Calculate payoffs based on game type
            if request.game_type == "prisoners_dilemma":
                p0, p1 = game.quantum_payoff_from_measurement(result['probabilities'])
            elif request.game_type == "battle_of_sexes":
                p0, p1 = game.quantum_payoff_from_measurement(result['probabilities'])
            else:  # matching_pennies
                p0, p1 = game.quantum_payoff_from_measurement(result['probabilities'])
            
            # Return negative for minimization (we want to maximize)
            return -(p0 + p1)
        
        # Initial parameters
        initial_params = np.array([np.pi/4, np.pi/4, 0, 0])
        bounds = [(0, 2*np.pi)] * 4
        
        # Run optimization
        opt_result = optimizer.optimize(
            objective_function,
            initial_params,
            bounds=bounds,
            max_iterations=request.max_iterations
        )
        
        # Get optimal parameters
        optimal_theta = opt_result.optimal_params[:2]
        optimal_phi = opt_result.optimal_params[2:]
        
        # Run final simulation with optimal parameters
        final_result = circuit.simulate(optimal_theta, optimal_phi)
        
        # Calculate final payoffs
        if request.game_type == "prisoners_dilemma":
            final_p0, final_p1 = game.quantum_payoff_from_measurement(final_result['probabilities'])
        elif request.game_type == "battle_of_sexes":
            final_p0, final_p1 = game.quantum_payoff_from_measurement(final_result['probabilities'])
        else:
            final_p0, final_p1 = game.quantum_payoff_from_measurement(final_result['probabilities'])
        
        # Get circuit diagram
        circuit_diagram = circuit.get_circuit_diagram(optimal_theta, optimal_phi)
        
        # Get measurement histogram
        hist_image = measurement.get_probability_histogram(
            final_result['probabilities'],
            f"{game.name} - Quantum Strategy Probabilities"
        )
        
        # Get convergence plot
        convergence_image = measurement.get_convergence_plot(
            opt_result.history,
            "Quantum Optimization Convergence"
        )
        
        # Get Bloch sphere coordinates
        bloch_coords = []
        for i in range(2):
            coords = circuit.get_bloch_coordinates(optimal_theta[i], optimal_phi[i])
            bloch_coords.append(coords)
        
        bloch_image = measurement.get_bloch_sphere_plot(
            bloch_coords,
            ["Player 0", "Player 1"]
        )
        
        return {
            "game": request.game_type,
            "game_name": game.name,
            "optimal_parameters": {
                "theta": optimal_theta.tolist(),
                "phi": optimal_phi.tolist()
            },
            "optimal_payoff": {
                "player_0": final_p0,
                "player_1": final_p1,
                "total": final_p0 + final_p1
            },
            "measurement_result": {
                "counts": final_result['counts'],
                "probabilities": final_result['probabilities']
            },
            "optimization": {
                "iterations": opt_result.iterations,
                "converged": opt_result.converged,
                "history": opt_result.history
            },
            "circuit_diagram": circuit_diagram,
            "visualizations": {
                "histogram": hist_image,
                "convergence": convergence_image,
                "bloch_sphere": bloch_image
            },
            "bloch_coordinates": bloch_coords
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_strategies(request: CompareRequest):
    """Compare classical and quantum strategies."""
    try:
        game = get_game(request.game_type)
        game_type_enum = get_game_type_enum(request.game_type)
        
        # === CLASSICAL SOLUTION ===
        calculator = GamePayoffCalculator()
        p0, p1 = calculator.get_payoff_matrices(game_type_enum)
        
        classical_solver = ClassicalGameSolver()
        classical_result = classical_solver.solve_game(p0, p1, game_type_enum)
        
        # Extract classical optimal payoff
        if classical_result['optimal_mixed_strategies']:
            classical_payoff = (
                classical_result['optimal_mixed_strategies']['player_0']['expected_payoff'] +
                classical_result['optimal_mixed_strategies']['player_1']['expected_payoff']
            )
        else:
            classical_payoff = 0
        
        # === QUANTUM SOLUTION ===
        circuit = QuantumGameCircuit(num_players=2, shots=request.shots)
        optimizer = VQAOptimizer(OptimizerType.COBYLA)
        measurement = QuantumMeasurement(shots=request.shots)
        
        def objective_function(params):
            theta = params[:2]
            phi = params[2:]
            result = circuit.simulate(theta, phi)
            
            if request.game_type == "prisoners_dilemma":
                p0, p1 = game.quantum_payoff_from_measurement(result['probabilities'])
            elif request.game_type == "battle_of_sexes":
                p0, p1 = game.quantum_payoff_from_measurement(result['probabilities'])
            else:
                p0, p1 = game.quantum_payoff_from_measurement(result['probabilities'])
            
            return -(p0 + p1)
        
        initial_params = np.array([np.pi/4, np.pi/4, 0, 0])
        bounds = [(0, 2*np.pi)] * 4
        
        opt_result = optimizer.optimize(
            objective_function,
            initial_params,
            bounds=bounds,
            max_iterations=50
        )
        
        optimal_theta = opt_result.optimal_params[:2]
        optimal_phi = opt_result.optimal_params[2:]
        
        final_result = circuit.simulate(optimal_theta, optimal_phi)
        
        if request.game_type == "prisoners_dilemma":
            q_p0, q_p1 = game.quantum_payoff_from_measurement(final_result['probabilities'])
        elif request.game_type == "battle_of_sexes":
            q_p0, q_p1 = game.quantum_payoff_from_measurement(final_result['probabilities'])
        else:
            q_p0, q_p1 = game.quantum_payoff_from_measurement(final_result['probabilities'])
        
        quantum_payoff = q_p0 + q_p1
        
        # === COMPARISON ===
        advantage = measurement.analyze_quantum_advantage(
            {'optimal_payoff': classical_payoff},
            {'optimal_payoff': quantum_payoff}
        )
        
        # Get comparison plot
        comparison_image = measurement.get_comparison_plot(
            classical_payoff,
            quantum_payoff,
            game.name
        )
        
        # Get quantum advantage info
        if request.game_type == "prisoners_dilemma":
            advantage_info = game.get_quantum_advantage_info()
        elif request.game_type == "battle_of_sexes":
            advantage_info = game.get_quantum_advantage_info()
        else:
            advantage_info = game.get_quantum_advantage_info()
        
        return {
            "game": request.game_type,
            "game_name": game.name,
            "classical": {
                "payoff": classical_payoff,
                "result": classical_result
            },
            "quantum": {
                "payoff": quantum_payoff,
                "player_0_payoff": q_p0,
                "player_1_payoff": q_p1,
                "optimal_parameters": {
                    "theta": optimal_theta.tolist(),
                    "phi": optimal_phi.tolist()
                },
                "measurement_probabilities": final_result['probabilities']
            },
            "advantage": advantage,
            "advantage_info": advantage_info,
            "visualizations": {
                "comparison": comparison_image
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-circuit")
async def get_circuit(request: CircuitRequest):
    """Get quantum circuit diagram for given parameters."""
    try:
        game = get_game(request.game_type)
        
        circuit = QuantumGameCircuit(num_players=2)
        
        theta = np.array(request.theta)
        phi = np.array(request.phi)
        
        # Get ASCII diagram
        ascii_diagram = circuit.get_circuit_diagram(theta, phi)
        
        # Get PNG diagram
        png_diagram = circuit.get_mpl_circuit(theta, phi)
        
        # Get Bloch coordinates
        bloch_coords = []
        for i in range(len(theta)):
            coords = circuit.get_bloch_coordinates(theta[i], phi[i])
            bloch_coords.append(coords)
        
        return {
            "game": request.game_type,
            "game_name": game.name,
            "parameters": {
                "theta": request.theta,
                "phi": request.phi
            },
            "circuit_diagram": ascii_diagram,
            "circuit_image": png_diagram,
            "bloch_coordinates": bloch_coords
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game-info/{game_type}")
async def get_game_info(game_type: str):
    """Get detailed information about a specific game."""
    try:
        game = get_game(game_type)
        
        return {
            "id": game_type,
            "name": game.name,
            "description": game.description,
            "classical_equilibrium": game.get_classical_equilibrium() if game_type == "prisoners_dilemma" else None,
            "quantum_advantage": game.get_quantum_advantage_info()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# STEP-BASED EXECUTION ENDPOINTS (Algorithm Visualizer)
# =====================================================

class StepExecutionRequest(BaseModel):
    game_type: str
    max_iterations: int = 20
    shots: int = 1024


@app.post("/run-classical-steps")
async def run_classical_steps(request: StepExecutionRequest):
    """
    Run classical game optimization with step-by-step execution.
    Returns all steps for visualization.
    """
    try:
        game = get_game(request.game_type)
        game_type_enum = get_game_type_enum(request.game_type)
        
        # Get payoff matrices
        calculator = GamePayoffCalculator()
        p0, p1 = calculator.get_payoff_matrices(game_type_enum)
        
        # Generate step-by-step execution
        step_solver = StepBasedClassicalSolver()
        steps = step_solver.generate_steps(p0, p1, request.game_type, request.max_iterations)
        
        # Get code display
        code_display = step_solver.get_code_display(request.game_type)
        
        # Extract payoff history
        payoff_history = [step['payoff'] for step in steps if step['payoff'] > 0]
        
        return {
            "game": request.game_type,
            "game_name": game.name,
            "steps": steps,
            "code_display": code_display,
            "total_steps": len(steps),
            "payoff_history": payoff_history,
            "description": "Step-by-step classical optimization execution"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-quantum-steps")
async def run_quantum_steps(request: StepExecutionRequest):
    """
    Run quantum game optimization with step-by-step execution.
    Returns all steps for visualization including circuit data.
    """
    try:
        game = get_game(request.game_type)
        game_type_enum = get_game_type_enum(request.game_type)
        
        # Get payoff matrices
        calculator = GamePayoffCalculator()
        p0, p1 = calculator.get_payoff_matrices(game_type_enum)
        
        # Generate step-by-step quantum optimization
        step_optimizer = StepBasedQuantumOptimizer()
        steps = step_optimizer.generate_optimization_steps(p0, p1, request.game_type, request.max_iterations)
        
        # Get code displays
        quantum_code = step_optimizer.get_code_display()
        optimizer_code = step_optimizer.get_optimizer_code_display()
        
        # Get final circuit data
        final_step = steps[-1]
        circuit_data = final_step.get('state', {}).get('circuit', {})
        
        # Extract payoff history
        payoff_history = [step['payoff'] for step in steps if step['payoff'] > 0]
        
        return {
            "game": request.game_type,
            "game_name": game.name,
            "steps": steps,
            "quantum_code_display": quantum_code,
            "optimizer_code_display": optimizer_code,
            "circuit_data": circuit_data,
            "total_steps": len(steps),
            "payoff_history": payoff_history,
            "description": "Step-by-step quantum optimization execution"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/code-display/{engine_type}")
async def get_code_display(engine_type: str, game_type: str = "prisoners_dilemma"):
    """
    Get code display for classical or quantum engine.
    Used for syntax highlighting in the visualizer.
    """
    try:
        if engine_type == "classical":
            step_solver = StepBasedClassicalSolver()
            return {
                "engine": "classical",
                "code": step_solver.get_code_display(game_type)
            }
        elif engine_type == "quantum":
            step_optimizer = StepBasedQuantumOptimizer()
            return {
                "engine": "quantum",
                "code": step_optimizer.get_code_display()
            }
        elif engine_type == "optimizer":
            step_optimizer = StepBasedQuantumOptimizer()
            return {
                "engine": "optimizer",
                "code": step_optimizer.get_optimizer_code_display()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown engine type: {engine_type}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)