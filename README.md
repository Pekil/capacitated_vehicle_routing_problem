# Capacitated Vehicle Routing Problem (CVRP) Solver

A Python implementation of NSGA-II and SPEA2 algorithms for solving the Capacitated Vehicle Routing Problem with two objectives: minimizing total distance and balancing route lengths, using CVRPLIB dataset instances.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation

### 1. Clone the repository:
```bash
git clone git@github.com:Pekil/capacitated_vehicle_routing_problem.git
cd capacitated_vehicle_routing_problem
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
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

### Run Multi-Objective CVRP Experiments

The entrypoint now requires choosing an algorithm via a flag.

Run NSGA-II (recommended first, also creates initial populations used by SPEA2):
```bash
python main.py -a nsga2
```

Run SPEA2 (loads initial populations saved by the NSGA-II run):
```bash
python main.py -a spea2
```

This will run on all available datasets with multiple parameter configurations:
- **Datasets**: A-n33-k6, B-n35-k5, X-n110-k13 (and any other `.txt` in `data/`)
- **Algorithms**: NSGA-II, SPEA2
- **Parameter sets**: Baseline, Deep Search, High Exploration
- **Objectives**: Minimize total distance and maximum single-route distance (route balance)

**Outputs**
- Experiment artifacts under `results/` (per algorithm/problem/parameter-set/run)
- Initial populations under `results/initial_populations/` (created by NSGA-II)
- Process logs redirected to `data/process_logs/` (one log per run)




## Project Structure

```
├── main.py                 # Main entry point - runs NSGA-II or SPEA2
├── analysis.py             # Aggregates results, computes HV/spacing, and plots
├── requirements.txt        # Python dependencies
├── venv/                   # Virtual environment (created by you)
├── results/                # Output directory for experiment results
│   ├── initial_populations/  # Saved by NSGA-II, loaded by SPEA2
│   ├── NSGA-II/              # Per-run outputs for NSGA-II
│   └── SPEA2/                # Per-run outputs for SPEA2
├── data/                   # CVRP problem instances and process logs
│   ├── A-n33-k6.txt        # Small problem (33 customers, 6 vehicles)
│   ├── B-n35-k5.txt        # Medium problem (35 customers, 5 vehicles)
│   ├── X-n110-k13.txt      # Large problem (110 customers, 13 vehicles)
│   └── process_logs/       # Stdout/stderr log files per run
└── src/
    ├── vrp/               # Problem loading and representation
    │   ├── load_set.py    # Load CVRPLIB files
    │   └── problem.py     # Problem instance class with distance matrix
    └── ga/                # Multi-Objective Genetic Algorithm components
        ├── algorithms.py  # NSGA-II and SPEA2 implementations
        ├── individual.py  # Multi-objective solution representation
        ├── fitness.py     # Multi-objective fitness evaluation (Split/DP)
        ├── operators.py   # PMX crossover and swap mutation
        ├── pareto_selection.py  # Non-dominated sorting and crowding distance
        ├── selection.py   # Tournament selection utilities
        └── logger.py      # Results logging and analysis
```

## Data Files

The `data/` folder contains CVRP instances from CVRPLIB:
- **A-n33-k6**: Small problem (33 customers, 6 vehicles, capacity=100)
- **A-n34-k5**: Small problem (34 customers, 5 vehicles)
- **B-n35-k5**: Medium problem (35 customers, 5 vehicles) 
- **B-n38-k6**: Medium problem (38 customers, 6 vehicles)
- **X-n101-k25**: Large problem (101 customers, 25 vehicles)
- **X-n110-k13**: Large problem (110 customers, 13 vehicles)

Each file contains:
- Customer coordinates (x, y)
- Customer demands 
- Vehicle capacity
- Depot location (node 1)


## Analyze Results

After runs complete, you can aggregate metrics and generate plots:

```bash
python analysis.py
```

This will:
- Load `summary.json` and `final_pareto_front.csv` for all problems/parameter-set/algorithm combos
- Compute Hypervolume and Spacing (mean/std)
- Save a CSV table `analysis_summary.csv`
- Generate per-problem Pareto-front comparison plots under `results/plots/`

