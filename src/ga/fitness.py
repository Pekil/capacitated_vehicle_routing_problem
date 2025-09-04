from typing import List
from src.ga.individual import Individual
import numpy as np

class FitnessEvaluator:
    def __init__(self, problem_instance):
        self.problem = problem_instance
    
    def evaluate(self, individual):
        chromosome = individual.chromosome
        num_vehicles = self.problem.num_vehicles

        best_distance, best_routes = self._optimal_split(chromosome, num_vehicles)

        return best_distance, best_routes
    
    def _optimal_split(self, chromosome, num_vehicles):
        n: int = len(chromosome)
        C: List[float]= [float('inf')] * (n + 1)
        P: List[int] = [0] * (n + 1)
        C[0] = 0

        for i in range(1, n + 1):
            for j in range(i):
                sub_route = chromosome[j:i] 
                current_dist = 0
                last_node = 0
                route_demand = 0

                for c_id in sub_route:
                    route_demand += self.problem.customer_demands[c_id - 1]
                    current_dist += self.problem.get_distance(last_node, c_id)
                    last_node = c_id 
                current_dist += self.problem.get_distance(last_node, 0)

                if route_demand > self.problem.vehicle_capacity:
                    current_dist = float('inf')
                
                if C[j] + current_dist < C[i]:
                    C[i] = C[j] + current_dist
                    P[i] = j 
        
        best_distance = C[n]
        
        routes = []
        end = n
        while end > 0:
            start = P[end]
            routes.append(chromosome[start:end])
            end = start
        
        routes.reverse()

        # <-- FIX: REMOVED DEBUG PRINT STATEMENT
        if len(routes) > num_vehicles:
            return float('inf'), []

        return best_distance, routes