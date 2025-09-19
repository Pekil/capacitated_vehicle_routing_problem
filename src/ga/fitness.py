from typing import List
from src.ga.individual import Individual
import numpy as np

# This class figures out how good a solution is (lower distance is better)
FitnessSet = tuple[float, float]
class FitnessEvaluator:
    def __init__(self, problem_instance):
        self.problem = problem_instance

    def evaluate(self, individual):
        # Figure out the best way to split the route for the available vehicles
        chromosome = individual.chromosome
        num_vehicles = self.problem.num_vehicles
        fitness_values, best_routes = self._optimal_split(chromosome, num_vehicles)
        return fitness_values, best_routes

    def _optimal_split(self, chromosome, num_vehicles) -> tuple[FitnessSet, list[list[int]]]:
        # Implements the Split algorithm using dynamic programming to find the optimal
        # way to partition a single giant tour (chromosome) into a set of feasible
        # vehicle routes with the minimum total distance.
        n: int = len(chromosome)
        C: List[float]= [float('inf')] * (n + 1)
        L: List[float]= [0.0] * (n + 1) # Tracks the longest route distance
        P: List[int] = [0] * (n + 1)
        C[0] = 0

        for i in range(1, n + 1):
            for j in range(i):
                sub_route = chromosome[j:i]
                current_dist = 0
                last_node = 0
                route_demand = 0
                # Calculate distance and demand for this sub-route
                for c_id in sub_route:
                    route_demand += self.problem.customer_demands[c_id - 1]
                    current_dist += self.problem.get_distance(last_node, c_id)
                    last_node = c_id
                current_dist += self.problem.get_distance(last_node, 0)

                if route_demand > self.problem.vehicle_capacity:
                    current_dist = float('inf')

                if C[j] + current_dist < C[i]:
                    C[i] = C[j] + current_dist
                    L[i] = max(L[j], current_dist)
                    P[i] = j

        best_distance = C[n]
        longest_route_dist = L[n]
        routes = []
        end = n
        while end > 0:
            start = P[end]
            routes.append(chromosome[start:end])
            end = start
        
        routes.reverse()

        if len(routes) > num_vehicles:
            return (float('inf'), float('inf')), []

        return (best_distance, longest_route_dist), routes