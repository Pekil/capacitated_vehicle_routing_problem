import random
import json
import os
from typing import List


scenario_definitions = {
    's-1': {"num_vehicles_range": (2, 10), "num_customers_range": (10, 20)},
    's-2': {"num_vehicles_range": (2, 10), "num_customers_range": (10, 20)},
    'm-1': {"num_vehicles_range": (11, 25), "num_customers_range": (15, 30)},
    'm-2': {"num_vehicles_range": (11, 25), "num_customers_range": (15, 30)},
    'l-1': {"num_vehicles_range": (26, 50), "num_customers_range": (20, 50)},
    'l-2': {"num_vehicles_range": (26, 50), "num_customers_range": (20, 50)}
}

def generate_scenario(
    name,
    num_vehicle_range,
    num_customer_range,
    coord_range=(0,100),
    vehicle_capacity=100
):
    num_vehicles = random.randint(*num_vehicle_range)
    num_customers = random.randint(*num_customer_range)
    depot = (50,50)

    customers = []
    for i in range(num_customers):
        x = random.uniform(coord_range[0], coord_range[1])
        y = random.uniform(coord_range[0], coord_range[1])
        customers.append((x,y))

    c_demands, fleet_utilization = _randomize_customer_demands(
        num_vehicles,
        vehicle_capacity,
        num_customers
    )

    return {
        "name": name,
        "num_vehicles": num_vehicles,
        "num_customers": num_customers,
        "depot": depot,
        "customers": customers,
        "customer_demands": c_demands,
        "vehicle_capacity": vehicle_capacity,
        "fleet_utilization": fleet_utilization,
    }

def _randomize_customer_demands(num_vehicles, vehicle_capacity, num_customers):
    lower_demand_bound = 10
    
    avg_stops_per_vehicle = num_customers / num_vehicles

    if avg_stops_per_vehicle <= 1:
        # Unconstrained: more vehicles than customers. Allow high demands.
        upper_demand_bound = vehicle_capacity - 10
    else:
        # Constrained: Calculate the theoretical max demand based on the ratio.
        theoretical_bound = vehicle_capacity / avg_stops_per_vehicle
        
        # Ensure the upper bound is at least the lower bound.
        upper_demand_bound = max(lower_demand_bound, theoretical_bound)
        # Also ensure it doesn't exceed the absolute max capacity.
        upper_demand_bound = min(vehicle_capacity - 1, upper_demand_bound)

    # "ONE PASS" generation to ensure high variance.
    c_demands = [random.randint(lower_demand_bound, int(upper_demand_bound)) for _ in range(num_customers)]

    # Calculate final toughness/utilization as an output metric.
    total_demand = sum(c_demands)
    total_fleet_capacity = num_vehicles * vehicle_capacity
    actual_utilization = total_demand / total_fleet_capacity if total_fleet_capacity > 0 else 0

    return c_demands, actual_utilization

def generate_instances():
    
    scenarios = {}
    for name, params in scenario_definitions.items():
        file_path = "data/" + f"scenario-{name}.json"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                scenarios[name] = json.load(f)
        else:
            print(f"Generating new scenario '{name}'...")
            new_scenario = generate_scenario(
                name,
                params["num_vehicles_range"],
                params["num_customers_range"]
            )
            with open(file_path, "w") as f:
                json.dump(new_scenario, f, indent=4)
            scenarios[name] = new_scenario
    return scenarios

