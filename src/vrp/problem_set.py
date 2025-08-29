import random
import json
import os
from typing import List

def generate_scenario(
    name,
    num_vehicle_range,
    num_customer_range,
    coord_range=(0,100),
    vehicle_capacity=100 ## a vehicle can store 100 "goods" 
):
    num_vehicles = random.randint(*num_vehicle_range)
    num_customers = random.randint(*num_customer_range)

    # this is fixed in the middle, the random locations of customers give enough variation
    depot = (50,50)

    ## this generates random positions for the customers within the bounds of the grid 0,100
    customers = []
    for i in range(num_customers):
        x = random.uniform(coord_range[0], coord_range[1])
        y = random.uniform(coord_range[0], coord_range[1])
        customers.append((x,y))
    c_demands = _randomize_customer_demands(num_vehicles, vehicle_capacity, num_customers)
    return {
        "name": name,
        "num_vehicles": num_vehicles,
        "num_customers": num_customers,
        "depot": depot,
        "customers": customers,
        "customer_demands": c_demands
    }
def _randomize_customer_demands(num_vehicles, vehicle_capacity, num_customers) -> List[int]:
    tot_fleet_cap = num_vehicles * vehicle_capacity
    c_demands = [5] * num_customers ## ensure each customer has atleast some demand as a baseline
    filled = False # checker
    tot_added = 5 * num_customers
    while not filled:
        for i in range(num_customers):
            addition: int = random.randint(1, 10) ## fill a small random amount for each pass of the array
            if tot_fleet_cap >= tot_added + addition:
                c_demands[i] += addition
                tot_added += addition
            else:
                filled = True
                break
    return c_demands
        

def generate_instances():
    
    ## i name the instances after their size category (s,m and l) and 1 or 2
    scenario_definitions = {
        's-1': {"num_vehicles_range": (2, 10), "num_customers_range": (10, 20)},
        's-2': {"num_vehicles_range": (2, 10), "num_customers_range": (10, 20)},
        'm-1': {"num_vehicles_range": (11, 25), "num_customers_range": (15, 30)},
        'm-2': {"num_vehicles_range": (11, 25), "num_customers_range": (15, 30)},
        'l-1': {"num_vehicles_range": (26, 50), "num_customers_range": (20, 50)},
        'l-2': {"num_vehicles_range": (26, 50), "num_customers_range": (20, 50)}
    }

    scenarios = {}
    ## loop the scenario definitions and load or create
    for name, params in scenario_definitions.items():
        file_path = "data/" + f"scenario-{name}.json"

        ## load the datasets if they already exist
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

