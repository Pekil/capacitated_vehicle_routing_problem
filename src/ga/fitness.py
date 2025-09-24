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
        individual.fitness = fitness_values
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

        # Prefix sums for O(1) demand queries over chromosome subsequences
        prefix_demand: List[int] = [0] * (n + 1)
        for idx in range(n):
            c_id = chromosome[idx]
            prefix_demand[idx + 1] = prefix_demand[idx] + self.problem.customer_demands[c_id - 1]

        # Dynamic programming with incremental route cost computation (O(n^2))
        for i in range(1, n + 1):
            # Maintain tail cost of route from chromosome[j]..chromosome[i-1] to depot as j moves backward
            # Base tail cost when subroute is just [i-1]: cost to return to depot
            current_tail_cost = self.problem.get_distance(chromosome[i - 1], 0)
            for j in range(i - 1, -1, -1):
                if j < i - 1:
                    # Add edge from chromosome[j] to next node chromosome[j+1]
                    current_tail_cost = (
                        self.problem.get_distance(chromosome[j], chromosome[j + 1])
                        + current_tail_cost
                    )

                # Demand for customers chromosome[j:i]
                route_demand = prefix_demand[i] - prefix_demand[j]

                # Route cost includes leaving depot to first customer
                route_cost = self.problem.get_distance(0, chromosome[j]) + current_tail_cost

                # Capacity penalty (proportional)
                if route_demand > self.problem.vehicle_capacity:
                    route_cost *= 10

                if C[j] + route_cost < C[i]:
                    C[i] = C[j] + route_cost
                    L[i] = max(L[j], route_cost)
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

        # Handle case where solution requires more vehicles than available
        if len(routes) > num_vehicles:
            # Apply penalty for using too many vehicles
            extra_vehicles = len(routes) - num_vehicles
            penalty = extra_vehicles * 10000  # Large penalty per extra vehicle
            return (best_distance + penalty, longest_route_dist + penalty), routes

        return (best_distance, longest_route_dist), routes