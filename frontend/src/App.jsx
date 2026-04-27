import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'


const API_BASE = 'http://localhost:8000'

const games = [
  {
    id: 'prisoners_dilemma',
    name: "Prisoner's Dilemma",
    description: 'Classic cooperation vs defection',
    icon: '🔒'
  },
  {
    id: 'battle_of_sexes',
    name: 'Battle of the Sexes',
    description: 'Coordination game',
    icon: '💕'
  },
  {
    id: 'matching_pennies',
    name: 'Matching Pennies',
    description: 'Zero-sum game',
    icon: '🪙'
  }
]

function App() {
  const [selectedGame, setSelectedGame] = useState('prisoners_dilemma')
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState('visualizer')
  
  // Step execution state
  const [classicalSteps, setClassicalSteps] = useState([])
  const [quantumSteps, setQuantumSteps] = useState([])
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1000)
  
  // Legacy result state
  const [classicalResult, setClassicalResult] = useState(null)
  const [quantumResult, setQuantumResult] = useState(null)
  const [compareResult, setCompareResult] = useState(null)

  // Load step data
  const loadStepData = useCallback(async () => {
    setLoading(true)
    try {
      const [classicalRes, quantumRes] = await Promise.all([
        axios.post(`${API_BASE}/run-classical-steps`, {
          game_type: selectedGame,
          max_iterations: 15
        }),
        axios.post(`${API_BASE}/run-quantum-steps`, {
          game_type: selectedGame,
          max_iterations: 15,
          shots: 1024
        })
      ])
      
      setClassicalSteps(classicalRes.data)
      setQuantumSteps(quantumRes.data)
      setCurrentStep(0)
    } catch (error) {
      console.error('Error loading step data:', error)
    }
    setLoading(false)
  }, [selectedGame])

  // Auto-play functionality
  useEffect(() => {
    let interval
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentStep(prev => {
          const maxStep = Math.max(
            classicalSteps.total_steps || 0,
            quantumSteps.total_steps || 0
          ) - 1
          return prev >= maxStep ? 0 : prev + 1
        })
      }, playbackSpeed)
    }
    return () => clearInterval(interval)
  }, [isPlaying, playbackSpeed, classicalSteps, quantumSteps])

  // Load data when game changes
  useEffect(() => {
    if (viewMode === 'visualizer') {
      loadStepData()
    }
  }, [selectedGame, viewMode, loadStepData])

  const runClassical = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/run-classical`, {
        game_type: selectedGame
      })
      setClassicalResult(response.data)
    } catch (error) {
      console.error('Error running classical:', error)
    }
    setLoading(false)
  }

  const runQuantum = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/run-quantum`, {
        game_type: selectedGame,
        optimizer: 'cobyla',
        max_iterations: 50,
        shots: 1024
      })
      setQuantumResult(response.data)
    } catch (error) {
      console.error('Error running quantum:', error)
    }
    setLoading(false)
  }

  const runCompare = async () => {
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/compare`, {
        game_type: selectedGame,
        shots: 1024
      })
      setCompareResult(response.data)
    } catch (error) {
      console.error('Error running comparison:', error)
    }
    setLoading(false)
  }

  const handlePrevStep = () => {
    setCurrentStep(prev => Math.max(0, prev - 1))
  }

  const handleNextStep = () => {
    const maxStep = Math.max(
      classicalSteps.total_steps || 0,
      quantumSteps.total_steps || 0
    ) - 1
    setCurrentStep(prev => Math.min(maxStep, prev + 1))
  }

  const handleStepChange = (e) => {
    setCurrentStep(parseInt(e.target.value))
  }

  // Get current step data
  const getClassicalStepData = () => {
    if (!classicalSteps.steps || classicalSteps.steps.length === 0) return null
    return classicalSteps.steps[currentStep] || classicalSteps.steps[0]
  }

  const getQuantumStepData = () => {
    if (!quantumSteps.steps || quantumSteps.steps.length === 0) return null
    return quantumSteps.steps[currentStep] || quantumSteps.steps[0]
  }

  const classicalStepData = getClassicalStepData()
  const quantumStepData = getQuantumStepData()

  return (
    <div className="app">
      <header className="header">
        <h1>⚛️ QGOptimus</h1>
        <p className="subtitle">Algorithm Execution Visualizer</p>
        <div className="mode-toggle">
          <button 
            className={viewMode === 'visualizer' ? 'active' : ''} 
            onClick={() => setViewMode('visualizer')}
          >
            🔬 Step Visualizer
          </button>
          <button 
            className={viewMode === 'compare' ? 'active' : ''} 
            onClick={() => setViewMode('compare')}
          >
            📊 Compare Results
          </button>
        </div>
      </header>

      <section className="game-selection">
        {games.map(game => (
          <div
            key={game.id}
            className={`game-card ${selectedGame === game.id ? 'selected' : ''}`}
            onClick={() => setSelectedGame(game.id)}
          >
            <span style={{ fontSize: '2rem' }}>{game.icon}</span>
            <h3>{game.name}</h3>
            <p>{game.description}</p>
          </div>
        ))}
      </section>

      {viewMode === 'visualizer' ? (
        <>
          <section className="step-controls">
            <div className="control-group">
              <button 
                className="control-btn play" 
                onClick={() => setIsPlaying(!isPlaying)}
              >
                {isPlaying ? '⏸ Pause' : '▶ Play'}
              </button>
              <button className="control-btn" onClick={handlePrevStep}>
                ⏮ Prev
              </button>
              <button className="control-btn" onClick={handleNextStep}>
                ⏭ Next
              </button>
            </div>
            
            <div className="slider-group">
              <label>Step: {currentStep + 1}</label>
              <input 
                type="range" 
                min="0" 
                max={Math.max(
                  (classicalSteps.total_steps || 1) - 1,
                  (quantumSteps.total_steps || 1) - 1
                )} 
                value={currentStep}
                onChange={handleStepChange}
              />
            </div>
            
            <div className="speed-control">
              <label>Speed:</label>
              <select 
                value={playbackSpeed} 
                onChange={(e) => setPlaybackSpeed(parseInt(e.target.value))}
              >
                <option value={2000}>Slow</option>
                <option value={1000}>Normal</option>
                <option value={500}>Fast</option>
                <option value={200}>Very Fast</option>
              </select>
            </div>
          </section>

          <div className="split-screen">
            {/* Classical Side */}
            <div className="panel classical-panel">
              <div className="panel-header">
                <h2>🖥️ Classical Optimization</h2>
                <span className="badge classical">Best Response Dynamics</span>
              </div>
              
              <div className="code-display">
                <div className="code-title">Execution Trace</div>
                {classicalSteps.code_display && (
                  <div className="code-lines">
                    {Object.entries(classicalSteps.code_display).map(([line, code]) => (
                      <div 
                        key={line} 
                        className={`code-line ${classicalStepData?.active_line === parseInt(line) ? 'active' : ''}`}
                      >
                        <span className="line-number">{line}</span>
                        <span className="line-code">{code}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="step-description">
                <h4>Current Operation</h4>
                <p>{classicalStepData?.description || 'Loading...'}</p>
              </div>

              <div className="parameters-display">
                <h4>Parameters</h4>
                <div className="param-grid">
                  {classicalStepData?.parameters && Object.entries(classicalStepData.parameters).map(([key, value]) => (
                    <div key={key} className="param-item">
                      <span className="param-key">{key}:</span>
                      <span className="param-value">
                        {typeof value === 'number' ? value.toFixed(4) : JSON.stringify(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="payoff-display">
                <h4>Total Payoff</h4>
                <div className="payoff-value">{classicalStepData?.payoff?.toFixed(4) || '0.0000'}</div>
              </div>

              <div className="graph-display">
                <h4>Payoff Convergence</h4>
                <div className="simple-chart">
                  {classicalSteps.payoff_history?.map((payoff, idx) => (
                    <div 
                      key={idx} 
                      className={`chart-bar ${idx === currentStep ? 'current' : ''}`}
                      style={{ height: `${(payoff / Math.max(...classicalSteps.payoff_history, 1)) * 100}%` }}
                      title={`Step ${idx + 1}: ${payoff.toFixed(4)}`}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Quantum Side */}
            <div className="panel quantum-panel">
              <div className="panel-header">
                <h2>⚛️ Quantum Optimization</h2>
                <span className="badge quantum">VQA + Gradient Descent</span>
              </div>
              
              <div className="code-display">
                <div className="code-title">Quantum Circuit</div>
                {quantumSteps.optimizer_code_display && (
                  <div className="code-lines">
                    {Object.entries(quantumSteps.optimizer_code_display).map(([line, code]) => (
                      <div 
                        key={line} 
                        className={`code-line ${quantumStepData?.active_line === parseInt(line) ? 'active' : ''}`}
                      >
                        <span className="line-number">{line}</span>
                        <span className="line-code">{code}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="step-description">
                <h4>Current Operation</h4>
                <p>{quantumStepData?.description || 'Loading...'}</p>
              </div>

              <div className="circuit-visualization">
                <h4>Quantum Circuit</h4>
                <div className="circuit-gates">
                  {quantumSteps.circuit_data?.gates?.map((gate, idx) => (
                    <div key={idx} className={`gate ${gate.type.toLowerCase()}`}>
                      <span className="gate-type">{gate.type}</span>
                      {gate.qubit !== null && <span className="gate-qubit">Q{gate.qubit}</span>}
                      {gate.control !== null && <span className="gate-control">{gate.control}→{gate.target}</span>}
                      {gate.theta && <span className="gate-param">θ={gate.theta.toFixed(2)}</span>}
                      {gate.phi && <span className="gate-param">φ={gate.phi.toFixed(2)}</span>}
                    </div>
                  ))}
                </div>
              </div>

              <div className="parameters-display">
                <h4>Parameters (θ, φ)</h4>
                <div className="param-grid">
                  {quantumStepData?.parameters?.theta && (
                    <>
                      <div className="param-item">
                        <span className="param-key">θ₀:</span>
                        <span className="param-value">{quantumStepData.parameters.theta[0]?.toFixed(4)}</span>
                      </div>
                      <div className="param-item">
                        <span className="param-key">θ₁:</span>
                        <span className="param-value">{quantumStepData.parameters.theta[1]?.toFixed(4)}</span>
                      </div>
                    </>
                  )}
                  {quantumStepData?.parameters?.phi && (
                    <>
                      <div className="param-item">
                        <span className="param-key">φ₀:</span>
                        <span className="param-value">{quantumStepData.parameters.phi[0]?.toFixed(4)}</span>
                      </div>
                      <div className="param-item">
                        <span className="param-key">φ₁:</span>
                        <span className="param-value">{quantumStepData.parameters.phi[1]?.toFixed(4)}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="payoff-display">
                <h4>Total Payoff</h4>
                <div className="payoff-value quantum">{quantumStepData?.payoff?.toFixed(4) || '0.0000'}</div>
              </div>

              <div className="graph-display">
                <h4>Payoff Convergence</h4>
                <div className="simple-chart">
                  {quantumSteps.payoff_history?.map((payoff, idx) => (
                    <div 
                      key={idx} 
                      className={`chart-bar quantum ${idx === currentStep ? 'current' : ''}`}
                      style={{ height: `${(payoff / Math.max(...quantumSteps.payoff_history, 1)) * 100}%` }}
                      title={`Step ${idx + 1}: ${payoff.toFixed(4)}`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          <section className="comparison-bar">
            <div className="comparison-item">
              <span className="comparison-label">Classical Payoff:</span>
              <span className="comparison-value classical">{classicalStepData?.payoff?.toFixed(4) || '-'}</span>
            </div>
            <div className="comparison-item">
              <span className="comparison-label">Quantum Payoff:</span>
              <span className="comparison-value quantum">{quantumStepData?.payoff?.toFixed(4) || '-'}</span>
            </div>
            <div className="comparison-item">
              <span className="comparison-label">Quantum Advantage:</span>
              <span className="comparison-value advantage">
                {classicalStepData?.payoff && quantumStepData?.payoff 
                  ? ((quantumStepData.payoff - classicalStepData.payoff) / Math.abs(classicalStepData.payoff) * 100).toFixed(1)
                  : '-'
                }%
              </span>
            </div>
          </section>
        </>
      ) : (
        <>
          <section className="control-panel">
            <button className="run-btn classical" onClick={runClassical} disabled={loading}>
              🖥️ Run Classical
            </button>
            <button className="run-btn quantum" onClick={runQuantum} disabled={loading}>
              ⚛️ Run Quantum
            </button>
            <button className="run-btn compare" onClick={runCompare} disabled={loading}>
              ⚖️ Compare Both
            </button>
          </section>

          {loading && <div className="loading">Loading...</div>}

          {compareResult && (
            <section className="results">
              <div className="result-card">
                <h3>Classical Result</h3>
                <p>Payoff: {compareResult.classical.payoff.toFixed(4)}</p>
              </div>
              <div className="result-card">
                <h3>Quantum Result</h3>
                <p>Payoff: {compareResult.quantum.payoff.toFixed(4)}</p>
                <p>Parameters: θ=[{compareResult.quantum.optimal_parameters.theta.map(t => t.toFixed(3)).join(', ')}]</p>
              </div>
              <div className="result-card advantage">
                <h3>Quantum Advantage</h3>
                <p>{compareResult.advantage.percentage}%</p>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}

export default App