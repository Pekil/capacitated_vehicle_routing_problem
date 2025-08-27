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

    def draw_locations(self, depot, customers):
        d_x, d_y = depot
        self.ax.scatter(d_x, d_y, c='red', marker='s', label='Depot', s=100)

        if customers:
            customer_x, customer_y = zip(*customers)
            self.ax.scatter(customer_x, customer_y, c='cyan', marker='o', label = 'Customers')
        
        ## set the zoom boundaries to just outside the boundaries of the points
        self.ax.set_xlim(-10,110)
        self.ax.set_ylim(-10,110)
        
        self.ax.legend()
        self.ax.grid(True, linestyle='--', alpha=0.3)

    def show(self):
        plt.show()