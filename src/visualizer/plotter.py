import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Plots the VRP scenario and routes
class Plotter:
    def __init__(self, title="VRP Visualizer"):
        self.fig, self.ax = plt.subplots()
        self.ax.set_facecolor('black')
        self.ax.set_title(title, color='white')
        self.ax.set_xlabel('X Coordinate')
        self.ax.set_ylabel('Y Coordinate')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('white')
        self.route_lines = []

    def draw_locations(self, problem_instance):
        # Draw depot and customers
        depot = problem_instance.depot
        customers = problem_instance.customers
        demands = problem_instance.customer_demands
        d_x, d_y = depot
        self.ax.scatter(d_x, d_y, c='red', marker='s', label='Depot', s=100)
        if customers:
            customer_x, customer_y = zip(*customers)
            sizes = [20 + demand * 2 for demand in demands]
            self.ax.scatter(customer_x, customer_y, c='cyan', marker='o', label = 'Customers', s=sizes)
        self.ax.set_xlim(-10, 110)
        self.ax.set_ylim(-10, 110)
        self.ax.grid(True, linestyle='--', alpha=0.3)

    def draw_routes(self, problem_instance, routes):
        # Draw each vehicle's route
        if not routes:
            return
        cmap = plt.get_cmap('gist_rainbow', len(routes))
        colors = [cmap(i) for i in range(len(routes))]
        for i, route in enumerate(routes):
            if not route:
                continue
            color = colors[i]
            full_path_indicies = [0] + route + [0]
            path_coords = [problem_instance.all_locations[idx] for idx in full_path_indicies]
            path_x, path_y = zip(*path_coords)
            self.ax.plot(path_x, path_y, color=color, marker='o', markersize=4, label=f'Vehicle {i+1}')
        self.ax.legend()


    def show(self):
        plt.show()

    # <-- MODIFIED: Method now accepts a 'speed' parameter with a default
    def animate_evolution(self, problem_instance, evolution_data, speed=10):
        self.draw_locations(problem_instance)
        
        gen_text = self.ax.text(0.02, 0.95, '', transform=self.ax.transAxes, color='yellow', fontsize=14, fontweight='bold')

        def _update_frame(frame_num):
            for line in self.route_lines:
                line.remove()
            self.route_lines.clear()

            legend = self.ax.get_legend()
            if legend:
                legend.remove()

            gen_data = evolution_data[frame_num]
            generation = gen_data['generation']
            fitness = gen_data['best_fitness']
            routes = gen_data['best_routes']
            
            self.ax.set_title(
                f"Evolution of VRP Solution (Best Fitness: {fitness:.2f})",
                color='white'
            )
            gen_text.set_text(f'Generation: {generation}')

            if routes:
                num_routes = len(routes)
                cmap = plt.get_cmap('gist_rainbow', max(1, num_routes))
                colors = [cmap(i) for i in range(num_routes)]

                for i, route in enumerate(routes):
                    if not route:
                        continue
                    
                    full_path_indices = [0] + route + [0]
                    path_coords = [problem_instance.all_locations[idx] for idx in full_path_indices]
                    path_x, path_y = zip(*path_coords)
                    
                    line, = self.ax.plot(path_x, path_y, color=colors[i], marker='o', markersize=4, label=f'Vehicle {i+1}')
                    self.route_lines.append(line)
            
            self.ax.legend(loc='upper right')
            
            return tuple(self.route_lines) + (gen_text,)

        # <-- MODIFIED: Calculate the frame interval from the speed
        # Ensure speed is not zero to avoid division error
        if speed <= 0:
            speed = 1
        interval_ms = 1000 / speed

        ani = animation.FuncAnimation(
            self.fig, 
            _update_frame, 
            frames=len(evolution_data), 
            interval=interval_ms, # Use the calculated interval
            blit=False,
            repeat=False
        )
        
        self.show()