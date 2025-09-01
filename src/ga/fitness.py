from typing import List
import numpy as np

class FitnessEvaluator:
    def __init__(self, problem_instance):
        self.problem = problem_instance
    
    def evaluate(self, individual):
        chromosome = individual.chromosome
        num_vehicles = self.problem.num_vehicles

        best_distance, best_routes = self._optimal_split(chromosome, num_vehicles)

        return best_distance, best_routes
    

    ## this is the splitter function
    # we chose the optimal split, using "dynamic programming" to find the optimal way to split
    # this invovles finding the 'fittest' split before running he final fitness evaluation
    def _optimal_split(self, chromosome, num_vehicles):
        n: int = len(chromosome)                    # lets say n = 5
        C: List[float]= [float('inf')] * (n + 1)    # ['inf','inf','inf','inf','inf','inf']
        P: List[int] = [0] * (n + 1)                # [0,0,0,0,0,0]
        C[0] = 0                                    # [0,'inf','inf','inf','inf','inf']

        for i in range(1, n + 1): # check best for serving 1 up to and including n locatins
            for j in range(i):
                # extract sub route from indexes j to i
                sub_route = chromosome[j:i] 
                current_dist = 0
                last_node = 0
                route_demand = 0

                for c_id in sub_route:
                    # add customer demand from customer at given index
                    route_demand += self.problem.customer_demands[c_id - 1]
                    # increment distance from last node to given customer id
                    current_dist += self.problem.get_distance(last_node, c_id)
                    # update last node to given customer id
                    last_node = c_id 
                current_dist += self.problem.get_distance(last_node, 0) # add the distance back to depot

                # breaking vehicle constraints makes the solution invalid
                if route_demand > self.problem.vehicle_capacity:
                    current_dist = float('inf')
                
                # if cost of best route up to J + cost of this route is less than
                # the  
                if C[j] + current_dist < C[i]:
                    C[i] = C[j] + current_dist
                    P[i] = j 
        
        best_distance = C[n]
        
        # reconstruct the route that lead to the optimal cost using the predecessor List 
        routes = []
        end = n
        while end > 0:
            start = P[end]
            routes.append(chromosome[start:end])
            end = start
        
        routes.reverse()

        print(f"DEBUG: Splitter found {len(routes)} routes. vehicle limit is {num_vehicles}.")

        if len(routes) > num_vehicles:
            return float('inf'), []

        return best_distance, routes
