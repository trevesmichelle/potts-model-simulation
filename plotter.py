import os
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from fit_tc import find_peak_T_for_q

def load_results(out_dir):
    data = []
    for fname in os.listdir(out_dir):
        if fname.endswith('.json'):
            with open(os.path.join(out_dir, fname)) as f:
                data.append(json.load(f))
    return data

def plot_histograms(data, q_val, L_val, T_star_val, save_dir="figures/histograms"):
    subset = [
        d for d in data
        if d["q"] == q_val and d["L"] == L_val and abs(d["T_star"] - T_star_val) < 1e-6
    ]
    if not subset:
        print(f"[WARN] No data for q={q_val}, L={L_val}, T*={T_star_val}")
        return

    d = subset[0]
    os.makedirs(save_dir, exist_ok=True)

    plt.hist(d["energies"], bins=50, color="skyblue", edgecolor="k")
    plt.title(f"Energy Histogram — q={q_val}, L={L_val}, T*={T_star_val:.3f}")
    plt.xlabel("Energy")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{save_dir}/energy_q{q_val}_L{L_val}_T{T_star_val:.3f}.png")
    plt.close()

    plt.hist(d["magnetizations"], bins=50, color="salmon", edgecolor="k")
    plt.title(f"Magnetization Histogram — q={q_val}, L={L_val}, T*={T_star_val:.3f}")
    plt.xlabel("Order Parameter m")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{save_dir}/magnetization_q{q_val}_L{L_val}_T{T_star_val:.3f}.png")
    plt.close()

    print(f"Saved histograms for q={q_val}, L={L_val}, T*={T_star_val:.3f}")

def plot_quantity(data, q_val, quantity='c', ylabel='Specific Heat c', save_dir="figures"):
    filtered = [d for d in data if d['q'] == q_val]
    L_values = sorted(set(d['L'] for d in filtered))
    color_map = cm.viridis(np.linspace(0, 1, len(L_values)))

    plt.figure(figsize=(8, 6))
    for L, color in zip(L_values, color_map):
        subset = sorted([d for d in filtered if d['L'] == L], key=lambda x: x['T_star'])
        T_vals = [d['T_star'] for d in subset]
        y_vals = [d[quantity] for d in subset]
        plt.plot(T_vals, y_vals, label=f'L = {L}', color=color)

    plt.title(f'{ylabel} vs Temperature (q = {q_val})')
    plt.xlabel('T*')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    os.makedirs(save_dir, exist_ok=True)
    filename = f"{save_dir}/{quantity}_q{q_val}.png"
    plt.savefig(filename, dpi=300)
    print(f"Saved plot: {filename}")
    plt.close()

def run_plotting(q_values, L_values, quantity='c', data_dir="results", output_dir="figures", do_histograms=True):
    data = load_results(data_dir)
    for q in q_values:
        ylabel = "Specific Heat c" if quantity == 'c' else "Susceptibility χ"
        plot_quantity(data, q, quantity=quantity, ylabel=ylabel, save_dir=output_dir)

        if do_histograms:
            T_peak = find_peak_T_for_q(data, q)
            print(f"  q={q}: estimated T* ≈ {T_peak:.4f}")
            for L in L_values:
                plot_histograms(data, q_val=q, L_val=L, T_star_val=T_peak, save_dir=f"{output_dir}/histograms")

if __name__ == "__main__":
    q_vals = [2, 3, 4]
    L_vals = [5, 8, 11, 14, 17, 20]

    # Toggle between coarse and high-res mode
    highres = True

    results_dir = "results_highres" if highres else "results"
    output_dir = "figures/highres" if highres else "figures"

    print(f"\n--- Plotting from '{results_dir}' → saving to '{output_dir}' ---\n")
    run_plotting(q_vals, L_vals, quantity='c', data_dir=results_dir, output_dir=output_dir)
    run_plotting(q_vals, L_vals, quantity='chi', data_dir=results_dir, output_dir=output_dir)
