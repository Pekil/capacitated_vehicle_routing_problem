import os
import argparse
import sys
from src.vrp.load_set import load_problem_instance
from src.vrp.problem import ProblemInstance
from src.ga.fitness import FitnessEvaluator
from src.ga.individual import Individual
from src.ga.algorithms import run_nsga2, run_spea2, create_valid_pop, save_population_chromosomes, load_population_from_file
from src.ga.pareto_selection import fast_non_dominated_sort
from src.ga.logger import log_run_results
import glob
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from contextlib import redirect_stdout, redirect_stderr

## -- Configuration -- ##
runs_per = 20
output_base_dir = "results"
parameter_sets = [
    {
        "name": "Baseline",
        "population_size": 100,
        "archive_size": 100,
        "generations": 500,
        "crossover_prob": 0.7,
        "mutation_prob": 0.2,
        "total_evaluations": 100 * 500  # 50,000
    },
    {
        "name": "Deep Search",
        "population_size": 50,
        "archive_size": 50,
        "generations": 1000,
        "crossover_prob": 0.7,
        "mutation_prob": 0.2,
        "total_evaluations": 50 * 1000  # 50,000
    },
    {
        "name": "High Exploration",
        "population_size": 100,
        "archive_size": 100,
        "generations": 500,
        "crossover_prob": 0.6,
        "mutation_prob": 0.4, # Higher mutation rate
        "total_evaluations": 100 * 500  # 50,000
    }
]

## -- Data Loading -- ##
ProblemSet = list[ProblemInstance]
def load_CVRP() -> ProblemSet:
    print("--- Loading VRP Problem Instances from .txt files ---")
    data_dir = "data"
    txt_files = glob.glob(os.path.join(data_dir, "*.txt"))
    problem_instances = []

    if not txt_files:
        print("No .txt files found in the data directory.")
        return problem_instances

    for file_path in txt_files:
        try:
            problem_instance = load_problem_instance(file_path)
            problem_instances.append(problem_instance)
        except Exception as e:
            print(f"\nError processing file {os.path.basename(file_path)}: {e}")

    return problem_instances

def run_and_log_nsga2(run_args):
    """Helper function to run NSGA-II and log results, designed for parallel execution."""
    problem, evaluator, param_set, run_idx, base_dir, initial_pop = run_args
    log_dir = os.path.join("data", "process_logs")
    log_file_path = os.path.join(log_dir, f"NSGA2-{problem.name}-{param_set['name']}-run{run_idx+1}.log")

    with open(log_file_path, 'w') as log_file:
        with redirect_stdout(log_file), redirect_stderr(log_file):
            # All print statements and errors from the algorithm will go to the log file
            final_front, runtime, evaluations = run_nsga2(
                problem,
                evaluator,
                param_set["generations"],
                param_set["crossover_prob"],
                param_set["mutation_prob"],
                param_set["population_size"],
                initial_pop=initial_pop
            )
            log_run_results(
                f"{base_dir}/NSGA-II",
                problem,
                param_set,
                run_idx,
                runtime,
                evaluations,
                final_front
            )
            # This print will also go to the log file
            print(f"NSGA-II Run {run_idx + 1}/{runs_per} for {problem.name} ({param_set['name']}) logged successfully.")
    
    return f"Finished: NSGA-II Run {run_idx + 1}/{runs_per} for {problem.name} ({param_set['name']})"


def run_and_log_spea2(run_args):
    """Helper function to run SPEA2 and log results, designed for parallel execution."""
    problem, evaluator, param_set, run_idx, base_dir, initial_pop = run_args
    log_dir = os.path.join("data", "process_logs")
    log_file_path = os.path.join(log_dir, f"SPEA2-{problem.name}-{param_set['name']}-run{run_idx+1}.log")

    with open(log_file_path, 'w') as log_file:
        with redirect_stdout(log_file), redirect_stderr(log_file):
            # All print statements and errors from the algorithm will go to the log file
            final_front, runtime, evaluations = run_spea2(
                problem,
                evaluator,
                param_set["generations"],
                param_set["crossover_prob"],
                param_set["mutation_prob"],
                param_set["population_size"],
                param_set["archive_size"],
                initial_pop=initial_pop
            )
            log_run_results(
                f"{base_dir}/SPEA2",
                problem,
                param_set,
                run_idx,
                runtime,
                evaluations,
                final_front
            )
            # This print will also go to the log file
            print(f"SPEA2 Run {run_idx + 1}/{runs_per} for {problem.name} ({param_set['name']}) logged successfully.")

    return f"Finished: SPEA2 Run {run_idx + 1}/{runs_per} for {problem.name} ({param_set['name']})"

## -- Main Function -- ##
def main():
    parser = argparse.ArgumentParser(description="Run NSGA-II or SPEA2 for VRP.")
    parser.add_argument(
        "-a", "--algorithm",
        choices=['nsga2', 'spea2'],
        required=True,
        help="The algorithm to execute."
    )
    args = parser.parse_args()

    problem_instances: ProblemSet = load_CVRP()
    if not problem_instances:
        print("No problem instances loaded. Exiting.")
        return

    # Create the directory for process-specific logs
    os.makedirs(os.path.join("data", "process_logs"), exist_ok=True)

    fitness_evaluators = [FitnessEvaluator(p) for p in problem_instances]

    with ProcessPoolExecutor() as executor:
        for i, (problem, evaluator) in enumerate(zip(problem_instances, fitness_evaluators)):
            for param_set in parameter_sets:
                print(f"\n--- Starting simulations for {problem.name} with '{param_set['name']}' parameters for {args.algorithm} ---")
                
                if args.algorithm == 'nsga2':
                    # For NSGA-II, create, save, and then run.
                    initial_pops = []
                    for run_idx in range(runs_per):
                        pop_file_path = f"{output_base_dir}/initial_populations/{problem.name}/run_{run_idx}_pop.json"
                        initial_pop = create_valid_pop(problem, param_set["population_size"])
                        save_population_chromosomes(initial_pop, pop_file_path)
                        initial_pops.append(initial_pop)

                    nsga2_args = zip(
                        repeat(problem),
                        repeat(evaluator),
                        repeat(param_set),
                        range(runs_per),
                        repeat(output_base_dir),
                        initial_pops
                    )
                    # Run NSGA-II simulations in parallel and print status as they complete
                    for result in executor.map(run_and_log_nsga2, nsga2_args):
                        print(result)

                elif args.algorithm == 'spea2':
                    # For SPEA2, load populations and then run.
                    initial_pops = []
                    run_indices = []
                    for run_idx in range(runs_per):
                        pop_file_path = f"{output_base_dir}/initial_populations/{problem.name}/run_{run_idx}_pop.json"
                        if not os.path.exists(pop_file_path):
                            print(f"Error: Initial population for run {run_idx} not found at {pop_file_path}. Please run NSGA-II first. Skipping this run.")
                            continue
                        
                        initial_pop = load_population_from_file(problem, pop_file_path)
                        initial_pops.append(initial_pop)
                        run_indices.append(run_idx)

                    if not initial_pops:
                        print(f"No valid initial populations found for {problem.name} with '{param_set['name']}'. Skipping SPEA2 runs for this configuration.")
                        continue

                    spea2_args = zip(
                        repeat(problem),
                        repeat(evaluator),
                        repeat(param_set),
                        run_indices,
                        repeat(output_base_dir),
                        initial_pops
                    )
                    # Run SPEA2 simulations in parallel and print status as they complete
                    for result in executor.map(run_and_log_spea2, spea2_args):
                        print(result)

    return 0

if __name__ == "__main__":
    main()