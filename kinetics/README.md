# oxDNA Strand Displacement Kinetics Analysis

This project contains a set of Python scripts to analyze raw simulation data from oxDNA simulations of DNA strand displacement events. The analysis is based on the Forward Flux Sampling (FFS) method, which calculates kinetic rates by measuring an initial flux and a series of conditional probabilities from shooting stages.

## Folder Structure and Nomenclature

The main directory `/kinetics/FINAL/` contains simulation data categorized by system design, along with Python scripts for analysis.

*   `summary.py`, `master_data_aggregator.py`, `kinetics_plotter.py`: Python scripts for data processing and analysis.

### Simulation Data Key

The simulation data is organized into folders, each representing a different DNA system (e.g., `at1`, `p1`, `gc3U`, etc.). The naming convention indicates the system's design:
*   **Base name** (e.g., `at1`, `ev1`): Standard closed topology designs.
*   **`_U` suffix** (e.g., `at1U`): "Unique" designs with sequence modifications.
*   **`hyb` or `_MC`** (e.g., `at1hyb`): "Modulated Closed" topologies where a modulator strand is present.
*   **`nobub` or `_O`** (e.g., `at1nobub`): "Open" topologies.

Each system-specific folder (e.g., `at1/`) contains subdirectories for each stage of the FFS simulation.

## Simulation Workflow and File Structure

The kinetic rate is calculated using Forward Flux Sampling (FFS), which involves two main steps performed in sequence:

1.  **FLUX Simulations**: An initial, long simulation is run in the unbound state (Basin A) to measure the rate of crossing the first interface. This provides the initial flux.
2.  **SHOOT Simulations**: A series of short, unbiased trajectories ("shoots") are launched from configurations saved at each interface. This is done in stages (`SHOOT1`, `SHOOT2`, `SHOOT3`) to calculate the conditional probability of reaching the next interface.

The overall rate is the product of the initial flux and the success probabilities from all SHOOT stages.

### Key Files in Each System Folder (e.g., `/at1/`)

*   `topology.top`: Defines the connectivity and nucleotide types for the DNA strands.
*   `op.dat`: Specifies the order parameters used to monitor the reaction's progress.
*   `seq.txt`: Contains the DNA sequences of the strands.
*   `conditions.txt`: Lists experimental conditions.
*   **`FLUX/`**: Contains replicas of the initial flux simulation (e.g., `FLUX_1/`, `FLUX_2/`).
    *   `input`: The primary oxDNA input file for the flux simulation.
    *   `flux_summary.txt` (Output): A key output file summarizing the first-crossing events.
*   **`SHOOT1/`, `SHOOT2/`, `SHOOT3/`**: Each directory contains replicas for the corresponding shooting stage.
    *   `input`: The oxDNA input file for that shooting stage.
    *   `ffs.log` (Output): A log file recording the success or failure of each trajectory, used to calculate probabilities.

## Analysis Scripts

The analysis pipeline processes the raw simulation outputs to produce aggregated summary tables and plots.

*   **`summary.py`**: Parses the raw `flux_summary.txt` (from `FLUX` runs) and `ffs.log` (from `SHOOT` runs) files for a single simulation case to calculate flux, success/failure counts, and probabilities for each stage.
*   **`master_data_aggregator.py`**: Iterates through all simulation case directories, runs `summary.py` on each replica, and compiles the results into a single `master_simulation_summary.csv` file.
*   **`kinetics_plotter.py`**: Reads the master summary file, calculates the mean and standard error of the mean (SEM) across replicas, and generates final summary plots and processed data tables.

## How to Run the Analysis

1.  **Aggregate Data**:
    First, run the `master_data_aggregator.py` script. It will automatically discover all system directories, process their raw data, and generate individual summary CSVs and a master summary file.
    ```bash
    python3 master_data_aggregator.py
    ```

2.  **Generate Plots and Final Summaries**:
    After the master summary is created, run `kinetics_plotter.py` to perform the final analysis, calculate mean rates, and generate plots.
    ```bash
    python3 kinetics_plotter.py
    ```

## Expected Outputs

*   `FFS_values/`: Contains a summary CSV for each individual simulation case, plus the main `master_simulation_summary.csv`.
*   `analysis_results/`: Contains processed data tables (`flux_summary.csv`, `rate_processed.csv`, etc.).
*   `plots/`: Contains the final analysis plots as PNG images (e.g., `rate_plot.png`).

## Simulation Methodology (Summary from `main.tex`)

The simulations use the coarse-grained oxDNA model to represent DNA.

### Forward Flux Sampling (FFS)

FFS is used to estimate the rate of rare events (like strand displacement) by breaking the transition from an initial state (A) to a final state (B) into a series of more likely steps.

1.  **Order Parameter**: A collective variable, `Q`, is defined to track the progress of the reaction (e.g., based on the distance between the invader and target strands).
2.  **Interfaces**: A series of non-intersecting interfaces are defined along the reaction pathway based on the value of `Q`.
3.  **Initial Flux**: A long, unbiased simulation is run in state A to measure the rate of trajectories crossing the first interface. This is the `FLUX` stage.
4.  **Conditional Probabilities**: Short trajectories ("shoots") are launched from points on each interface to calculate the probability of reaching the next interface before returning to state A. These are the `SHOOT` stages (`SHOOT1`, `SHOOT2`, `SHOOT3`).

The final rate is calculated as the product of the initial flux and the conditional probabilities from all shooting stages.