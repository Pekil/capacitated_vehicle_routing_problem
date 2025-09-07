import sys
import os
import argparse
import csv
import shutil
import json

from src.vrp.problem_set import generate_instances, scenario_definitions
from src.vrp.problem import ProblemInstance
from src.ga.individual import Individual
from src.ga.fitness import FitnessEvaluator
from src.ga.logger import GenerationLogger
from src.ga.run_sim import run_sim
from src.visualizer.plotter import Plotter

# ... (handle_status, handle_generate, handle_run, handle_visualize, handle_reset are unchanged) ...
def handle_status():
    print("--- VRP Problem Set Status ---")
    data_dir = "data"
    generations_dir = "data/generations"

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
                if len(f.readlines()) < 2:
                     print(f"  - {scenario_name}: Initialized, but not run.")
                     continue
                f.seek(0)
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

def handle_init(pop_sizes: list[int]):
    # 1. Validate the number of population size arguments
    if len(pop_sizes) not in [1, 3]:
        print("Error: -pop requires either 1 value (e.g., 100) or 3 values (e.g., 100 200 300).")
        sys.exit(1)

    # 2. Create a mapping from scenario prefix to population size
    pop_map = {}
    if len(pop_sizes) == 1:
        size = pop_sizes[0]
        pop_map = {'s': size, 'm': size, 'l': size}
        print(f"--- Preparing to initialize all scenarios with population size: {size} ---")
    else: # len is 3
        pop_map = {'s': pop_sizes[0], 'm': pop_sizes[1], 'l': pop_sizes[2]}
        print(f"--- Preparing to initialize with sizes: Small={pop_map['s']}, Medium={pop_map['m']}, Large={pop_map['l']} ---")

    scenarios = generate_instances()

    # 3. SAFETY CHECK: Abort if any gen_0 files already exist
    for scenario_name in scenarios:
        gen0_path = os.path.join("data", "generations", scenario_name, "gen_0.csv")
        if os.path.exists(gen0_path):
            print(f"\nError: Initialization file '{gen0_path}' already exists.")
            print("To prevent overwriting an experiment, please run 'python main.py -reset' or manually delete the 'data/generations' folder.")
            sys.exit(1)

    # 4. If safety check passes, proceed with initialization
    for name, scenario_data in scenarios.items():
        prefix = name[0] # 's', 'm', or 'l'
        pop_size = pop_map[prefix]

        print(f"\n===== Processing Scenario: {name} with Population: {pop_size} =====")

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

    gen0_path = os.path.join("data", "generations", scenario_name, "gen_0.csv")
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
            ind = Individual(problem, chromosome=chromosome)
            population.append(ind)

    print(f"Successfully loaded {len(population)} individuals from {gen0_path}")

    run_sim(problem, logger, evaluator, population, fitness_pop_0)

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

    print(f"Loaded {len(evolution_data)} generations. Starting animation at {speed} gen/s...")

    plotter = Plotter(title=f"Evolution for {scenario_name}")
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
    # <-- IMPLEMENTED AS REQUESTED
    parser.add_argument('-pop', type=int, nargs='+', help="Population size(s). Use 1 value for all, or 3 for s, m, l.")
    parser.add_argument('-run', action='store_true', help="Run the Genetic Algorithm.")
    parser.add_argument('-s', type=str, help="Specify scenario name (used with -run and -viz).")
    parser.add_argument('-reset', action='store_true', help="Remove all generated scenario files and log data.")
    parser.add_argument('-viz', type=str, help="Visualize the evolution from a log file. Provide scenario name (e.g., s-1).")
    parser.add_argument('--speed', type=int, default=10, help="Set animation speed in generations per second (used with -viz). Default: 10.")

    args = parser.parse_args()

    if args.generate:
        handle_generate()
    elif args.init:
        if not args.pop:
            print("Error: -pop <size(s)> is required when using -init.")
            sys.exit(1)
        # <-- IMPLEMENTED AS REQUESTED
        handle_init(args.pop)
    elif args.run:
        if not args.s:
            print("Error: -s <scenario_name> is required when using -run.")
            sys.exit(1)
        handle_run(args.s)
    elif args.viz:
        # This argument is positional in the handler, so we need a value.
        # It's better to check here if the value is provided.
        if not args.viz:
            print("Error: a scenario name is required when using -viz.")
            sys.exit(1)
        handle_visualize(args.viz, args.speed)
    elif args.reset:
        handle_reset()
    else:
        handle_status()

if __name__ == "__main__":
    main()