from __future__ import annotations

from typing import List

from src.ga.individual import Individual


def fast_non_dominated_sort(population: List[Individual]) -> List[List[Individual]]:
    """Assign Pareto ranks to the population and return the list of fronts.

    - Uses the standard fast non-dominated sorting from NSGA-II.
    - Modifies individuals in-place: sets individual.pareto_rank (1-based).
    - Returns a list of fronts, where each front is a list of Individuals.
    """
    if not population:
        return []

    # Initialize dominance structures
    domination_sets: List[set[int]] = [set() for _ in range(len(population))]
    domination_counts: List[int] = [0 for _ in range(len(population))]
    fronts: List[List[int]] = [[]]

    def dominates(p: Individual, q: Individual) -> bool:
        p0, p1 = p.objectives
        q0, q1 = q.objectives
        return (p0 <= q0 and p1 <= q1) and (p0 < q0 or p1 < q1)

    # Compute domination relationships
    for i, p in enumerate(population):
        for j, q in enumerate(population):
            if i == j:
                continue
            if dominates(p, q):
                domination_sets[i].add(j)
            elif dominates(q, p):
                domination_counts[i] += 1
        if domination_counts[i] == 0:
            fronts[0].append(i)

    # Build subsequent fronts
    current = 0
    while current < len(fronts) and fronts[current]:
        next_front: List[int] = []
        for i in fronts[current]:
            for j in domination_sets[i]:
                domination_counts[j] -= 1
                if domination_counts[j] == 0:
                    next_front.append(j)
        current += 1
        if next_front:
            fronts.append(next_front)

    # Set 1-based pareto ranks on individuals and return fronts as Individuals
    fronts_as_inds: List[List[Individual]] = []
    for rank, front in enumerate(fronts, start=1):
        inds: List[Individual] = []
        for idx in front:
            population[idx].pareto_rank = rank
            inds.append(population[idx])
        if inds:
            fronts_as_inds.append(inds)

    return fronts_as_inds


def calculate_crowding_distance(front: list[Individual]) -> None:
    """Compute crowding distance for a single front in-place.

    - Sets individual.crowding_distance.
    - Boundary solutions for each objective receive infinite distance.
    """
    n = len(front)
    if n <= 2:
        # For fronts with 0, 1, or 2 solutions, all get infinite distance
        for ind in front:
            ind.crowding_distance = float('inf')
        return

    # Initialize all distances to zero
    for ind in front:
        ind.crowding_distance = 0.0

    num_objectives = 2  # total_distance, longest_route

    # --- STAGE 1: Calculate and sum the distances for interior points ---
    # This must be done for all objectives before assigning infinite distance
    # to boundaries to prevent summed distances from being overwritten.
    for m in range(num_objectives):
        # Sort by the current objective to find neighbors
        front.sort(key=lambda ind: ind.objectives[m])
        min_val = front[0].objectives[m]
        max_val = front[-1].objectives[m]

        # Avoid division by zero if all values are the same
        if max_val == min_val:
            continue

        # Add the normalized distance for all interior points
        for i in range(1, n - 1):
            prev_val = front[i - 1].objectives[m]
            next_val = front[i + 1].objectives[m]
            front[i].crowding_distance += (next_val - prev_val) / (max_val - min_val)

    # --- STAGE 2: Assign infinite distance to all boundary points ---
    # An individual gets infinite distance if it's a boundary for *any* objective.
    for m in range(num_objectives):
        # Sort again to be sure we identify the correct boundaries
        front.sort(key=lambda ind: ind.objectives[m])
        front[0].crowding_distance = float('inf')
        front[-1].crowding_distance = float('inf')


