import numpy as np
import multiprocessing as mp
from functools import partial
import os
import json
from potts_simulation import run_simulation
from tqdm import tqdm

def simulate_and_save(args):
    q, L, T_star, steps, burn_in, out_dir = args
    result = run_simulation(q=q, L=L, T_star=T_star, steps=steps, burn_in=burn_in)
    result.update({'q': q, 'L': L, 'T_star': T_star})
    fname = f"q{q}_L{L}_T{T_star:.4f}_steps{steps}_burn{burn_in}.json"
    fpath = os.path.join(out_dir, fname)
    with open(fpath, 'w') as f:
        json.dump(result, f)
    return result

def run_parallel_sims(q_values, L_values, T_values, steps=10000, burn_in=1000, out_dir="results", num_procs=8):
    os.makedirs(out_dir, exist_ok=True)
    pool = mp.Pool(processes=num_procs)

    tasks = [
        (q, L, T_star, steps, burn_in, out_dir)
        for q in q_values
        for L in L_values
        for T_star in T_values
    ]

    results = []
    for result in tqdm(pool.imap_unordered(simulate_and_save, tasks), total=len(tasks), desc="Running Sims"):
        if result is not None:
            results.append(result)

    pool.close()
    pool.join()


if __name__ == "__main__":
    q_values = [2, 3, 4]
    L_values = [5, 8, 11, 14, 17, 20]
    T_values = np.linspace(0.5, 1.5, 45)

    run_parallel_sims(q_values, L_values, T_values, steps=10000, burn_in=2000)
