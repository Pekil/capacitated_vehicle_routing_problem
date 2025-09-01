import math

class ProblemInstance:
    def __init__(self, scenario_data):
        self.name = scenario_data["name"] 
        self.num_vehicles = scenario_data["num_vehicles"]
        self.depot = scenario_data["depot"]
        self.customers = scenario_data["customers"]
        self.customer_demands = scenario_data["customer_demands"]
        self.num_customers = scenario_data["num_customers"]
        self.vehicle_capacity = scenario_data["vehicle_capacity"]
        self.toughness = scenario_data["fleet_utilization"]
        # The 'packing_index' line has been removed.

        self.all_locations = [self.depot] + self.customers
        self.distance_matrix = self._calculate_distance_matrix()

    def _calculate_euclidean_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

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
    
    def get_distance(self, idx1, idx2):
        return self.distance_matrix[idx1][idx2]