import matplotlib.pyplot as plt
import numpy as np

## This is a class to visualize the solutions on a grid
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

    def draw_locations(self, problem_instance):
        depot = problem_instance.depot
        customers = problem_instance.customers
        demands = problem_instance.customer_demands

        d_x, d_y = depot
        self.ax.scatter(d_x, d_y, c='red', marker='s', label='Depot', s=100)

        if customers:
            customer_x, customer_y = zip(*customers)
            sizes = [20 + demand * 2 for demand in demands]
            self.ax.scatter(customer_x, customer_y, c='cyan', marker='o', label = 'Customers', s=sizes)
        
        ## set the zoom boundaries to just outside the boundaries of the points
        self.ax.set_xlim(-10,110)
        self.ax.set_ylim(-10,110)
        
        self.ax.grid(True, linestyle='--', alpha=0.3)
    
    def draw_routes(self, problem_instance, routes):
        if not routes:
            return
        
        cmap = plt.get_cmap('gist_rainbow', len(routes)) # get a color map
        colors = [cmap(i) for i in range(len(routes))] # map colors to each route
        
        for i, route in enumerate(routes):
            if not route:
                continue

            color = colors[i]
            full_path_indicies = [0] + route + [0] # add from and to depot

            path_coords = [problem_instance.all_locations[idx] for idx in full_path_indicies]
            path_x, path_y = zip(*path_coords)

            self.ax.plot(path_x, path_y, color=color, marker='o', markersize=4, label=f'Vehicle {i+1}') 

    def show(self):
        self.ax.legend()
        plt.show()