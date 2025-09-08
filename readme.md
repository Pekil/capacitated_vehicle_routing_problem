# Vehicle Routing Problem (VRP) - Group 9 ACIT

## VRP Genetic Algorithm Solver

This project provides a comprehensive toolkit for solving the Vehicle Routing Problem (VRP) using a steady-state Genetic Algorithm (GA). It includes features for scenario generation, configurable GA execution, results visualization, and a fully automated experimentation suite for performance analysis.

## Features

*   **Random Scenario Generation**: Creates VRP problem instances of varying complexity (small, medium, large) with randomized customer locations and demands.

*   **Configurable Genetic Algorithm**: A steady-state GA that uses Partially-Mapped Crossover (PMX) and Swap Mutation to find optimal vehicle routes. Key parameters like generations, crossover probability, and mutation probability are controllable from the command line.

*   **Fitness Evaluation**: Utilizes a sophisticated dynamic programming algorithm (the Split algorithm) to optimally partition a chromosome into the most efficient set of vehicle routes, respecting vehicle capacity constraints.

*   **Results Logging**: Automatically saves detailed generation-by-generation statistics (best, average, worst fitness) and run metadata (parameters, execution time) to `.csv` and `.json` files.

*   **Dynamic Visualization**:
    *   **Animation (`-viz`)**: Plays back the entire evolution of the best solution for a given run, showing how the routes improve over generations.
    *   **Convergence Plotting (`-plot`)**: Automatically generates and saves a `.png` graph of the best, average, and worst fitness over generations, providing a clear view of the algorithm's convergence.

*   **Automated Experimentation Suite**: A master script (`run_experiments.py`) that fully automates the process of running multiple trials for different scenarios and parameter sets, aggregating the results, and generating final report-ready statistical tables.

## Requirements & Setup

1.  **Python 3.8+**

2.  **Virtual Environment (Recommended)**:
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Dependencies**: Install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

---

## For the Instructor: How to Run the Program

The scenario files (`scenario-*.json`) are included with the project. You can immediately run experiments or individual tests.

There are two primary ways to use this program:
1.  **Run the Full Experiment Suite**: The recommended method to replicate the final report results (THIS MAY TAKE UP TO 20 MINUTES).
2.  **Run Individual Tests**: For examining or verifying the performance of any single configuration.

### 1. Run the Full Experiment Suite (Recommended)

The `run_experiments.py` script is the simplest and most effective way to evaluate the project. It automates the entire process of generating the results for the final report.

**What this script does:**
1.  **Handles Cleanup:** The script automatically performs a safe cleanup of previous experimental runs and population initializations. It does **NOT** delete the provided `scenario-*.json` files.
2.  **Initializes Populations:** It creates new "Generation 0" populations for the 6 scenarios using the correct population sizes (100 for small, 200 for medium, 300 for large).
3.  **Executes All Runs:** It systematically runs **5 independent trials** for each of the **6 scenarios** with each of the **3 predefined parameter sets** (Baseline, Exploration, Exploitation), for a total of 90 runs.
4.  **Generates Report:** After all runs are complete, it parses the results and prints final, formatted summary tables to the console. It also saves a full report to `data/experiments/final_summary_report.csv`.

**To execute, simply run the following command from the project's root directory:**
```bash
python run_experiments.py
```

### 2. Run Individual Tests

This method allows you to run a single simulation for any scenario with any set of parameters using `main.py`.

**Step A: Initialize the Populations**
Before your first run, you must create the initial populations.
```bash
# Initialize Small scenarios with pop 100, Medium with 200, and Large with 300
python main.py -init -pop 100 200 300
```
Note: This command has a safety check and will only run once. To re-initialize, you must first manually delete the data/generations directory.

**Step B: Run a GA Simulation**
Use the -run command with your desired parameters.

### Run a baseline simulation on scenario 'm-1'
``` bash
python main.py -run -s m-1
```
### Run a custom experiment with 10,000 generations
```
python main.py -run -s m-1 --gen 10000 --pc 0.8 --pm 0.3
```

Step C: Analyze the Results
Generate a plot or animation for that specific run.
```
# Create a .png graph of the fitness curves
python main.py -plot -s m-1
```
```
# Watch an animation of the best solution evolving over time
python main.py -viz m-1 --speed 50
```

# Command Reference
### Main Scripts
Command	Description
* python run_experiments.py (Recommended) Runs the full suite of 90 experiments and generates the final report.
* python main.py [command]	The main program for running individual simulations and analysis tools.

### Commands for main.py
Command	Description
* -init	Initializes populations. Must be used with -pop.
* -run	Runs a single GA simulation. Must be used with -s.
* -plot	Generates a convergence graph from a completed run's log file. Must be used with -s.
* -viz <scenario>	Plays an animation of a completed run. Example: -viz m-1.
* -generate	Creates a new set of random scenario-*.json files. Only needed after a -reset.
* -reset	(Use with Caution) Deletes all generated data, including scenario files.
* -status	Shows the current status of the problem sets and their logs.

## Parameters for Commands


| Parameter | Used With | Description |
| :------- | :------: | -------: |
| -pop <sizes...> |-init | Sets population size(s). Use 1 value (e.g., 150) or 3 for s, m, l (e.g., 100 200 300) |
| -s <scenario> | -run, -plot | Specifies the target scenario name (e.g., m-1) |
| --gen <int> | -run | Sets the number of generations. Default: 5000. |
| --pc <float> | -run |	Sets the crossover probability. Default: 0.9. |
| --pm <float> | -run | Sets the mutation probability. Default: 0.1. |
| --speed <int> | -viz | Sets animation playback speed in generations/sec. Default: 10. |
