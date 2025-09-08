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