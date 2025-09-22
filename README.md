# Capacitated Vehicle Routing Problem (CVRP) Solver

This project implements Multi-Objective Evolutionary Algorithms (MOEAs) to solve the Multi-Objective Capacitated Vehicle Routing Problem using CVRPLIB dataset instances.

## Setup Virtual Environment

Modern Python installations require using virtual environments to avoid conflicts. Follow these steps:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```


## How to Run

**IMPORTANT: Always activate your virtual environment first!**

```bash
source venv/bin/activate  # Activate virtual environment
```

### Run Multi-Objective CVRP Experiments

```bash
python main.py
```

This will run NSGA-II on all available datasets with multiple parameter configurations:
- **Datasets**: A-n33-k6, B-n35-k5, X-n110-k13
- **Algorithm**: NSGA-II (Non-dominated Sorting Genetic Algorithm II)
- **Parameter sets**: Baseline, Deep Search, High Exploration
- **Objectives**: Total distance + Route balance (longest route)

**Output**: Results are logged to `results/` directory with detailed performance metrics.



*Note: This is currently a placeholder framework for systematic experimentation.*

## Project Structure

```
├── main.py                 # Main entry point - runs NSGA-II experiments
├── run_experiments.py      # Systematic experiment framework (legacy)
├── requirements.txt        # Python dependencies
├── venv/                   # Virtual environment (created by you)
├── results/                # Output directory for experiment results
├── data/                   # CVRP problem instances
│   ├── A-n33-k6.txt       # Small problem (33 customers, 6 vehicles)
│   ├── B-n35-k5.txt       # Medium problem (35 customers, 5 vehicles)
│   ├── X-n110-k13.txt     # Large problem (110 customers, 13 vehicles)
│   └── ...                # Other CVRPLIB instances
└── src/
    ├── vrp/               # Problem loading and representation
    │   ├── load_set.py    # Load CVRPLIB files
    │   └── problem.py     # Problem instance class with distance matrix
    └── ga/                # Multi-Objective Genetic Algorithm components
        ├── algorithms.py  # NSGA-II implementation
        ├── individual.py  # Multi-objective solution representation
        ├── fitness.py     # Multi-objective fitness evaluation
        ├── operators.py   # PMX crossover and swap mutation
        ├── pareto_selection.py  # Non-dominated sorting and crowding distance
        ├── selection.py   # Tournament selection
        └── logger.py      # Results logging and analysis
```

## Data Files

The `data/` folder contains CVRP instances from CVRPLIB:
- **A-n33-k6**: Small problem (33 customers, 6 vehicles, capacity=100)
- **B-n35-k5**: Medium problem (35 customers, 5 vehicles) 
- **X-n110-k13**: Large problem (110 customers, 13 vehicles)

Each file contains:
- Customer coordinates (x, y)
- Customer demands 
- Vehicle capacity
- Depot location (node 1)


