import sys
import os

from src.vrp.problem_set import generate_instances
from src.vrp.problem import ProblemInstance
from src.ga.individual import Individual
from src.ga.fitness import FitnessEvaluator
from src.ga.logger import GenerationLogger
# Plotter is not used for now, so it can be commented out or removed
# from src.visualizer.plotter import Plotter

def main():
    print("Welcome to our solution to the Vehicle Routing Problem.")
    print("Creating instances if they do not exist already..")
    scenarios = generate_instances()
    
    population_size = 50
    
    for scenario_name, scenario_data in scenarios.items():
        print(f"\n===== Processing Scenario: {scenario_name} =====")
        
        problem = ProblemInstance(scenario_data)
        logger = GenerationLogger(scenario_name)
        evaluator = FitnessEvaluator(problem)
        
        print(f"--- Initializing Generation 0 with {population_size} individuals ---")
        population = [Individual(problem) for _ in range(population_size)]

        evaluated_population = []
        for individual in population:
            fitness, routes = evaluator.evaluate(individual)
            evaluated_population.append({
                "individual": individual,
                "fitness": fitness,
                "routes": routes
            })

        logger.log_generation(0, evaluated_population)
        
        # Here is where you would put your loop for subsequent generations (e.g., for gen in range(1, 500): ...)
        # Inside the loop, you would perform selection, crossover, mutation,
        # then re-evaluate the new population and call logger.log_generation(gen, new_evaluated_pop)

    print("\nAll scenarios have been processed for Generation 0.")

if __name__ == "__main__":
    main()