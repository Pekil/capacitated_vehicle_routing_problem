from src.vrp.problem import ProblemInstance
from src.ga.logger import GenerationLogger 
from src.ga.fitness import FitnessEvaluator 
from src.ga.individual import Individual
from src.ga.operators import pmx_crossover, swap_mutation

import random
from typing import List
import sys
import numpy as np

SelectionProbabilities = list[tuple[Individual, float]]
# <-- MODIFIED: Now takes separate lists as arguments
def calc_roulette_prob(population: List[Individual], fitness_values: List[float]) -> SelectionProbabilities:
    EPSILON = 1e-6
    
    combined = list(zip(population, fitness_values))
    valid_solutions = [(ind, fit) for ind, fit in combined if fit != float('inf')]

    if not valid_solutions:
        equal_prob = 1.0 / len(population)
        return [(ind, equal_prob) for ind in population]
        
    sorted_pop = sorted(valid_solutions, key=lambda item: item[1])
    
    highest_fitness = sorted_pop[-1][1]
    inversed_val_pop: list[tuple[Individual, float]] = [
        (indiv, (highest_fitness - fitness) + EPSILON)
        for indiv, fitness in sorted_pop
    ]

    TOT_VALUE = sum(item[1] for item in inversed_val_pop)
    return [(indiv, val / TOT_VALUE) for indiv, val in inversed_val_pop]

def select_parents(select_prob: SelectionProbabilities, num_parents: int) -> List[Individual]:
    if not select_prob:
        return []
    
    population, probabilities = zip(*select_prob)
    return random.choices(population=population, weights=probabilities, k=num_parents)

def run_sim(
    problem: ProblemInstance, 
    logger: GenerationLogger,  
    evaluator: FitnessEvaluator,
    population_0: List[Individual],
    fitness_pop_0: List[float],
    generations: int = 5000,
    pc: float = 0.9,
    pm: float = 0.1
):
    ## --- Hyperparameters ---
    EXIT_CON = generations
    Pc = pc
    Pm = pm

    # --- Initialize with clean, separated data structures ---
    current_population = population_0
    current_fitness_values = fitness_pop_0

    for gen in range(EXIT_CON + 1):
        # --- 1. Logging ---
        # Find the best individual to get its routes for the log
        best_idx = np.argmin(current_fitness_values)
        best_fitness = current_fitness_values[best_idx]
        best_individual = current_population[best_idx]
        
        # The only re-evaluation we do: get routes for the single best solution
        _, best_routes = evaluator.evaluate(best_individual)
        
        logger.log_generation(gen, current_fitness_values, best_fitness, best_routes)
        
        sys.stdout.write(f"\rGeneration {gen}/{EXIT_CON} | Best Fitness: {best_fitness:.2f}")
        sys.stdout.flush()

        if gen == EXIT_CON:
            break

        # --- 2. Parent Selection ---
        selection_probs = calc_roulette_prob(current_population, current_fitness_values)
        p1, p2 = select_parents(selection_probs, 2)
        
        # --- 3. Crossover & Mutation ---
        o1, o2 = pmx_crossover(p1, p2, Pc)
        swap_mutation(o1, Pm)
        swap_mutation(o2, Pm)

        # --- 4. Evaluate Offspring ---
        o1_fitness, _ = evaluator.evaluate(o1)
        o2_fitness, _ = evaluator.evaluate(o2)
        
        # --- 5. Replace Worst Individuals ---
        # Find the indices of the two worst individuals
        worst_indices = np.argsort(current_fitness_values)[-2:]
        
        # Replace the first worst with the first offspring
        current_population[worst_indices[0]] = o1
        current_fitness_values[worst_indices[0]] = o1_fitness
        
        # Replace the second worst with the second offspring
        current_population[worst_indices[1]] = o2
        current_fitness_values[worst_indices[1]] = o2_fitness

    print(f"\n\n--- Simulation Complete ---")
    final_best_fitness = min(current_fitness_values)
    print(f"Final best fitness after {EXIT_CON} generations: {final_best_fitness:.2f}")