# 2D Potts Model Simulation

This project simulates the 2D Potts model using the Metropolis algorithm to investigate phase transitions in statistical physics. The simulation supports both coarse and high-resolution modes, and includes automated peak detection and finite-size scaling analysis.

---

## Project Structure

├── config.py # Global toggle for highres mode
├── main.py # Main controller script
├── potts_simulation.py # Core simulation functions (Numba-accelerated)
├── runner.py # Parallel execution of simulations (default set for 8 cores, adjust if necessary)
├── fit_tc.py # Extract and fit T_c(L) and T_c(inf)
├── plotter.py # Visualization utilities
├── data_io.py # JSON input/output helpers
├── results/ # Coarse simulation results
├── results_highres/ # High-resolution simulation results (creates a folder if one doesn't exist already)
├── peak_data/ # T_c(L) and T_c(∞) estimates from coarse runs (same as above)
├── peak_data_highres/ # High-resolution counterparts (same as above)
└── figures/ # Output plots and histograms (same as above)


---

## Running the Simulation

The project is designed to run in two stages:

### Stage 1: Coarse Simulation and Peak Estimation

1. **Set `highres` to `False`**  
   In `config.py`:
   ```python
   highres = False

2. **Enable coarse simulation**  
   In `main.py`, set:
   ```python
   run_sims = True
   run_highres_after_peak = False

3. **Run the coarse simulation**
    This will produce histograms and plots in figures/:
    ```bash
    python main.py

4. **Extract T_c(L) and fit T_c(∞)**  
   This will produce peak estimate files in peak_data/:
   ```bash
   python fit_tc.py

### Stage 2: High-Resolution Zoom-In Around T_c(∞)

1. **Set `highres` to `True`**  
   In `config.py`:
   ```python
   highres = True

2. **Enable zoom-in and skip coarse rerun**  
   In `main.py`, set:
   ```python
    run_sims = False
    run_highres_after_peak = True

3. **Run zoom-in simulations and generate plots (optional - recommended)**
    ```bash
    python main.py

4. **Recalculate T_c(∞) from high-resolution data**  
   ```bash
   python fit_tc.py

---

## Output Description
- results/: Coarse-resolution simulation outputs (.json)

- results_highres/: High-resolution simulations around estimated T_c(∞)

- figures/: Plots of specific heat, susceptibility, histograms, and scaling fits

- peak_data/: JSON files containing T_c(L) and extrapolated T_c(∞) from coarse data

- peak_data_highres/: Same as above, but from high-resolution simulations

---

## Dependencies
Install required packages with (Python 3.8 or higher is recommended.):
`bash
pip install -r requirements.txt

---

## Notes
- Ensure the peak estimation files (Tc_peaks_q*.json) exist before attempting a high-resolution run.

- All simulation parameters (e.g., number of steps, lattice sizes, temperature ranges) are defined in main.py.

- Simulation results are automatically saved and reloaded as needed.

- To avoid clutter and ensure clean reruns, it is recommended to periodically delete or archive the contents of results/, results_highres/, and figures/ before new simulations.

---

## License and Contact
This project is developed for academic use and simulation-based exploration of critical phenomena in lattice models, specifically the 2D Potts model.
