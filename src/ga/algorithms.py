from src.vrp.problem import ProblemInstance
from src.ga.fitness import FitnessEvaluator
from src.ga.individual import Individual
from src.ga.operators import pmx_crossover, swap_mutation
from src.ga.pareto_selection import fast_non_dominated_sort, calculate_crowding_distance
from src.ga.selection import tournament_selection

import time
import sys
import random


def create_valid_pop(problem: ProblemInstance, population_size: int) -> list[Individual]:
    """
    Creates a hybrid initial population.
    - 50% of individuals are created with purely random chromosomes.
    - 50% are created using a capacity-packing heuristic to generate
      chromosomes that are likely to be capacity-feasible.
    """
    packed_count = population_size // 2
    random_count = population_size - packed_count

    # 1. Create purely random individuals
    pop = [Individual(problem) for _ in range(random_count)]
    
    # 2. Create capacity-packed individuals
    for _ in range(packed_count):
        # Start with a random permutation of customers to process
        remaining_customers = list(range(1, problem.num_customers + 1))
        random.shuffle(remaining_customers)
        
        packed_chromosome = []
        
        # Keep creating routes until all customers are served
        while remaining_customers:
            current_route = []
            current_demand = 0
            
            # Iterate through available customers to fill one vehicle
            # A copy is needed as we modify the list we are iterating over
            for customer_id in remaining_customers[:]:
                demand = problem.customer_demands[customer_id - 1]
                if current_demand + demand <= problem.vehicle_capacity:
                    current_route.append(customer_id)
                    current_demand += demand
                    # Remove customer from pool so it's not considered for the next vehicle
                    remaining_customers.remove(customer_id)

            # Add the customers for this packed vehicle to the chromosome
            packed_chromosome.extend(current_route)
        
        # Add the new individual with the capacity-aware chromosome
        pop.append(Individual(problem, chromosome=packed_chromosome))
        
    return pop


def run_nsga2(
    problem: ProblemInstance,
    evaluator: FitnessEvaluator,
    generations: int,
    pc: float,
    pm: float,
    population_size: int,
) -> bool:
    ## create population
    pop: list[Individual] = create_valid_pop(problem, population_size)
    
    sys.stdout.flush()
    print(f"""
        --------------------------------
        Initialisation: random
        Problem: {problem.name}
        Generations: {generations}
        Population size: {population_size}
        Crossover probability: {pc}
        Mutation probability: {pm}
    """)

    ## evaluate and store results in individuals
    for indiv in pop:
        fitness_values, routes = evaluator.evaluate(indiv)
        indiv.set_evaluation(fitness_values, routes)

    # -- Initial Population Logging --
    total_distances = [ind.objectives[0] for ind in pop]
    longest_routes = [ind.objectives[1] for ind in pop]
    unique_chromosomes = set(tuple(ind.chromosome) for ind in pop)

    avg_total_dist = sum(total_distances) / len(total_distances)
    best_total_dist = min(total_distances)
    avg_longest_route = sum(longest_routes) / len(longest_routes)
    best_longest_route = min(longest_routes)

    print(f"""
        Unique Solutions: {len(unique_chromosomes)}/{population_size}
        Total Distance (Avg): {avg_total_dist:.2f}
        Total Distance (Best): {best_total_dist:.2f}
        Longest Route (Avg): {avg_longest_route:.2f}
        Longest Route (Best): {best_longest_route:.2f}
        -------------------------------------
    """)

    start_time = time.time()
    evaluations = len(pop)  # initial evaluations

    # Generational loop
    print(f"NSGA-II start: gens={generations}, pop={population_size}")
    sys.stdout.flush()
    for g in range(generations):
        # Rank current population and compute crowding distances per front
        fronts = fast_non_dominated_sort(pop)
        for front in fronts:
            calculate_crowding_distance(front)

        # Build mating pool via tournament selection
        mating_pool: list[Individual] = [tournament_selection(pop) for _ in range(population_size)]

        # Variation: create offspring of size N
        offspring: list[Individual] = []
        for i in range(0, population_size, 2):
            p1 = mating_pool[i % population_size]
            p2 = mating_pool[(i + 1) % population_size]
            c1, c2 = pmx_crossover(p1, p2, pc)
            swap_mutation(c1, pm)
            swap_mutation(c2, pm)
            offspring.append(c1)
            if len(offspring) < population_size:
                offspring.append(c2)

        # Evaluate offspring
        for child in offspring:
            fitness_values, routes = evaluator.evaluate(child)
            child.set_evaluation(fitness_values, routes)
        evaluations += len(offspring)

        # Environmental selection: combine and select next generation
        combined = pop + offspring
        combined_fronts = fast_non_dominated_sort(combined)

        next_pop: list[Individual] = []
        for front in combined_fronts:
            if len(next_pop) + len(front) <= population_size:
                next_pop.extend(front)
            else:
                # Need to take only a subset from this front
                calculate_crowding_distance(front)
                # Sort descending by crowding distance
                front.sort(key=lambda ind: ind.crowding_distance, reverse=True)
                slots = population_size - len(next_pop)
                next_pop.extend(front[:slots])
                break

        pop = next_pop

        # Progress output every ~5% of gens or at the end
        step = max(1, generations // 20)
        if (g + 1) % step == 0 or g == generations - 1:
            best_td, best_lr = min(ind.objectives for ind in pop)
            num_rank1 = len(fronts[0]) if fronts else 0
            print(f"Gen {g+1}/{generations} | best_total={best_td:.2f} | best_longest_route={best_lr:.2f} | rank1={num_rank1}")
            sys.stdout.flush()

    end_time = time.time()
    runtime = end_time - start_time

    # Final front from the final population
    final_fronts = fast_non_dominated_sort(pop)
    final_front = final_fronts[0] if final_fronts else []

    # Return True for backward compatibility; main should use logger to persist
    # For now, we could adapt to return results if needed
    # But keep signature as requested
    return final_front, runtime, evaluations

def run_spea2(
    problem: ProblemInstance,
    evaluator: FitnessEvaluator,
    generations: int,
    pc: float,
    pm: float,
    population: list[Individual]
):
    pass