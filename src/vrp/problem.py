## this is the actual problem

import math

class ProblemInstance:
    def __init__(self, scenario_data):
        self.name = scenario_data["name"] 
        self.num_vehicles = scenario_data["num_vehicles"]
        self.depot = scenario_data["depot"]
        self.customers = scenario_data["customers"]
        self.num_customers = scenario_data["num_customers"]

        self.all_locations = [self.depot] + self.customers
        ## using a distance matrix because lookup is faster and 
        # computationally cheaper than calculating on the fly
        self.distance_matrix = self._calculate_distance_matrix()

    ## pythagorean theorem calculation of distance between two points
    def _calculate_euclidean_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    ## calculates the distance from all points to all points, including the depot.
    def _calculate_distance_matrix(self):
        num_locations = len(self.all_locations)
        matrix = [[0.0] * num_locations for _ in range(num_locations)]
        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:
                    matrix[i][j] = self._calculate_euclidean_distance(
                        self.all_locations[i], self.all_locations[j]
                    )
        return matrix
    
    ## get the distance between two points using the matrix indexes
    def get_distance(self, idx1, idx2):
        return self.distance_matrix[idx1][idx2]