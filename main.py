import os
from src.vrp.load_set import load_problem_instance
from src.vrp.problem import ProblemInstance
from src.ga.fitness import FitnessEvaluator
from src.ga.individual import Individual
from src.ga.algorithms import run_nsga2, run_spea2
from src.ga.pareto_selection import fast_non_dominated_sort
from src.ga.logger import log_run_results
import glob
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat

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
    problem, evaluator, param_set, run_idx, base_dir = run_args
    final_front, runtime, evaluations = run_nsga2(
        problem,
        evaluator,
        param_set["generations"],
        param_set["crossover_prob"],
        param_set["mutation_prob"],
        param_set["population_size"]
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
    print(f"NSGA-II Run {run_idx + 1}/{runs_per} for {problem.name} ({param_set['name']}) ok.")

def run_and_log_spea2(run_args):
    """Helper function to run SPEA2 and log results, designed for parallel execution."""
    problem, evaluator, param_set, run_idx, base_dir = run_args
    final_front, runtime, evaluations = run_spea2(
        problem,
        evaluator,
        param_set["generations"],
        param_set["crossover_prob"],
        param_set["mutation_prob"],
        param_set["population_size"],
        param_set["archive_size"]
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
    print(f"SPEA2 Run {run_idx + 1}/{runs_per} for {problem.name} ({param_set['name']}) ok.")

## -- Main Function -- ##
def main():
    problem_instances: ProblemSet = load_CVRP()
    if not problem_instances:
        print("No problem instances loaded. Exiting.")
        return

    fitness_evaluators = [FitnessEvaluator(p) for p in problem_instances]

    with ProcessPoolExecutor() as executor:
        for i, (problem, evaluator) in enumerate(zip(problem_instances, fitness_evaluators)):
            for param_set in parameter_sets:
                # Prepare arguments for parallel NSGA-II runs
                nsga2_args = zip(
                    repeat(problem),
                    repeat(evaluator),
                    repeat(param_set),
                    range(runs_per),
                    repeat(output_base_dir)
                )
                # Run NSGA-II simulations in parallel
                executor.map(run_and_log_nsga2, nsga2_args)

                # Prepare arguments for parallel SPEA2 runs
                spea2_args = zip(
                    repeat(problem),
                    repeat(evaluator),
                    repeat(param_set),
                    range(runs_per),
                    repeat(output_base_dir)
                )
                # Run SPEA2 simulations in parallel
                executor.map(run_and_log_spea2, spea2_args)

    return 0

if __name__ == "__main__":
    main()