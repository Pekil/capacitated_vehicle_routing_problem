# Capacitated Vehicle Routing Problem (CVRP) Solver

This project implements a Genetic Algorithm to solve the Capacitated Vehicle Routing Problem using CVRPLIB dataset instances.

## Setup Virtual Environment (REQUIRED)

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

### 4. When Finished - Deactivate

```bash
deactivate
```




## How to Run

**: If already set up, activate your virtual environment before running!**

```bash
source venv/bin/activate  # Activate virtual environment
```

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
├── venv/                   # Virtual environment (created by you)
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

