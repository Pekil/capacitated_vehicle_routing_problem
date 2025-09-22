import os
import csv
import json
from typing import List, Dict, Any

from src.vrp.problem import ProblemInstance
from src.ga.individual import Individual


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def log_run_results(
    output_base_dir: str,
    problem: ProblemInstance,
    params: Dict[str, Any],
    run_id: int,
    runtime: float,
    evaluations: int,
    final_front: List[Individual]
) -> None:
    """Persist results of a NSGA-II run in a structured directory.

    Directory layout:
      {output_base_dir}/{problem.name}/{params['name']}/run_{run_id}/
        - summary.json
        - final_pareto_front.csv
    """
    run_dir = os.path.join(output_base_dir, problem.name, params.get('name', 'default'), f"run_{run_id}")
    _ensure_dir(run_dir)

    # summary.json
    summary = {
        "problem_name": problem.name,
        "parameter_set_name": params.get('name', 'default'),
        "run_id": run_id,
        "wall_clock_time_sec": runtime,
        "total_evaluations": evaluations,
        "num_vehicles": problem.num_vehicles,
        "num_customers": problem.num_customers,
        "vehicle_capacity": problem.vehicle_capacity,
    }
    with open(os.path.join(run_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    # final_pareto_front.csv
    with open(os.path.join(run_dir, 'final_pareto_front.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["total_distance", "max_route_length", "chromosome", "routes"]) 
        for ind in final_front:
            td, mr = ind.objectives
            chromosome_str = "-".join(map(str, ind.chromosome))
            routes_str = ";".join(["-".join(map(str, r)) for r in ind.routes])
            writer.writerow([td, mr, chromosome_str, routes_str])