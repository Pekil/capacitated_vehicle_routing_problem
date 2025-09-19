import re
from src.vrp.problem import ProblemInstance

def load_problem_instance(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    name_match = re.search(r"NAME\s*:\s*(.*)", content)
    if not name_match:
        raise ValueError("Could not parse NAME from file.")
    name = name_match.group(1).strip()

    num_vehicles_match = re.search(r"k(\d+)", name)
    if not num_vehicles_match:
        raise ValueError("Could not parse number of vehicles from NAME.")
    num_vehicles = int(num_vehicles_match.group(1))

    capacity_match = re.search(r"CAPACITY\s*:\s*(\d+)", content)
    if not capacity_match:
        raise ValueError("Could not parse CAPACITY from file.")
    capacity = int(capacity_match.group(1))
    
    node_coord_match = re.search(r"NODE_COORD_SECTION\s*\n([\s\S]*?)\n\s*DEMAND_SECTION", content)
    if not node_coord_match:
        raise ValueError("Could not find NODE_COORD_SECTION.")
    node_coord_section = node_coord_match.group(1)

    demand_match = re.search(r"DEMAND_SECTION\s*\n([\s\S]*?)\n\s*DEPOT_SECTION", content)
    if not demand_match:
        raise ValueError("Could not find DEMAND_SECTION.")
    demand_section = demand_match.group(1)

    locations = {}
    for line in node_coord_section.strip().split('\n'):
        parts = line.strip().split()
        node_id = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        locations[node_id] = (x, y)

    demands = {}
    for line in demand_section.strip().split('\n'):
        parts = line.strip().split()
        node_id = int(parts[0])
        demand = int(parts[1])
        demands[node_id] = demand

    depot_id = 1 # based on file format
    depot_coords = locations[depot_id]
    
    customers = []
    customer_demands = []
    customer_ids = sorted([key for key in locations.keys() if key != depot_id])

    for c_id in customer_ids:
        customers.append(locations[c_id])
        customer_demands.append(demands[c_id])

    scenario_data = {
        "name": name,
        "num_vehicles": num_vehicles,
        "depot": depot_coords,
        "customers": customers,
        "customer_demands": customer_demands,
        "num_customers": len(customers),
        "vehicle_capacity": capacity,
        "fleet_utilization": sum(customer_demands) / (num_vehicles * capacity)
    }

    return ProblemInstance(scenario_data)
