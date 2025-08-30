import random
import json
import os
from typing import List

# Updated to be a module-level constant
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
    # ... (rest of the function is unchanged)
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

    packing_index = _calculate_packing_index(c_demands, num_vehicles, vehicle_capacity)

    return {
        "name": name,
        "num_vehicles": num_vehicles,
        "num_customers": num_customers,
        "depot": depot,
        "customers": customers,
        "customer_demands": c_demands,
        "vehicle_capacity": vehicle_capacity,
        "fleet_utilization": fleet_utilization,
        "packing_index": packing_index
    }

# ... (_randomize_customer_demands, _calculate_packing_index are unchanged)
def _calculate_packing_index(customer_demands, num_vehicles, vehicle_capacity):
    num_customers = len(customer_demands)
    if num_vehicles == 0 or num_customers == 0:
        return 0.0
    avg_stops_per_vehicle = num_customers / num_vehicles
    ideal_demand_per_customer = (vehicle_capacity * 0.9) / avg_stops_per_vehicle
    total_deviation = sum(abs(demand - ideal_demand_per_customer) for demand in customer_demands)
    packing_index = total_deviation / num_customers
    return packing_index

def _randomize_customer_demands(num_vehicles, vehicle_capacity, num_customers):
    tot_fleet_cap = num_vehicles * vehicle_capacity
    target_utilization = random.uniform(0.70, 0.90)
    target_demand = tot_fleet_cap * target_utilization
    c_demands = [5] * num_customers
    tot_added = 5 * num_customers
    filled = False
    while not filled:
        high_demand_customers = sum(1 for d in c_demands if d > vehicle_capacity / 2)
        if high_demand_customers > num_vehicles:
            break
        for i in range(num_customers):
            addition: int = random.randint(1, 25)
            if vehicle_capacity < c_demands[i] + addition: continue
            if tot_fleet_cap*0.9 < tot_added + addition: continue
            tot_added += addition
            c_demands[i] += addition
            if target_demand < tot_added:
                filled = True
                break
    actual_utilization = tot_added / tot_fleet_cap
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