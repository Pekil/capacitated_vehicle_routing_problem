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


def calculate_crowding_distance(front: List[Individual]) -> None:
    """Compute crowding distance for a single front in-place.

    - Sets individual.crowding_distance.
    - Boundary solutions for each objective receive infinite distance.
    """
    n = len(front)
    if n == 0:
        return
    if n == 1:
        front[0].crowding_distance = float('inf')
        return

    # Initialize
    for ind in front:
        ind.crowding_distance = 0.0

    num_objectives = 2  # total_distance, longest_route
    for m in range(num_objectives):
        # Sort by objective m
        front.sort(key=lambda ind: ind.objectives[m])
        min_val = front[0].objectives[m]
        max_val = front[-1].objectives[m]

        # Assign infinite distance to boundary points
        front[0].crowding_distance = float('inf')
        front[-1].crowding_distance = float('inf')

        if max_val == min_val:
            # All points identical on this objective; skip distance accumulation
            continue

        for i in range(1, n - 1):
            prev_val = front[i - 1].objectives[m]
            next_val = front[i + 1].objectives[m]
            front[i].crowding_distance += (next_val - prev_val) / (max_val - min_val)


