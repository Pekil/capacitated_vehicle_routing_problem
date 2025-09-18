import os
from src.vrp.load_set import load_problem_instance
from src.vrp.problem import ProblemInstance
import glob

ProblemSet = list[ProblemInstance]
def load_CVRP() -> ProblemSet:
    print("--- Loading VRP Problem Instances from .txt files ---")
    data_dir = "data"
    txt_files = glob.glob(os.path.join(data_dir, "*.txt"))
    problem_instances = []

    if not txt_files:
        print("No .txt files found in the data directory.")
        return problem_instances

    for file_path in txt_files:
        try:
            problem_instance = load_problem_instance(file_path)
            problem_instances.append(problem_instance)
        except Exception as e:
            print(f"\nError processing file {os.path.basename(file_path)}: {e}")

    return problem_instances

def main():
    problem_instances: ProblemSet = load_CVRP()
    if problem_instances:
        print('Problem instances loaded successfully')

if __name__ == "__main__":
    main()