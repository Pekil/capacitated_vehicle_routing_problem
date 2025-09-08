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

3.  **Dependencies**: Install the required Python packages. Create a file named `requirements.txt` in your project's root directory with the following content:
    ```
    numpy
    pandas
    matplotlib
    ```
    Then, install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

---

## For the Instructor: How to Run the Program

There are two primary ways to use this program:
1.  **Run the Full Experiment Suite**: This is the recommended method to replicate the final report results. It runs all 90 simulations automatically.
2.  **Run Individual Tests**: This method is for examining or verifying the performance of any single configuration.

### 1. Run the Full Experiment Suite (Recommended)

This is the simplest and most effective way to evaluate the project. The `run_experiments.py` script will automatically handle all necessary setup and cleanup.

**What this script does:**
1.  Safely removes any old experimental results and population initializations. **It will NOT delete the provided `scenario-*.json` files.**
2.  Initializes new populations for all 6 scenarios with sizes 100 (small), 200 (medium), and 300 (large), using the existing scenario files.
3.  Systematically runs **5 independent trials** for each of the **6 scenarios** with each of the **3 predefined parameter sets** (Baseline, Exploration, Exploitation), for a total of 90 runs.
4.  Parses all results and calculates the aggregated statistics.
5.  Prints the final, formatted summary tables to the console and saves them to `data/experiments/final_summary_report.csv`.

**To execute, simply run the following command from the project's root directory:**
```bash
python run_experiments.py
