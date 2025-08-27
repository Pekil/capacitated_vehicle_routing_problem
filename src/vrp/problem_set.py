import random
import json
import os

def generate_scenario(
    name,
    num_vehicle_range,
    num_customer_range,
    coord_range=(0,100)
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
    
    return {
        "name": name,
        "num_vehicles": num_vehicles,
        "num_customers": num_customers,
        "depot": depot,
        "customers": customers
    }

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

