import random
from src.ga.individual import Individual

def pmx_crossover(
    p1: Individual,
    p2: Individual,
    Pc: float
) -> tuple[Individual, Individual]:

    chr1 = p1.chromosome[:]
    chr2 = p2.chromosome[:]
    size = len(chr1)

    o1_chr = [0] * size
    o2_chr = [0] * size

    if random.random() > Pc:
        return Individual(p1.problem, chr1), Individual(p2.problem, chr2)

    cx_p1, cx_p2 = sorted(random.sample(range(size), 2))
    
    # <-- FIX: ADDED THE MISSING DIRECT COPY STEP
    o1_chr[cx_p1:cx_p2] = chr1[cx_p1:cx_p2]
    o2_chr[cx_p1:cx_p2] = chr2[cx_p1:cx_p2]
    
    mapping1 = {chr1[i]: chr2[i] for i in range(cx_p1, cx_p2)}
    mapping2 = {chr2[i]: chr1[i] for i in range(cx_p1, cx_p2)}

    for i in list(range(cx_p1)) + list(range(cx_p2, size)):
        # For offspring 1
        val_from_p2 = chr2[i]
        while val_from_p2 in mapping1:
            val_from_p2 = mapping1[val_from_p2]
        o1_chr[i] = val_from_p2

        # For offspring 2
        val_from_p1 = chr1[i]
        while val_from_p1 in mapping2:
            val_from_p1 = mapping2[val_from_p1]
        o2_chr[i] = val_from_p1
    
    return Individual(p1.problem, o1_chr), Individual(p2.problem, o2_chr)

def swap_mutation(indiv: Individual, Pm: float):
    if random.random() < Pm:
        chr = indiv.chromosome
        idx1, idx2 = random.sample(range(len(chr)),2)
        chr[idx1], chr[idx2] = chr[idx2], chr[idx1]