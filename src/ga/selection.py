from __future__ import annotations

import random
from typing import List

from src.ga.individual import Individual


def tournament_selection(population: List[Individual]) -> Individual:
    """Binary tournament selection based on (pareto_rank, crowding_distance).

    - Lower pareto_rank is better (rank 1 is best)
    - If ranks equal, larger crowding_distance is better
    """
    if len(population) == 1:
        return population[0]

    i1, i2 = random.sample(range(len(population)), k=2)
    a = population[i1]
    b = population[i2]

    if a.pareto_rank < b.pareto_rank:
        return a
    if b.pareto_rank < a.pareto_rank:
        return b
    # ranks equal: compare crowding (higher is better)
    return a if a.crowding_distance >= b.crowding_distance else b


