# Quantum vs Classical Game Optimization
# Project: QGOptimus

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

### Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
QGOptimus/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── quantum/
│   │   ├── circuit.py          # Quantum circuit implementation
│   │   ├── optimizer.py        # VQA optimizer (COBYLA/SPSA)
│   │   └── measurement.py      # Measurement & state analysis
│   ├── classical/
│   │   └── solver.py           # Classical game theory solver
│   └── games/
│       ├── prisoners_dilemma.py
│       ├── battle_of_sexes.py
│       └── matching_pennies.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── services/
│   └── package.json
└── README.md
```

## Games Implemented

1. **Prisoner's Dilemma** - Classic cooperation vs defection
2. **Battle of the Sexes** - Coordination game
3. **Matching Pennies** - Zero-sum game

## Quantum Advantage

The system demonstrates how quantum strategies can outperform classical ones:
- Prisoner's Dilemma: Quantum strategy achieves (C,C) while classical gets (D,D)
- Uses real Qiskit circuits with RY, RZ gates and CNOT entanglement
- Variational Quantum Algorithm optimizes player strategies