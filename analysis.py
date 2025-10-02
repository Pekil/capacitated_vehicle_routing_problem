import json
import csv
import glob
import os
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
from pymoo.indicators.hv import HV
from pymoo.indicators.spacing import SpacingIndicator # <-- 1. IMPORT SPACING
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

PROBLEM_NAMES = [
    "A-n33-k6", "A-n34-k5", "B-n35-k5", "B-n38-k6",
    "X-n101-k25", "X-n110-k13"
]
PARAMETER_SETS = ["Baseline", "Deep Search", "High Exploration"]
ALGORITHMS = ["NSGA-II", "SPEA2"]
RESULTS_DIR = "results"
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_summary_data(algorithm: str, problem: str, param_set: str) -> List[Dict]:
    """Load all summary.json files for a given scenario."""
    pattern = os.path.join(RESULTS_DIR, algorithm, problem, param_set, "run_*", "summary.json")
    summaries = []
    for file_path in glob.glob(pattern):
        try:
            with open(file_path, 'r') as f:
                summaries.append(json.load(f))
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    return summaries

def load_pareto_fronts(algorithm: str, problem: str, param_set: str) -> List[List[Dict]]:
    """Load all final_pareto_front.csv files for a given scenario."""
    pattern = os.path.join(RESULTS_DIR, algorithm, problem, param_set, "run_*", "final_pareto_front.csv")
    fronts = []
    for file_path in glob.glob(pattern):
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                front = [{'total_distance': float(row['total_distance']), 'max_route_length': float(row['max_route_length'])} for row in reader]
                if front:
                    fronts.append(front)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    return fronts

def fronts_to_array(fronts: List[List[Dict]]) -> List[np.ndarray]:
    """Convert list of fronts to list of numpy arrays."""
    return [np.array([[sol['total_distance'], sol['max_route_length']] for sol in front]) for front in fronts if front]

# ============================================================================
# STATISTICAL AND PLOTTING HELPER FUNCTIONS
# ============================================================================

def find_non_dominated_front(points: np.ndarray) -> np.ndarray:
    """Finds the non-dominated front from a given set of points."""
    if points.size == 0:
        return np.array([])
    unique_points = np.unique(points, axis=0)
    is_dominated = np.zeros(len(unique_points), dtype=bool)
    for i, p1 in enumerate(unique_points):
        dominating_mask = np.all(unique_points <= p1, axis=1) & np.any(unique_points < p1, axis=1)
        if np.any(dominating_mask):
            is_dominated[i] = True
    non_dominated_points = unique_points[~is_dominated]
    return non_dominated_points[non_dominated_points[:, 0].argsort()]

def create_summary_csv(all_results: List[Dict]):
    """Create a CSV file containing summary statistics for all analyzed scenarios."""
    # --- 2. ADD SPACING TO THE CSV HEADERS ---
    headers = ["Problem", "Parameters", "Algorithm", "Mean Runtime (s)", "Std Dev Runtime (s)", "Mean Hypervolume", "Std Dev Hypervolume", "Mean Spacing", "Std Dev Spacing"]
    df = pd.DataFrame(all_results, columns=headers)
    df.sort_values(by=["Problem", "Parameters", "Algorithm"], inplace=True)
    output_filename = "analysis_summary.csv"
    df.to_csv(output_filename, index=False, float_format="%.2f")
    print("\n" + "="*80)
    print(f"[SUCCESS] Summary table saved to: {output_filename}")
    print("="*80)
    
# ============================================================================
# CORE PLOTTING FUNCTION
# ============================================================================

def plot_problem_comparison(problem: str, problem_data: Dict, output_dir: str):
    """Generates a comprehensive plot showing the achieved Pareto front for each combination."""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(16, 10))
    styles = {
        ('NSGA-II', 'Baseline'):         {'color': '#0e5fe3', 'linestyle': '-', 'marker': 'o'},
        ('NSGA-II', 'Deep Search'):       {'color': '#b512a2', 'linestyle': '--', 'marker': 's'},
        ('NSGA-II', 'High Exploration'): {'color': '#ba0b34', 'linestyle': ':', 'marker': '^'},
        ('SPEA2', 'Baseline'):         {'color': '#c95b0c', 'linestyle': '-', 'marker': 'o'},
        ('SPEA2', 'Deep Search'):       {'color': '#31bf11', 'linestyle': '--', 'marker': 's'},
        ('SPEA2', 'High Exploration'): {'color': '#096360', 'linestyle': ':', 'marker': '^'}
    }
    for param_set in PARAMETER_SETS:
        for algorithm in ALGORITHMS:
            data = problem_data.get(param_set, {}).get(algorithm, {})
            fronts_np = data.get('fronts_np', [])
            if not fronts_np: continue
            all_solutions = np.vstack(fronts_np)
            if all_solutions.size == 0: continue
            achieved_front = find_non_dominated_front(all_solutions)
            style = styles[(algorithm, param_set)]
            label = f'{algorithm} ({param_set})'
            ax.scatter(all_solutions[:, 0], all_solutions[:, 1], color=style['color'], marker=style['marker'], alpha=0.15, s=40, edgecolors='none')
            if achieved_front.size > 0:
                ax.plot(achieved_front[:, 0], achieved_front[:, 1], color=style['color'], linestyle=style['linestyle'], linewidth=2.2, marker=style['marker'], markersize=7, label=label, markeredgecolor='k', markeredgewidth=0.5)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=12, title="Experimental Setups", title_fontsize=14, loc='best')
    ax.set_title(f'Achieved Pareto Fronts for Problem: {problem}', fontsize=20, fontweight='bold')
    ax.set_xlabel('Total Distance (Objective 1)', fontsize=16)
    ax.set_ylabel('Maximum Route Length (Objective 2)', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=12)
    filename = f"{problem}_fronts_comparison.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  - Multi-front plot saved for {problem}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("="*80)
    print("STARTING MULTI-OBJECTIVE ALGORITHM ANALYSIS")
    print("="*80)
    
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # Step 1: Load all data
    print("\n--- Loading all summary and front data... ---")
    all_data = {p: {ps: {a: {} for a in ALGORITHMS} for ps in PARAMETER_SETS} for p in PROBLEM_NAMES}
    for problem in PROBLEM_NAMES:
        for param_set in PARAMETER_SETS:
            for algorithm in ALGORITHMS:
                all_data[problem][param_set][algorithm]['summaries'] = load_summary_data(algorithm, problem, param_set)
                fronts_list = load_pareto_fronts(algorithm, problem, param_set)
                all_data[problem][param_set][algorithm]['fronts_np'] = fronts_to_array(fronts_list)
    print("All data loaded successfully.")

    # Step 2: Perform statistical analysis
    print("\n--- Performing statistical analysis... ---")
    statistical_results = []
    for problem in PROBLEM_NAMES:
        all_points_for_problem = []
        for param_set in PARAMETER_SETS:
            for algorithm in ALGORITHMS:
                fronts_np = all_data[problem][param_set][algorithm]['fronts_np']
                if fronts_np:
                    all_points_for_problem.append(np.vstack(fronts_np))
        if not all_points_for_problem: continue
        ref_point = np.max(np.vstack(all_points_for_problem), axis=0) * 1.1
        print(f"  - Unified Reference Point for {problem}: [{ref_point[0]:.2f}, {ref_point[1]:.2f}]")

        for param_set in PARAMETER_SETS:
            for algorithm in ALGORITHMS:
                summaries = all_data[problem][param_set][algorithm]['summaries']
                fronts_np = all_data[problem][param_set][algorithm]['fronts_np']
                
                time_mean, time_std = (np.mean([s['wall_clock_time_sec'] for s in summaries]), np.std([s['wall_clock_time_sec'] for s in summaries])) if summaries else (0,0)
                
                hv_indicator = HV(ref_point=ref_point)
                hv_values = [hv_indicator(f) for f in fronts_np if f.size > 0]
                hv_mean, hv_std = (np.mean(hv_values), np.std(hv_values)) if hv_values else (0,0)
 
                # --- 3. CALCULATE SPACING METRIC ---
                sp_indicator = SpacingIndicator()
                # Spacing is only defined for fronts with more than one solution
                sp_values = [sp_indicator(f) for f in fronts_np if f.shape[0] > 1]
                sp_mean, sp_std = (np.mean(sp_values), np.std(sp_values)) if sp_values else (0,0)

                # --- 4. ADD SPACING TO THE RESULTS DICTIONARY ---
                statistical_results.append({
                    "Problem": problem, "Parameters": param_set, "Algorithm": algorithm,
                    "Mean Runtime (s)": time_mean, "Std Dev Runtime (s)": time_std,
                    "Mean Hypervolume": hv_mean, "Std Dev Hypervolume": hv_std,
                    "Mean Spacing": sp_mean, "Std Dev Spacing": sp_std
                })
    print("Statistical analysis complete.")

    # Step 3: Create the summary CSV
    if statistical_results:
        create_summary_csv(statistical_results)

    # Step 4: Generate plots
    print("\n--- Generating comparison plots for each problem... ---")
    for problem in PROBLEM_NAMES:
        try:
            plot_problem_comparison(problem, all_data[problem], PLOTS_DIR)
        except Exception as e:
            print(f"  [ERROR] Could not generate plot for {problem}: {e}")
    print("Plot generation complete.")
    
    print("\n" + "="*80)
    print("ANALYSIS SCRIPT FINISHED")
    print("="*80)

if __name__ == '__main__':
    main()