import random

class Individual:
    def __init__(self, problem_instance):
        self.problem = problem_instance
        
        ## since the customers from the json problem_set are in arrays, 
        # we increment them by one. 0 is the depot
        customer_indicies = list(range(1, self.problem.num_customers + 1))
        ## we initialize them completely randomly to start
        random.shuffle(customer_indicies)
        self.chromosome = customer_indicies