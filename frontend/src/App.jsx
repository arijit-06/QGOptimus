import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import ParticleBackground from './components/ParticleBackground'


const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  
  // Step execution state
  const [classicalSteps, setClassicalSteps] = useState([])
  const [quantumSteps, setQuantumSteps] = useState([])
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playbackSpeed, setPlaybackSpeed] = useState(1000)
  const [iterationComplete, setIterationComplete] = useState(false)
  
  // Track maximum payoffs
  const [maxClassicalPayoff, setMaxClassicalPayoff] = useState(0)
  const [maxQuantumPayoff, setMaxQuantumPayoff] = useState(0)

  // Load step data
  const loadStepData = useCallback(async () => {
    setLoading(true)
    setIterationComplete(false)
    setMaxClassicalPayoff(0)
    setMaxQuantumPayoff(0)
    setCurrentStep(0)
    setIsPlaying(false)
    
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
    } catch (error) {
      console.error('Error loading step data:', error)
    }
    setLoading(false)
  }, [selectedGame])

  // Get current step data — declared BEFORE the effects that reference them
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

  // Auto-play functionality - stops after one full iteration
  useEffect(() => {
    let interval
    if (isPlaying && !iterationComplete) {
      interval = setInterval(() => {
        setCurrentStep(prev => {
          const maxStep = Math.max(
            classicalSteps.total_steps || 0,
            quantumSteps.total_steps || 0
          ) - 1
          
          // Stop at the end of iteration
          if (prev >= maxStep) {
            setIsPlaying(false)
            setIterationComplete(true)
            return maxStep
          }
          return prev + 1
        })
      }, playbackSpeed)
    }
    return () => clearInterval(interval)
  }, [isPlaying, playbackSpeed, classicalSteps, quantumSteps, iterationComplete])

  // Track maximum payoffs
  useEffect(() => {
    if (classicalStepData?.payoff && classicalStepData.payoff > maxClassicalPayoff) {
      setMaxClassicalPayoff(classicalStepData.payoff)
    }
    if (quantumStepData?.payoff && quantumStepData.payoff > maxQuantumPayoff) {
      setMaxQuantumPayoff(quantumStepData.payoff)
    }
  }, [currentStep, classicalStepData, quantumStepData])

  // Load data when game changes
  useEffect(() => {
    loadStepData()
  }, [selectedGame, loadStepData])

  const handlePrevStep = () => {
    setCurrentStep(prev => Math.max(0, prev - 1))
    setIterationComplete(false)
  }

  const handleNextStep = () => {
    const maxStep = Math.max(
      classicalSteps.total_steps || 0,
      quantumSteps.total_steps || 0
    ) - 1
    const newStep = Math.min(maxStep, currentStep + 1)
    setCurrentStep(newStep)
    
    // Check if we've reached the end
    if (newStep >= maxStep) {
      setIterationComplete(true)
    }
  }

  const handleStepChange = (e) => {
    const newStep = parseInt(e.target.value)
    setCurrentStep(newStep)
    setIterationComplete(newStep >= (Math.max(classicalSteps.total_steps || 0, quantumSteps.total_steps || 0) - 1))
  }

  const handleRestart = () => {
    setCurrentStep(0)
    setIterationComplete(false)
    setMaxClassicalPayoff(0)
    setMaxQuantumPayoff(0)
    setIsPlaying(false)
  }

  // (step data helpers moved above the effects that consume them)

  // Calculate comparison
  const quantumAdvantage = maxClassicalPayoff > 0 
    ? ((maxQuantumPayoff - maxClassicalPayoff) / Math.abs(maxClassicalPayoff) * 100).toFixed(1)
    : 0

  return (
    <>
      <ParticleBackground />
      {/* glass overlay that sits between canvas and content */}
      <div className="bg-glass-overlay" />
      <div className="app">
      <header className="header">
        <h1>⚛️ QGOptimus</h1>
        <p className="subtitle">Algorithm Execution Visualizer</p>
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

      <section className="step-controls">
        <div className="control-group">
          <button 
            className="control-btn play" 
            onClick={() => setIsPlaying(!isPlaying)}
            disabled={iterationComplete}
          >
            {isPlaying ? '⏸ Pause' : '▶ Play'}
          </button>
          <button className="control-btn" onClick={handlePrevStep}>
            ⏮ Prev
          </button>
          <button className="control-btn" onClick={handleNextStep}>
            ⏭ Next
          </button>
          <button className="control-btn" onClick={handleRestart}>
            🔄 Restart
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

      {loading && <div className="loading">Loading algorithm execution...</div>}

      {!loading && (
        <>
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
                <h4>Current Payoff</h4>
                <div className="payoff-value">{classicalStepData?.payoff?.toFixed(4) || '0.0000'}</div>
              </div>

              <div className="graph-display">
                <h4>Payoff Convergence</h4>
                <div className="simple-chart">
                  {classicalSteps.payoff_history?.map((payoff, idx) => {
                    const maxVal = Math.max(...classicalSteps.payoff_history.map(Math.abs), 1)
                    const heightPct = Math.max(0, (payoff / maxVal) * 100)
                    return (
                      <div 
                        key={idx} 
                        className={`chart-bar ${idx === currentStep ? 'current' : ''}`}
                        style={{ height: `${heightPct}%` }}
                        title={`Step ${idx + 1}: ${payoff.toFixed(4)}`}
                      />
                    )
                  })}
                </div>
              </div>

              <div className="max-payoff-display">
                <h4>Best Payoff Achieved</h4>
                <div className="max-payoff-value">{maxClassicalPayoff.toFixed(4)}</div>
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
                      {gate.qubit != null && <span className="gate-qubit">Q{gate.qubit}</span>}
                      {gate.control != null && <span className="gate-control">{gate.control}→{gate.target}</span>}
                      {gate.theta != null && <span className="gate-param">θ={gate.theta.toFixed(2)}</span>}
                      {gate.phi != null && <span className="gate-param">φ={gate.phi.toFixed(2)}</span>}
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
                <h4>Current Payoff</h4>
                <div className="payoff-value quantum">{quantumStepData?.payoff?.toFixed(4) || '0.0000'}</div>
              </div>

              <div className="graph-display">
                <h4>Payoff Convergence</h4>
                <div className="simple-chart">
                  {quantumSteps.payoff_history?.map((payoff, idx) => {
                    const maxVal = Math.max(...quantumSteps.payoff_history.map(Math.abs), 1)
                    const heightPct = Math.max(0, (payoff / maxVal) * 100)
                    return (
                      <div 
                        key={idx} 
                        className={`chart-bar quantum ${idx === currentStep ? 'current' : ''}`}
                        style={{ height: `${heightPct}%` }}
                        title={`Step ${idx + 1}: ${payoff.toFixed(4)}`}
                      />
                    )
                  })}
                </div>
              </div>

              <div className="max-payoff-display">
                <h4>Best Payoff Achieved</h4>
                <div className="max-payoff-value quantum">{maxQuantumPayoff.toFixed(4)}</div>
              </div>
            </div>
          </div>

          {/* Final Comparison - shown after iteration completes */}
          <section className="comparison-bar">
            <div className="comparison-item">
              <span className="comparison-label">Classical Best:</span>
              <span className="comparison-value classical">{maxClassicalPayoff.toFixed(4)}</span>
            </div>
            <div className="comparison-item">
              <span className="comparison-label">Quantum Best:</span>
              <span className="comparison-value quantum">{maxQuantumPayoff.toFixed(4)}</span>
            </div>
            <div className="comparison-item">
              <span className="comparison-label">Winner:</span>
              <span className={`comparison-value ${maxQuantumPayoff >= maxClassicalPayoff ? 'quantum' : 'classical'}`}>
                {maxQuantumPayoff >= maxClassicalPayoff ? '⚛️ Quantum' : '🖥️ Classical'}
              </span>
            </div>
            <div className="comparison-item">
              <span className="comparison-label">Difference:</span>
              <span className={`comparison-value advantage ${parseFloat(quantumAdvantage) < 0 ? 'negative' : ''}`}>
                {parseFloat(quantumAdvantage) >= 0 ? '+' : ''}{quantumAdvantage}%
              </span>
            </div>
          </section>

          {iterationComplete && (
            <div className="iteration-complete-banner">
              <span>🎉 Iteration Complete! Review the best payoffs above.</span>
              <button className="control-btn play" onClick={loadStepData}>
                Run Again
              </button>
            </div>
          )}
        </>
      )}
    </div>
    </>
  )
}

export default App