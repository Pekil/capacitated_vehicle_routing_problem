import sys
import os
import argparse
import csv
import shutil
import json

# random comment

from src.vrp.problem_set import generate_instances, scenario_definitions
from src.vrp.problem import ProblemInstance
from src.ga.individual import Individual
from src.ga.fitness import FitnessEvaluator
from src.ga.logger import GenerationLogger
from src.ga.run_sim import run_sim
from src.visualizer.plotter import Plotter

# ... (handle_status, handle_generate, handle_init, handle_run, handle_reset functions are unchanged) ...
def handle_status():
    print("--- VRP Problem Set Status ---")
    data_dir = "data"
    generations_dir = "data/generations"

    # Updated logic: Check for JSON files first
    for scenario_name in scenario_definitions.keys():
        json_path = os.path.join(data_dir, f"scenario-{scenario_name}.json")
        if not os.path.exists(json_path):
            print(f"  - {scenario_name}: Scenario file does not exist.")
            continue

        log_path = os.path.join(generations_dir, scenario_name, 'log.csv')
        if not os.path.exists(log_path):
            print(f"  - {scenario_name}: Generated, but not initialized.")
            continue

        try:
            with open(log_path, 'r') as f:
                # Check if file has more than just a header
                if len(f.readlines()) < 2:
                     print(f"  - {scenario_name}: Initialized, but not run.")
                     continue
                f.seek(0) # Reset file pointer
                reader = csv.reader(f)
                header = next(reader)
                gen_0_data = next(reader)
                data_dict = dict(zip(header, gen_0_data))
                fitness = float(data_dict['best_fitness'])
                if fitness == float('inf'):
                    print(f"  - {scenario_name}: Initialized. No feasible solution found in Gen 0.")
                else:
                    print(f"  - {scenario_name}: Run complete. Best initial fitness: {fitness:.2f}")
        except (StopIteration, ValueError):
                print(f"  - {scenario_name}: Log file is empty or corrupt.")

    print("\nHint: Use '-generate', '-init -pop <size>', '-run -s <name>', or '-viz <name>'.")


def handle_generate():
    print("--- Generating VRP Scenario Files ---")
    generate_instances()
    print("\nScenario files generated successfully in 'data/' directory.")

def handle_init(pop_size, scenario_name=None):
    scenarios = generate_instances()
    
    # If a specific scenario is targeted, filter the dictionary
    if scenario_name:
        if scenario_name not in scenarios:
            print(f"Error: Scenario '{scenario_name}' not found.")
            return
        # Create a new dictionary with only the target scenario
        scenarios_to_process = {scenario_name: scenarios[scenario_name]}
        print(f"--- Initializing scenario '{scenario_name}' with population size: {pop_size} ---")
    else:
        scenarios_to_process = scenarios
        print(f"--- Initializing all scenarios with population size: {pop_size} ---")

    for name, scenario_data in scenarios_to_process.items():
        print(f"\n===== Processing Scenario: {name} =====")
        
        problem = ProblemInstance(scenario_data)
        logger = GenerationLogger(problem)
        evaluator = FitnessEvaluator(problem)
        
        population = [Individual(problem) for _ in range(pop_size)]

        evaluated_population = []
        feasible_count = 0
        for i, individual in enumerate(population):
            sys.stdout.write(f"\rEvaluating individual {i+1}/{pop_size}...")
            sys.stdout.flush()
            fitness, routes = evaluator.evaluate(individual)
            if fitness != float('inf'):
                feasible_count += 1
            
            evaluated_population.append({
                "individual": individual,
                "fitness": fitness,
                "routes": routes
            })
        print()

        logger.log_initial_population(evaluated_population)
        
        feasibility_percentage = (feasible_count / pop_size) * 100
        print(f"Feasibility: {feasible_count}/{pop_size} ({feasibility_percentage:.2f}%) of individuals had a valid solution.")

    print("\n--- Initialization complete. ---")


def handle_run(scenario_name):
    print(f"--- Running GA scenario: {scenario_name} ---")

    gen0_path = os.path.join("data", "generations", scenario_name, "gen_0.csv") # <-- Corrected filename
    if not os.path.exists(gen0_path):
        print("Error: gen_0.csv not found. Please run the '-init' command first.")
        return
    
    json_path = os.path.join("data", f"scenario-{scenario_name}.json")
    if not os.path.exists(json_path):
        print("Error: Scenario JSON file not found. Please run the '-generate' command first.")
        return
    
    with open(json_path, 'r') as f:
        scenario_data = json.load(f)
    
    problem = ProblemInstance(scenario_data)
    logger = GenerationLogger(problem)
    evaluator = FitnessEvaluator(problem)
    
    population = []
    fitness_pop_0 = []
    with open(gen0_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fitness_pop_0.append(float(row['fitness']))
            chromosome_str = row['chromosome']
            chromosome = [int(gene) for gene in chromosome_str.split('-')]
            # Renamed variable to avoid shadowing class name
            ind = Individual(problem, chromosome=chromosome)
            population.append(ind)
    
    print(f"Successfully loaded {len(population)} individuals from {gen0_path}")
    
    run_sim(problem, logger, evaluator, population, fitness_pop_0)

# <-- MODIFIED: Function now accepts a 'speed' parameter
def handle_visualize(scenario_name, speed):
    print(f"--- Visualizing evolution for scenario: {scenario_name} ---")

    log_path = os.path.join("data", "generations", scenario_name, "log.csv")
    if not os.path.exists(log_path):
        print(f"Error: Log file not found at '{log_path}'.")
        print("Please run the simulation with '-run -s {scenario_name}' first.")
        return

    json_path = os.path.join("data", f"scenario-{scenario_name}.json")
    if not os.path.exists(json_path):
        print(f"Error: Scenario file not found at '{json_path}'.")
        return

    with open(json_path, 'r') as f:
        scenario_data = json.load(f)
    problem = ProblemInstance(scenario_data)

    evolution_data = []
    with open(log_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            routes_str = row['best_routes']
            routes = []
            if routes_str:
                routes = [[int(c) for c in r.split('-')] for r in routes_str.split(';')]

            evolution_data.append({
                'generation': int(row['generation']),
                'best_fitness': float(row['best_fitness']),
                'best_routes': routes
            })
    
    if not evolution_data:
        print("Log file is empty. Nothing to visualize.")
        return

    # <-- MODIFIED: Include speed in the status message
    print(f"Loaded {len(evolution_data)} generations. Starting animation at {speed} gen/s...")

    plotter = Plotter(title=f"Evolution for {scenario_name}")
    # <-- MODIFIED: Pass the speed to the animation method
    plotter.animate_evolution(problem, evolution_data, speed)

def handle_reset():
    print("--- Resetting VRP Environment ---")
    data_dir = "data"
    generations_dir = os.path.join(data_dir, "generations")

    print("Deleting scenario files...")
    deleted_scenarios = 0
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.startswith("scenario-") and filename.endswith(".json"):
                os.remove(os.path.join(data_dir, filename))
                deleted_scenarios += 1
    print(f"Removed {deleted_scenarios} scenario file(s).")

    print("Deleting generation logs...")
    if os.path.exists(generations_dir):
        shutil.rmtree(generations_dir)
        print(f"Removed directory and all its contents: {generations_dir}")
    else:
        print("Generations directory not found, nothing to delete.")
    
    print("\n--- Reset complete. ---")


def main():
    parser = argparse.ArgumentParser(description="VRP Genetic Algorithm runner.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-generate', action='store_true', help="Generate the scenario JSON files only.")
    parser.add_argument('-init', action='store_true', help="Initialize problem sets and create Generation 0 logs.")
    parser.add_argument('-pop', type=int, help="Population size for initialization (used with -init).")
    parser.add_argument('-run', action='store_true', help="Run the Genetic Algorithm.")
    parser.add_argument('-s', type=str, help="Specify scenario name (used with -run, -viz, and optionally with -init).")
    parser.add_argument('-reset', action='store_true', help="Remove all generated scenario files and log data.")
    parser.add_argument('-viz', type=str, help="Visualize the evolution from a log file. Provide scenario name (e.g., s-1).")
    # <-- MODIFIED: Add the new --speed argument
    parser.add_argument('--speed', type=int, default=10, help="Set animation speed in generations per second (used with -viz). Default: 10.")


    args = parser.parse_args()

    if args.generate:
        handle_generate()
    elif args.init:
        if not args.pop:
            print("Error: -pop <size> is required when using -init.")
            sys.exit(1)
        handle_init(args.pop, args.s)
    elif args.run:
        if not args.s:
            print("Error: -s <scenario_name> is required when using -run.")
            sys.exit(1)
        handle_run(args.s)
    # <-- MODIFIED: Pass the speed argument to the handler
    elif args.viz:
        handle_visualize(args.viz, args.speed)
    elif args.reset:
        handle_reset()
    else:
        handle_status()

if __name__ == "__main__":
    main()