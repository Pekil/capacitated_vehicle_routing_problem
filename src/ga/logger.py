import os
import csv
import json
import numpy as np

class GenerationLogger:
    def __init__(self, problem_instance):
        base_dir = "data/generations"
        self.output_dir = os.path.join(base_dir, problem_instance.name)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self._write_metadata(problem_instance)
        
        self.log_file_path = os.path.join(self.output_dir, 'log.csv')
        
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

    def _write_metadata(self, problem_instance):
        metadata_path = os.path.join(self.output_dir, 'metadata.json')
        metadata = {
            "scenario_name": problem_instance.name,
            "num_vehicles": problem_instance.num_vehicles,
            "num_customers": problem_instance.num_customers,
            "vehicle_capacity": problem_instance.vehicle_capacity,
            "toughness": problem_instance.toughness
            # The 'packing_index' line has been removed.
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    def log_generation(self, generation_number, evaluated_population):
        if not evaluated_population:
            return

        evaluated_population.sort(key=lambda x: x["fitness"])

        best_solution = evaluated_population[0]
        worst_solution = evaluated_population[-1]
        
        fitness_values = [sol["fitness"] for sol in evaluated_population if sol["fitness"] != float('inf')]
        avg_fitness = np.mean(fitness_values) if fitness_values else float('inf')

        chromosome_str = "-".join(map(str, best_solution['individual'].chromosome))

        with open(self.log_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                generation_number,
                best_solution['fitness'],
                avg_fitness,
                worst_solution['fitness'],
                chromosome_str
            ])
        
        if generation_number == 0:
            gen_0_path = os.path.join(self.output_dir, 'gen_0.csv')
            with open(gen_0_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'chromosome',
                    'fitness'
                ])

                for sol in evaluated_population:
                    chromosome_str = "-".join(map(str, sol['individual'].chromosome))
                    routes_str = ';'.join(["-".join(map(str, route)) for route in sol['routes']])
                    writer.writerow([
                        chromosome_str,
                        sol['fitness']
                    ])