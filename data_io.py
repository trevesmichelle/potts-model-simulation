import os
import json

def load_results(results_dir):
    """
    Load all .json result files from a directory.
    """
    data = []
    for fname in os.listdir(results_dir):
        if fname.endswith(".json"):
            with open(os.path.join(results_dir, fname)) as f:
                data.append(json.load(f))
    return data

def save_tc_peaks_json(q, L_to_Tc, Tc_inf, quantity, out_dir="peak_data", label=""):
    os.makedirs(out_dir, exist_ok=True)
    label_suffix = f"_{label}" if label else ""
    fname = f"{out_dir}/Tc_peaks_q{q}_{quantity}{label_suffix}.json"
    with open(fname, 'w') as f:
        json.dump({
            "q": q,
            "quantity": quantity,
            "Tc_infinity": Tc_inf,
            "Tc_L": L_to_Tc
        }, f, indent=2)

