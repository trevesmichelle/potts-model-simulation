# --- imports ---
from plotter import run_plotting
from runner import run_parallel_sims
import numpy as np
import os
import json
from config import highres

# --- toggle settings ---
run_sims = False             # <--- toggle running initial sims
run_highres_after_peak = True # <--- toggle zoom-in rerun around T_c(∞)

print(f"[config] Running in {'HIGH-RES' if highres else 'COARSE'} mode")

# --- define high-res function ---
def rerun_highres_around_peak(q, L_values, quantity='c', delta=0.05, n_points=60):
    peak_file = f"peak_data/Tc_peaks_q{q}_{quantity}.json"
    if not os.path.exists(peak_file):
        print(f"[WARNING] Peak file not found: {peak_file}")
        return

    with open(peak_file) as f:
        peak_data = json.load(f)

    Tc_inf = peak_data.get("Tc_infinity")
    if not Tc_inf:
        print(f"[WARNING] No Tc_infinity found in {peak_file}")
        return

    T_values = np.linspace(Tc_inf - delta, Tc_inf + delta, n_points)
    print(f"\n--> Re-running high-resolution simulations for q={q} near T_c(inf) = {Tc_inf:.4f}")
    run_parallel_sims(
        q_values=[q],
        L_values=L_values,
        T_values=T_values,
        steps=30000,
        burn_in=5000,
        out_dir="results_highres"
    )

# --- main orchestrator ---
def main():
    q_values = [2, 3, 4]
    L_values = [5, 8, 11, 14, 17, 20]
    T_values = np.linspace(0.5, 1.5, 45)

    results_dir = "results_highres" if highres else "results"
    figures_dir = "figures/highres" if highres else "figures"

    if run_sims:
        print(f"\n--- Running simulations ({'high-res' if highres else 'coarse'}) ---")
        run_parallel_sims(q_values, L_values, T_values, steps=30000 if highres else 10000,
                          burn_in=5000 if highres else 2000,
                          out_dir=results_dir)
    else:
        print(f"\n--- Skipping simulations — using existing results in '{results_dir}' ---")

    if highres and run_highres_after_peak:
        print("\n--- Re-running high-resolution simulations around T_c(inf) ---")
        for q in q_values:
            rerun_highres_around_peak(q, L_values, quantity='c', delta=0.05, n_points=60)

    print(f"\n--- Plotting quantities and histograms from {results_dir} ---")
    run_plotting(q_values, L_values, quantity='c', data_dir=results_dir, output_dir=figures_dir)
    run_plotting(q_values, L_values, quantity='chi', data_dir=results_dir, output_dir=figures_dir)

# --- run ---
if __name__ == "__main__":
    main()
