import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit
from tqdm import tqdm
from collections import defaultdict
from data_io import load_results, save_tc_peaks_json
from config import highres

print(f"[config] Running in {'HIGH-RES' if highres else 'COARSE'} mode")

# Set paths and label suffix based on mode
results_dir = "results_highres" if highres else "results"
output_dir = "peak_data_highres" if highres else "peak_data"
label = "highres" if highres else ""

def extract_tc_peaks(data, q_val, quantity='c'):
    L_to_peakT = {}
    L_values = sorted(set(d['L'] for d in data if d['q'] == q_val))

    for L in tqdm(L_values, desc=f"Finding T_c(L) for q={q_val}"):
        subset = [d for d in data if d['q'] == q_val and d['L'] == L]
        if len(subset) < 5:
            continue
        subset = sorted(subset, key=lambda x: x['T_star'])

        T_vals = np.array([d['T_star'] for d in subset])
        Q_vals = np.array([d[quantity] for d in subset])

        cs = CubicSpline(T_vals, Q_vals)
        T_fine = np.linspace(T_vals[0], T_vals[-1], 500)
        Q_fine = cs(T_fine)

        Tc_L = T_fine[np.argmax(Q_fine)]
        L_to_peakT[L] = Tc_L

    return L_to_peakT

def fit_tc_infinity(Ls, Tcs):
    def scaling_func(L, Tc_inf, A, x):
        return Tc_inf + A * L**(-x)

    popt, pcov = curve_fit(scaling_func, Ls, Tcs, bounds=([0, -np.inf, 0.1], [2.0, np.inf, 5.0]))
    return popt, pcov

def plot_fitted_tc(L_to_Tc, popt, q_val, quantity, label=""):
    Ls = np.array(sorted(L_to_Tc.keys()))
    Tcs = np.array([L_to_Tc[L] for L in Ls])

    Tc_inf, A, x = popt
    L_fit = np.linspace(min(Ls), max(Ls), 200)
    Tc_fit = Tc_inf + A * L_fit**(-x)

    plt.figure(figsize=(7, 5))
    plt.plot(Ls, Tcs, 'o', label='Extracted $T_c(L)$')
    plt.plot(L_fit, Tc_fit, '-', label=fr'Fit: $T_c(\infty)={Tc_inf:.4f}$, $x={x:.2f}$')
    plt.title(f'Critical Temperature Fit (q={q_val}, quantity={quantity})')
    plt.xlabel('L')
    plt.ylabel('$T_c(L)$')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    folder = f"figures/fits_{label}" if label else "figures/fits"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/Tc_fit_q{q_val}_{quantity}_{label}.png" if label else f"{folder}/Tc_fit_q{q_val}_{quantity}.png"
    plt.savefig(filename, dpi=300)
    print(f"Saved fit plot: {filename}")
    plt.close()

def find_peak_T_for_q(data, q_val):
    T_to_c = defaultdict(list)
    for d in data:
        if d.get("q") == q_val and "T_star" in d and "c" in d:
            T_to_c[d["T_star"]].append(d["c"])

    T_vals = sorted(T_to_c.keys())
    if not T_vals:
        print(f"[WARN] No T* data found for q={q_val}. Skipping peak histogram.")
        return None

    avg_c_vals = [np.mean(T_to_c[T]) for T in T_vals]
    return T_vals[np.argmax(avg_c_vals)]

if __name__ == "__main__":
    data = load_results(results_dir)
    q_vals = [2, 3, 4]
    quantity = 'c'  # or 'chi'

    for q in tqdm(q_vals, desc="Processing q-values"):
        print(f"\n--- q = {q}, quantity = {quantity}, highres={highres} ---")
        L_to_Tc = extract_tc_peaks(data, q_val=q, quantity=quantity)
        print(f"T_c(L) values for q={q}:")
        for L in sorted(L_to_Tc):
            print(f"  L={L}: T_c ≈ {L_to_Tc[L]:.4f}")
        if len(L_to_Tc) < 3:
            print(f"Not enough data for q={q}")
            continue

        Ls = np.array(list(L_to_Tc.keys()))
        Tcs = np.array(list(L_to_Tc.values()))

        popt, pcov = fit_tc_infinity(Ls, Tcs)
        Tc_inf, A, x = popt
        print(f"Estimated T_c(inf) = {Tc_inf:.5f}, A = {A:.3f}, x = {x:.3f}")

        save_tc_peaks_json(q, L_to_Tc, Tc_inf, quantity, out_dir=output_dir, label=label)
        plot_fitted_tc(L_to_Tc, popt, q_val=q, quantity=quantity, label=label)
