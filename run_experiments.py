import os
import shutil
import subprocess
import json
import csv
import pandas as pd
import numpy as np
import sys

# --- Configuration ---
# Use the currently running Python interpreter for all subprocesses
PYTHON_EXECUTABLE = sys.executable

# Scenarios to run
SCENARIOS = ['s-1', 's-2', 'm-1', 'm-2', 'l-1', 'l-2']

# <-- MODIFIED: Population sizes for Small, Medium, and Large scenarios set correctly
POPULATION_SIZES = [100, 200, 300]

# Parameter sets to test
PARAMS = [
    {'name': 'Baseline', 'gen': 5000, 'pc': 0.9, 'pm': 0.1},
    {'name': 'Exploration', 'gen': 10000, 'pc': 0.8, 'pm': 0.3},
    {'name': 'Exploitation', 'gen': 5000, 'pc': 0.95, 'pm': 0.01}
]

# Number of independent runs for each configuration
NUM_RUNS = 5

# --- Directory Definitions ---
EXPERIMENTS_BASE_DIR = "data/experiments"
GENERATIONS_DIR = "data/generations"


def run_single_simulation(scenario, params, run_id, output_dir):
    """Executes a single run of main.py with the specified parameters."""
    command = [
        PYTHON_EXECUTABLE, 'main.py', '-run',
        '-s', scenario,
        '--gen', str(params['gen']),
        '--pc', str(params['pc']),
        '--pm', str(params['pm']),
        '--output', output_dir
    ]
    
    print(f"  Running trial {run_id}... ", end='', flush=True)
    result = subprocess.run(command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        error_message = result.stderr.decode()
        print(f"FAILED.\n--- ERROR in subprocess for trial {run_id} ---\n{error_message}\n---")
        raise subprocess.CalledProcessError(result.returncode, command, stderr=result.stderr)
    
    print("Done.")


def parse_run_results(output_dir):
    """Parses the log and metadata files to extract key performance metrics."""
    log_path = os.path.join(output_dir, 'log.csv')
    metadata_path = os.path.join(output_dir, 'metadata.json')

    with open(log_path, 'r') as f:
        reader = csv.DictReader(f)
        log_data = list(reader)
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    initial_best_fitness = float(log_data[0]['best_fitness'])
    final_best_fitness = float(log_data[-1]['best_fitness'])

    convergence_gen = 0
    for row in log_data:
        if float(row['best_fitness']) == final_best_fitness:
            convergence_gen = int(row['generation'])
            break
            
    return {
        'initial_best_fitness': initial_best_fitness,
        'final_best_fitness': final_best_fitness,
        'convergence_generation': convergence_gen,
        'compute_time': metadata.get('simulation_time_seconds', 0)
    }

def main():
    print("--- Starting Full Experiment Suite ---")

    # --- Step 1: Preparation ---
    print("\n[Phase 1] Preparing environment for a clean experiment run...")
    
    if os.path.exists(EXPERIMENTS_BASE_DIR):
        print(f"  - Removing old experiment results from '{EXPERIMENTS_BASE_DIR}'...")
        shutil.rmtree(EXPERIMENTS_BASE_DIR)
        
    if os.path.exists(GENERATIONS_DIR):
        print(f"  - Removing old initializations from '{GENERATIONS_DIR}'...")
        shutil.rmtree(GENERATIONS_DIR)
        
    print("  - Initializing new populations for existing scenarios...")
    
    pop_size_strs = [str(p) for p in POPULATION_SIZES]
    init_command = [PYTHON_EXECUTABLE, 'main.py', '-init', '-pop'] + pop_size_strs
    subprocess.run(init_command, check=True)
    
    print("[Phase 1] Complete.")

    # --- Step 2: Running All Simulations ---
    print("\n[Phase 2] Executing all simulation runs...")
    all_experiment_results = []
    
    for scenario in SCENARIOS:
        for i, params in enumerate(PARAMS):
            param_set_name = params['name']
            print(f"\nRunning Configuration: Scenario='{scenario}', Params='{param_set_name}'")
            
            run_results_for_config = []
            
            for run_id in range(1, NUM_RUNS + 1):
                output_dir = os.path.join(EXPERIMENTS_BASE_DIR, scenario, f"params_{i}_{param_set_name}", f"run_{run_id}")
                os.makedirs(output_dir, exist_ok=True)
                
                try:
                    run_single_simulation(scenario, params, run_id, output_dir)
                    results = parse_run_results(output_dir)
                    run_results_for_config.append(results)
                except subprocess.CalledProcessError:
                    print(f"Halting experiments due to an error in one of the simulation runs.")
                    return

            all_experiment_results.append({
                'scenario': scenario,
                'param_set_name': param_set_name,
                'raw_results': run_results_for_config
            })
    print("\n[Phase 2] All simulations complete.")

    # --- Step 3: Aggregating and Reporting Results ---
    print("\n[Phase 3] Aggregating results and generating report tables...")
    
    report_data = []
    
    for experiment in all_experiment_results:
        results = experiment['raw_results']
        if not results:
            continue
            
        final_fitness_values = [r['final_best_fitness'] for r in results]
        convergence_gen_values = [r['convergence_generation'] for r in results]
        compute_time_values = [r['compute_time'] for r in results]
        initial_fitness_values = [r['initial_best_fitness'] for r in results]

        avg_initial_fitness = np.mean(initial_fitness_values)
        avg_final_fitness = np.mean(final_fitness_values)
        
        improvement = ((avg_initial_fitness - avg_final_fitness) / avg_initial_fitness) * 100 if avg_initial_fitness > 0 else 0

        report_row = {
            'Scenario': experiment['scenario'],
            'Parameter Set': experiment['param_set_name'],
            'Best Fitness': np.min(final_fitness_values),
            'Average Fitness': avg_final_fitness,
            'Worst Fitness': np.max(final_fitness_values),
            'Stdev Fitness': np.std(final_fitness_values),
            'Avg Convergence Gen': np.mean(convergence_gen_values),
            'Avg Compute Time (s)': np.mean(compute_time_values),
            '% Improvement': improvement
        }
        report_data.append(report_row)
        
    df = pd.DataFrame(report_data)
    
    os.makedirs(EXPERIMENTS_BASE_DIR, exist_ok=True)
    report_csv_path = os.path.join(EXPERIMENTS_BASE_DIR, "final_summary_report.csv")
    df.to_csv(report_csv_path, index=False, float_format='%.2f')

    print("\n--- FINAL REPORT ---")
    
    for scenario in SCENARIOS:
        print(f"\n--- Results for Scenario: {scenario} ---")
        scenario_df = df[df['Scenario'] == scenario].drop('Scenario', axis=1)
        print(scenario_df.to_string(index=False, float_format='%.2f'))
        
    print(f"\n[Phase 3] Complete. Full report saved to '{report_csv_path}'")
    print("\n--- Experiment Suite Finished ---")


if __name__ == '__main__':
    main()