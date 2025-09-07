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
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    # THIS IS THE MAIN LOGGER FOR THE SIMULATION RUN
    def log_generation(self, generation_number, all_fitness_values, best_fitness, best_routes):
        if not all_fitness_values:
            return

        valid_fitness_values = [f for f in all_fitness_values if f != float('inf')]
        avg_fitness = np.mean(valid_fitness_values) if valid_fitness_values else float('inf')
        worst_fitness = max(all_fitness_values)

        routes_str = ';'.join(["-".join(map(str, route)) for route in best_routes])

        with open(self.log_file_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                generation_number,
                best_fitness,
                avg_fitness,
                worst_fitness,
                routes_str
            ])

    # <-- FIX: NEW DEDICATED METHOD FOR handle_init
    # This method handles the specific data structure created during initialization
    def log_initial_population(self, evaluated_population):
        # First, log the summary for Generation 0 to the main log file
        if not evaluated_population:
            return
            
        evaluated_population.sort(key=lambda x: x["fitness"])
        best_solution = evaluated_population[0]
        
        all_fitness_values = [sol["fitness"] for sol in evaluated_population]
        
        self.log_generation(0, all_fitness_values, best_solution['fitness'], best_solution['routes'])
        
        # Second, write the detailed gen_0.csv file for loading
        gen_0_path = os.path.join(self.output_dir, 'gen_0.csv')
        with open(gen_0_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'chromosome',
                'fitness'
            ])

            for sol in evaluated_population:
                chromosome_str = "-".join(map(str, sol['individual'].chromosome))
                writer.writerow([
                    chromosome_str,
                    sol['fitness']
                ])