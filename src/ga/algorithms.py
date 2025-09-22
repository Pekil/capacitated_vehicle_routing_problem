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
    - 50% are created by finding random chromosomes that are "packable"
    """
    random_count = population_size // 2
    fixed_count = population_size - random_count

    # 1. Create purely random individuals
    pop = [Individual(problem) for _ in range(random_count)]

    # 2. Create individuals by finding random chromosomes that are packable
    packable_pop: list[Individual] = []
    # Add a safety break to prevent potential infinite loops
    max_attempts = fixed_count * 200
    attempts = 0
    while len(packable_pop) < fixed_count and attempts < max_attempts:
        tmp_ind = Individual(problem)
        if _is_packable(tmp_ind, problem):
            packable_pop.append(tmp_ind)
        attempts += 1

    # If not enough packable individuals were found, fill with random ones
    if len(packable_pop) < fixed_count:
        print(f"Warning: Could only find {len(packable_pop)}/{fixed_count} packable individuals. Filling rest randomly.")
        needed = fixed_count - len(packable_pop)
        packable_pop.extend([Individual(problem) for _ in range(needed)])
    else:
        print(f"Found {len(packable_pop)} packable individuals.. lets go")
    

    pop.extend(packable_pop)
    return pop


def _is_packable(ind: Individual, problem: ProblemInstance) -> bool:
    """
    Checks if a chromosome is "packable" by assigning customers to vehicles
    in the order they appear, starting a new vehicle only when the current
    one is full. Returns True if the number of vehicles used does not exceed
    the available number of vehicles.
    """
    chromosome = ind.chromosome
    demands = problem.customer_demands
    capacity = problem.vehicle_capacity
    num_vehicles = problem.num_vehicles

    if not chromosome:
        return True  # An empty chromosome is packable (uses 0 vehicles)

    vehicles_used = 1
    current_load = 0

    for customer_id in chromosome:
        # customer IDs are 1-based, but demands list is 0-indexed
        customer_demand = demands[customer_id - 1]

        if current_load + customer_demand <= capacity:
            current_load += customer_demand
        else:
            # Current vehicle is full, start a new one
            vehicles_used += 1
            if vehicles_used > num_vehicles:
                return False  # Exceeded available vehicles
            # The new vehicle starts with the current customer
            current_load = customer_demand
    
    return True


def run_nsga2(
    problem: ProblemInstance,
    evaluator: FitnessEvaluator,
    generations: int,
    pc: float,
    pm: float,
    population_size: int,
) -> tuple[list[Individual], float, int]:
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
        random.shuffle(mating_pool)

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