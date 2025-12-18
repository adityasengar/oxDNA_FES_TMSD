# Supplementary Information: Thermodynamic Simulation Data and Analysis for DNA Systems

This repository contains the supplementary data and analysis scripts related to the thermodynamic aspects of DNA simulations, as described in the associated publication's Supplementary Information (`main.tex`). The data focuses on the runtime files required for various thermodynamic simulations using the coarse-grained oxDNA model and a Python script to calculate free energy curves.

## Folder Structure and Nomenclature

The main directory `/thermo/` contains simulation data categorized by topology and sequence design, along with the main analysis script:

*   `free_energy_calculator.py`: A Python script for calculating standardized binding free energies.

### Simulation Data Key

The simulation data is organized into the following folders based on the system's topology and design:

*   **`closed/`**: Contains simulation data for **non-unique** "closed topology" designs.
    *   `at1/`, `ev1/`, `gc3/`, `gc5b/`, `p1/`: Subfolders for each system.
*   **`closed_U/`**: Contains simulation data for **unique** "closed topology" designs. The `_U` suffix denotes "unique."
    *   `at1/`, `ev1/`, `gc3/`, `gc5b/`, `p1/`: Subfolders for each system.
*   **`open/`**: Contains simulation data for **non-unique** "open topology" designs.
    *   `at1/`, `ev1/`: Subfolders for each system.
*   **`open_U/`**: Contains simulation data for **unique** "open topology" designs.
    *   `at1/`, `ev1/`: Subfolders for each system.
*   **`hyb/`**: Contains simulation data for "modulated closed topology" designs, which study the hybridization of a modulator strand to the allosteric site.
    *   `gc3/`, `gc3U/`: Subfolders for the non-unique and unique `gc3` systems, respectively.

Each system-specific subfolder (e.g., `closed/at1/`) represents a single simulation replica and contains the runtime files detailed below.

## Key Runtime Files in Each Simulation Folder

Within each system-specific subfolder (e.g., `closed/at1/`), you will find the following files, which are essential for running and analyzing oxDNA simulations:

*   `generated.dat`: Initial configuration file, specifying the starting positions and orientations of DNA strands.
*   `generated.top`: Topology file, defining the connectivity and types of nucleotides in the DNA strands.
*   `input`: The primary input file for the oxDNA simulation, containing all simulation parameters (e.g., temperature, box size, dynamics, number of steps).
*   `op.dat`: Defines the order parameters used in the simulation, including `bond` and `mindistance` parameters, and their associated interfaces for Umbrella Sampling. This file is crucial for monitoring reaction progress.
*   `seq.txt`: Contains the DNA sequences of the strands involved in the simulation.
*   `wfile.dat`: (Specific to Umbrella Sampling) Contains the biasing weights applied to different order parameter states, used to level free-energy barriers. This file is read by `free_energy_calculator.py` for unbiasing.
*   `energy.dat`: (Output file) Contains the time series of energies and order parameter values, used by `free_energy_calculator.py` for analysis.

## Analysis Script: `free_energy_calculator.py`

This Python script is used to calculate the standardized binding free energies (ΔF_std/kT) from the Umbrella Sampling simulation outputs.

### Purpose

The script automates the process of:
1.  Reading umbrella sampling weights from `wfile.dat`.
2.  Extracting order parameter data (specifically `rho_4` for binding) from `energy.dat`.
3.  Categorizing simulation frames into "unbound" (`rho_4 = 0`) and "bound" (`rho_4 >= 1`) states.
4.  Calculating raw free energy differences using a numerically stable log-sum-exp method.
5.  Applying a volume correction to standardize the free energies to a reference volume (as detailed in `main.tex`, Section 4.2).
6.  Averaging the standardized free energies across multiple simulation replicas (folders) and calculating the Standard Error of the Mean (SEM).

### How to Use the Script

1.  **Prerequisites**: Ensure you have Python 3 and `numpy` installed.
    ```bash
    pip install numpy
    ```
2.  **Update `base_path`**: Open `free_energy_calculator.py` and modify the `base_path` variable in the `main()` function to point to the absolute path of the directory containing your simulation output folders (e.g., `/rds/general/user/asengar/home/oxDNA/sengar/bubbles2/zenodo/thermo/`).
    ```python
    # In free_energy_calculator.py
    base_path = '/path/to/your/thermo/directory' # <--- CHANGE THIS
    ```
3.  **Customize `analysis_sets` (Optional)**: The `analysis_sets` dictionary in `main()` defines how simulation folders are grouped and analyzed. You can modify this to match your specific folder naming conventions and simulation box sizes.
    *   `'contains'`: Substring required in the folder name.
    *   `'not_contains'`: Substring that must *not* be in the folder name.
    *   `'box_side'`: The edge length of the cubic simulation box used for runs in that set (e.g., `30.0`, `40.0`). This is critical for correct volume correction.
4.  **Run the Script**: Execute the script from your terminal.
    ```bash
    python free_energy_calculator.py
    ```
    The script will print the calculated standardized free energies and their SEMs for each defined analysis set.

## Simulation Methodologies (Summary from `main.tex`)

The simulations utilize the coarse-grained oxDNA model, which represents DNA as a string of nucleotides with specific interaction sites.

### Umbrella Sampling

This technique is employed to overcome free-energy barriers and improve equilibration. It involves applying artificial biasing weights (`W(rho)`) to high free energy states. The `wfile.dat` files contain these weights.

### Order Parameters

Two main types of order parameters are used for thermodynamic measurements:

*   **`bond`**: Tracks the number of formed base pairs within a specified list.
*   **`mindistance`**: Monitors the minimum distance between specified nucleotide pairs, comparing it against user-defined `interfaces`.

For the closed topology simulations, an 8-dimensional order parameter `rho = (rho_1, ..., rho_8)` is used, where `rho_4` specifically tracks the bond order parameter between the `beta` (target) and `beta*` (invader) domains, defining the unbound (`rho_4 = 0`) and bound (`rho_4 >= 1`) states.

### Standardization to a Reference Volume

The calculated raw free energy differences are standardized to a reference volume (`V_ref = (25)^3` internal units) by adding an ideal translational correction `ln(V_ref/V_sim)`, where `V_sim` is the simulation box volume.

