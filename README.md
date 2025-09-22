# Capacitated Vehicle Routing Problem (CVRP) Solver

This project implements a Genetic Algorithm to solve the Capacitated Vehicle Routing Problem using CVRPLIB dataset instances.

## What is CVRP?

The Capacitated Vehicle Routing Problem is about finding the best routes for delivery trucks. Each truck has a maximum capacity, and each customer has a demand. The goal is to visit all customers with the minimum total distance while respecting capacity constraints.

## Requirements

- Python 3.7 or higher
- Required packages (install with pip):

```bash
pip install -r requirements.txt
```

## How to Run

### 1. Basic Run - Load and Display Problem Instances

```bash
python main.py
```

This will:
- Load all problem instances from the `data/` folder
- Display information about each problem
- Show that the instances are loaded successfully

### 2. Run Genetic Algorithm (if implemented)

```bash
python main.py -run -s A-n33-k6 --gen 1000 --pc 0.9 --pm 0.1
```

Parameters:
- `-s`: Problem instance name (e.g., A-n33-k6)
- `--gen`: Number of generations (e.g., 1000)
- `--pc`: Crossover probability (e.g., 0.9)
- `--pm`: Mutation probability (e.g., 0.1)

### 3. Run Experiments (if implemented)

```bash
python run_experiments.py
```

This will run multiple experiments with different parameter settings.

## Project Structure

```
├── main.py                 # Main entry point
├── run_experiments.py      # Experiment runner
├── requirements.txt        # Python dependencies
├── data/                   # CVRP problem instances
│   ├── A-n33-k6.txt       # Small problems (32-34 customers)
│   ├── B-n35-k5.txt       # Medium problems (35-38 customers)
│   └── X-n101-k25.txt     # Large problems (101+ customers)
└── src/
    ├── vrp/               # Problem loading and representation
    │   ├── load_set.py    # Load CVRP files
    │   └── problem.py     # Problem instance class
    └── ga/                # Genetic Algorithm components
        ├── individual.py  # Solution representation
        ├── fitness.py     # Fitness evaluation
        ├── operators.py   # Crossover and mutation
        └── run_sim.py     # Main GA loop
```

## Data Files

The `data/` folder contains CVRP instances from CVRPLIB:
- **Small**: A-n33-k6, A-n34-k5 (32-34 customers)
- **Medium**: B-n35-k5, B-n38-k6 (35-38 customers) 
- **Large**: X-n101-k25, X-n110-k13 (101+ customers)

Each file contains:
- Customer coordinates
- Customer demands
- Vehicle capacity
- Depot location

## Current Implementation Status

✅ **Completed:**
- Problem loading from CVRPLIB format
- Basic genetic algorithm structure
- Single-objective optimization (total distance)
- PMX crossover and swap mutation operators

🚧 **To Do (for MOVRP assignment):**
- Multi-objective fitness evaluation
- Implementation of MOEAs (NSGA-II, SPEA2, etc.)
- Pareto front analysis
- Performance metrics and comparison

## Example Output

When you run `python main.py`, you should see:
```
--- Loading VRP Problem Instances from .txt files ---
Problem instances loaded successfully
```

## Troubleshooting

- **Error: No module found**: Install requirements with `pip install -r requirements.txt`
- **Error: No .txt files found**: Make sure you have CVRP data files in the `data/` folder
- **Permission denied**: Make sure you have read permissions for the data files
