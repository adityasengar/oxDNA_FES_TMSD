# oxDNA Free Energy Surface Project

This repository contains data and analysis scripts for calculating the free energy surface of DNA bubble formation and hybridization using the oxDNA model.

## Directory Structure

The repository is organized into two main directories:

*   `kinetics/`: Contains data and scripts related to the kinetics of DNA bubble formation.
    *   `at1/`, `at1U/`, `ev1/`, `ev1U/`: Example simulation data for different sequences.
    *   `kinetics_plotter.py`: Script for plotting kinetics data.
    *   `master_data_aggregator.py`: Script for aggregating data from multiple simulations.
    *   `summary.py`: Script for summarizing simulation results.
*   `thermo/`: Contains data and scripts related to the thermodynamics of DNA hybridization.
    *   `closed/`, `closed_U/`, `hyb/`, `open/`, `open_U/`: Simulation data for different thermodynamic states.
    *   `free_energy_calculator.py`: Script for calculating free energy from simulation data.
    *   `thermo_data.xlsx`: Spreadsheet containing thermodynamic data.

## Usage

The Python scripts in the `kinetics` and `thermo` directories can be used to analyze the simulation data. The specific usage of each script is documented within the script itself.
