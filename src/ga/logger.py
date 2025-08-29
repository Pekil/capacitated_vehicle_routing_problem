import os
import csv
import numpy as np

class GenerationLogger:
    def __init__(self, scenario_name):
        base_dir = "data/generations"
        self.output_dir = os.path.join(base_dir, scenario_name)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.log_file_path = os.path.join(self.output_dir, "log.csv")

        with open(self.log_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'generation',
                'best_fitness',
                'average_fitness',
                'worst_fitness',
                'best_chromosome',
                'best_routes'
            ])
        
    def log_generation(self, generation_number, evaluated_population):
        if not evaluated_population:
            return
        
        evaluated_population.sort(key=lambda x: x["fitness"])
        
        best_solution = evaluated_population[0]
        worst_solution = evaluated_population[-1]

        fitness_values = [sol["fitness"] for sol in evaluated_population if sol["fitness"] != float('inf')]
        avg_fitness = np.mean(fitness_values) if fitness_values else float('inf')

        chromosome_str = "-".join(map(str, best_solution['individual'].chromosome))
        routes_str = ";".join(["-".join(map(str, route)) for route in best_solution['routes']])

        with open(self.log_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                generation_number,
                best_solution["fitness"],
                avg_fitness,
                worst_solution["fitness"],
                chromosome_str,
                routes_str
            ])

        print(f"Gen {generation_number}: Best Fitness = {best_solution['fitness']:.2f}, Avg Fitness = {avg_fitness:.2f}. Data logged to '{self.log_file_path}'.")