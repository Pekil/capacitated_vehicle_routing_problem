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

## -- Configuration -- ##
runs_per = 1 # TODO: change to 20
output_base_dir = "results"
parameter_sets = [
    {
        "name": "Baseline",
        "population_size": 100,
        "generations": 500,
        "crossover_prob": 0.7,
        "mutation_prob": 0.2,
        "total_evaluations": 100 * 500  # 50,000
    },
    {
        "name": "Deep Search",
        "population_size": 50,
        "generations": 1000,
        "crossover_prob": 0.7,
        "mutation_prob": 0.2,
        "total_evaluations": 50 * 1000  # 50,000
    },
    {
        "name": "High Exploration",
        "population_size": 100,
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

## -- Main Function -- ##
def main():
    ## load problem instances into memory && error handling
    problem_instances: ProblemSet = load_CVRP()
    if problem_instances:
        print('Problem instances loaded successfully')
    ## create fitness evaluator
    fitnessEvaluators = [
        FitnessEvaluator(problem_instance)
        for problem_instance in problem_instances
    ]
    
    ## run NSGA-II for each problem instance and parameter set
    for i in range(len(problem_instances)):
        for parameter_set in parameter_sets:
            for run in range(runs_per):
                start = time.time()

                final_front, runtime, evaluations = run_nsga2(
                    problem_instances[i],
                    fitnessEvaluators[i],
                    parameter_set["generations"],
                    parameter_set["crossover_prob"],
                    parameter_set["mutation_prob"],
                    parameter_set["population_size"]
                )

                log_run_results(
                    output_base_dir, 
                    problem_instances[i], 
                    parameter_set, 
                    run, 
                    runtime, 
                    evaluations, 
                    final_front
                )
                print(f"Run {run + 1}/{runs_per} for {problem_instances[i].name} ({parameter_set['name']}) ok. Logged results.")# For now, reconstruct final front from current e
    return 0
if __name__ == "__main__":
    main()