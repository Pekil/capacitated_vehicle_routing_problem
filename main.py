import sys
import os

from src.vrp.problem_set import generate_instances
from src.vrp.problem import ProblemInstance
from src.ga.individual import Individual
from src.visualizer.plotter import Plotter

def main():
    print("Welcome to our solution to the Vehicle Routing Problem.")
    print("Creating instances if they do not exist already..")
    scenarios = generate_instances()
    
    problem_name = 'm-1'
    print(f"\nVisualizing scenario: {problem_name}")

    problem = ProblemInstance(scenarios[problem_name])

    print("\nCreating a single random solution...")
    first_solution = Individual(problem)

    scenario_data = scenarios[problem_name]

    plotter = Plotter(title=f"VRP Scenario: {problem.name}")
    plotter.draw_locations(problem.depot, problem.customers)
    plotter.show()

if __name__ == "__main__":
    main()
    
