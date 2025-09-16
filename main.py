import sys
import os
import argparse
import csv
import shutil
import json
import time
import matplotlib.pyplot as plt
from src.vrp.problem import ProblemInstance
from src.ga.individual import Individual
from src.ga.fitness import FitnessEvaluator
from src.ga.logger import GenerationLogger
from src.ga.run_sim import run_sim
from src.visualizer.plotter import Plotter

def handle_status():
    print("--- VRP Status ---")
    print("Scenario generation and initialization are removed in this project.")
    print("Use '-run' with your chosen data source once added.")

def handle_run(scenario_name, generations, pc, pm, output_dir=None):
    # This prevents the top-level print statements from cluttering experiment logs
    is_experiment_run = output_dir is not None
    
    if not is_experiment_run:
        print(f"--- Running GA scenario: {scenario_name} ---")
        print(f"Parameters -> Generations: {generations}, Crossover Pc: {pc}, Mutation Pm: {pm}")

    start_ts = time.perf_counter()

    # The init command still saves to the default location, which is fine
    gen0_path = os.path.join("data", "generations", scenario_name, "gen_0.csv")
    if not os.path.exists(gen0_path):
        print(f"Error: gen_0.csv not found for scenario '{scenario_name}'. Please run the '-init' command first.")
        return

    json_path = os.path.join("data", f"scenario-{scenario_name}.json")
    if not os.path.exists(json_path):
        print(f"Error: Scenario JSON file not found. Please run the '-generate' command first.")
        return
        
    with open(json_path, 'r') as f:
        scenario_data = json.load(f)
        
    problem = ProblemInstance(scenario_data)
    logger = GenerationLogger(problem, output_dir)
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
            
    if not is_experiment_run:
        print(f"Successfully loaded {len(population)} individuals from {gen0_path}")

    run_sim(problem, logger, evaluator, population, fitness_pop_0, generations, pc, pm)

    end_ts = time.perf_counter()
    elapsed = end_ts - start_ts
    
    if not is_experiment_run:
        print(f"Total simulation time: {elapsed:.2f} seconds")

    # The output directory for the metadata is now determined by the logger
    metadata_path = os.path.join(logger.output_dir, "metadata.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    metadata['simulation_time_seconds'] = round(elapsed, 2)
    metadata['ga_parameters'] = {
        'population_size': len(population),
        'generations': generations,
        'crossover_probability': pc,
        'mutation_probability': pm
    }

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    if not is_experiment_run:
        print(f"Performance metrics saved to '{metadata_path}'")

def handle_visualize(scenario_name, speed):
    print(f"--- Visualizing evolution for scenario: {scenario_name} ---")
    log_path = os.path.join("data", "generations", scenario_name, "log.csv")
    if not os.path.exists(log_path):
        print(f"Error: Log file not found at '{log_path}'. Please run the simulation first.")
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


def handle_plot(scenario_name):
    print(f"--- Generating convergence plot for scenario: {scenario_name} ---")
    
    log_path = os.path.join("data", "generations", scenario_name, "log.csv")
    output_path = os.path.join("data", "generations", scenario_name, "convergence_plot.png")

    if not os.path.exists(log_path):
        print(f"Error: Log file not found at '{log_path}'. Please run a simulation first.")
        return

    generations, best_fitness, avg_fitness, worst_fitness = [], [], [], []

    with open(log_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            generations.append(int(row['generation']))
            best_fitness.append(float(row['best_fitness']))
            avg_fitness.append(float(row['average_fitness']))
            worst_fitness.append(float(row['worst_fitness']))

    plt.figure(figsize=(12, 7))
    plt.plot(generations, best_fitness, label='Best Fitness', color='cyan', linewidth=2)
    plt.plot(generations, avg_fitness, label='Average Fitness', color='magenta', linestyle='--')
    plt.plot(generations, worst_fitness, label='Worst Fitness', color='red', linestyle=':')
    
    plt.title(f'GA Convergence for Scenario: {scenario_name}', fontsize=16)
    plt.xlabel('Generation', fontsize=12)
    plt.ylabel('Total Distance (Fitness)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(output_path)
    plt.close()
    print(f"Convergence plot saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="VRP Genetic Algorithm runner.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-reset', action='store_true', help="Remove generated log data.")
    
    parser.add_argument('-run', action='store_true', help="Run the Genetic Algorithm.")
    parser.add_argument('-s', type=str, help="Specify scenario name (used with -run and -plot).")
    parser.add_argument('--gen', type=int, default=5000, help="Number of generations for the GA. Default: 5000.")
    parser.add_argument('--pc', type=float, default=0.9, help="Crossover probability for the GA. Default: 0.9.")
    parser.add_argument('--pm', type=float, default=0.1, help="Mutation probability for the GA. Default: 0.1.")
    
    parser.add_argument('-viz', type=str, help="Visualize the evolution. Provide scenario name (e.g., s-1).")
    parser.add_argument('--speed', type=int, default=10, help="Set animation speed in gen/s (used with -viz). Default: 10.")
    
    parser.add_argument('-plot', action='store_true', help="Plots the fitness convergence curve (requires -s).")
    parser.add_argument('--output', type=str, help=argparse.SUPPRESS) # For internal use by experiment runner
    
    args = parser.parse_args()

    if args.run:
        if not args.s:
            print("Error: -s <scenario_name> is required when using -run.")
            sys.exit(1)
        handle_run(args.s, args.gen, args.pc, args.pm, args.output) # Pass the new argument
    elif args.viz:
        handle_visualize(args.viz, args.speed)
    elif args.reset:
        handle_reset()
    elif args.plot:
        if not args.s:
            print("Error: -s <scenario_name> is required when using -plot.")
            sys.exit(1)
        handle_plot(args.s)
    else:
        handle_status()

if __name__ == "__main__":
    main()