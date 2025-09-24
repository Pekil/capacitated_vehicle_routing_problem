import math
from typing import List
import numpy as np
from src.ga.individual import Individual

def _calculate_strength(combined_pop: List[Individual]) -> List[int]:
    """
    Calculates the S(i) value (strength) for each individual.
    Strength is the number of individuals an individual dominates.
    """
    strengths = [0] * len(combined_pop)
    for i, ind_i in enumerate(combined_pop):
        for j, ind_j in enumerate(combined_pop):
            if i == j:
                continue
            
            # Check for dominance: ind_i dominates ind_j if it's at least as good on all objectives
            # and strictly better on at least one.
            obj_i = np.array(ind_i.objectives)
            obj_j = np.array(ind_j.objectives)
            
            if np.all(obj_i <= obj_j) and np.any(obj_i < obj_j):
                strengths[i] += 1
    return strengths

def _calculate_raw_fitness(combined_pop: List[Individual], strengths: List[int]) -> List[float]:
    """
    Calculates the R(i) value (raw fitness) for each individual.
    Raw fitness is the sum of the strengths of an individual's dominators.
    """
    raw_fitness_values = [0.0] * len(combined_pop)
    for i, ind_i in enumerate(combined_pop):
        dominators_strength_sum = 0
        for j, ind_j in enumerate(combined_pop):
            if i == j:
                continue

            obj_i = np.array(ind_i.objectives)
            obj_j = np.array(ind_j.objectives)

            # ind_j dominates ind_i
            if np.all(obj_j <= obj_i) and np.any(obj_j < obj_i):
                dominators_strength_sum += strengths[j]
        
        raw_fitness_values[i] = dominators_strength_sum
    return raw_fitness_values

def _calculate_density(combined_pop: List[Individual]) -> List[float]:
    """
    Calculates the D(i) value (density) for each individual.
    Density is based on the k-th nearest neighbor distance.
    """
    num_individuals = len(combined_pop)
    k = int(math.sqrt(num_individuals))

    # Store distances to avoid recalculation
    distances = np.zeros((num_individuals, num_individuals))
    objectives = np.array([ind.objectives for ind in combined_pop])
    
    # Efficiently calculate all-pairs Euclidean distances
    for i in range(num_individuals):
        distances[i, :] = np.linalg.norm(objectives - objectives[i], axis=1)

    densities = []
    for i in range(num_individuals):
        # Sort distances to find the k-th nearest neighbor
        sorted_distances = np.sort(distances[i])
        
        # The k-th neighbor is at index k since the list includes the distance to self (0)
        kth_distance = sorted_distances[k]
        
        # Density D(i) = 1 / (sigma_k + 2)
        density = 1.0 / (kth_distance + 2.0)
        densities.append(density)
        
        # Store for potential use in archive truncation
        combined_pop[i].kth_distance = kth_distance
        
    return densities

def calculate_spea2_fitness(population: List[Individual], archive: List[Individual]):
    """
    Main function to calculate and assign SPEA2 fitness to individuals.

    This function orchestrates the SPEA2 fitness assignment process:
    1. Combines the current population and archive.
    2. Calculates strength (S-value) for each individual.
    3. Calculates raw fitness (R-value) based on dominator strengths.
    4. Calculates density (D-value) using a k-th nearest neighbor approach.
    5. Computes the final SPEA2 fitness as R + D and assigns it to each individual.
    """
    if not population and not archive:
        return

    combined_pop = population + archive
    
    strengths = _calculate_strength(combined_pop)
    raw_fitness_values = _calculate_raw_fitness(combined_pop, strengths)
    densities = _calculate_density(combined_pop)
    
    for i, individual in enumerate(combined_pop):
        individual.spea2_fitness = raw_fitness_values[i] + densities[i]
