import random

# Represents a possible solution (a route order)
class Individual:
    def __init__(self, problem_instance, chromosome=None):
        self.problem = problem_instance
        if chromosome is not None:
            # Used when loading a specific chromosome (route order)
            self.chromosome = chromosome
        else:
            # Make a random route (customers are 1-indexed, 0 is depot)
            customer_indicies = list(range(1, self.problem.num_customers + 1))
            random.shuffle(customer_indicies)
            self.chromosome = customer_indicies

        # Multi-objective attributes (minimize both)
        # Store as a mutable list so they can be updated in-place
        # objectives[0] = total_distance, objectives[1] = longest_route_distance
        self.objectives = [float('inf'), float('inf')]
        # Routes produced by the split evaluation for this chromosome
        self.routes = []
        # NSGA-II metadata
        self.pareto_rank = -1
        self.crowding_distance = 0.0
        # SPEA2 metadata
        self.spea2_fitness = float('inf')
        self.kth_distance = float('inf')

    def set_evaluation(self, fitness_values, routes):
        # fitness_values is a tuple[float, float] from FitnessEvaluator
        self.objectives[0] = fitness_values[0]
        self.objectives[1] = fitness_values[1]
        self.routes = routes

