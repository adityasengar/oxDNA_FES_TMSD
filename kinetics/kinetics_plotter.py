import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse

def main(master_summary_path: Path, output_dir: Path, plots_dir: Path):
    """
    Main function to analyze simulation data and generate plots.

    Args:
        master_summary_path (Path): Path to the master simulation summary CSV file.
        output_dir (Path): Directory to save analysis results.
        plots_dir (Path): Directory to save generated plots.
    """
    # --- ADDED: Define and create an output directory for the results ---
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Results will be saved in: {output_dir}")

    plots_dir.mkdir(parents=True, exist_ok=True)
    print(f"Plots will be saved in: {plots_dir}")

    # Load the master simulation summary
    try:
        master_df = pd.read_csv(master_summary_path)
    except FileNotFoundError:
        print(f"Error: Master summary file not found at {master_summary_path}")
        exit()

    # Initialize DataFrames to store results
    columns = ['Mean', 'SEM']
    flux_df = pd.DataFrame(columns=columns)
    shoot1_df = pd.DataFrame(columns=columns)
    shoot2_df = pd.DataFrame(columns=columns)
    shoot3_df = pd.DataFrame(columns=columns)
    rate_df = pd.DataFrame(columns=columns)

    # Iterate through each unique simulation type (System)
    simulation_types = master_df['System'].unique()

    for simulation_type in simulation_types:
        system_data = master_df[master_df['System'] == simulation_type].copy()

        # --- Process Flux values (1/FLUX) ---
        # Filter out zero flux values before calculating 1/flux
        flux_values_nonzero = system_data[system_data['Flux value'] != 0]['Flux value']
        if len(flux_values_nonzero) > 0:
            inv_flux_values = 1 / flux_values_nonzero
            flux_mean = np.mean(inv_flux_values)
            flux_sem = np.std(inv_flux_values) / np.sqrt(len(inv_flux_values)) if len(inv_flux_values) > 1 else np.nan
        else:
            flux_mean = np.nan
            flux_sem = np.nan
        flux_df.loc[simulation_type] = [flux_mean, flux_sem]

        # --- Process SHOOT probabilities ---
        for shoot_col, target_df in [('SHOOT1 prob', shoot1_df), ('SHOOT2 prob', shoot2_df), ('SHOOT3 prob', shoot3_df)]:
            probs = system_data[system_data[shoot_col] != 0][shoot_col]
            probs = probs.dropna() # More robust way to remove NaN values
            if len(probs) > 0:
                prob_mean = np.mean(probs)
                prob_sem = np.std(probs) / np.sqrt(len(probs)) if len(probs) > 1 else np.nan
            else:
                prob_mean = np.nan
                prob_sem = np.nan
            target_df.loc[simulation_type] = [prob_mean, prob_sem]

        # --- Process Rate values ---
        rates = system_data[system_data['rate'] != 0]['rate']
        rates = rates.dropna() # More robust way to remove NaN values
        if len(rates) > 0:
            rate_mean = np.mean(rates)
            rate_sem = np.std(rates) / np.sqrt(len(rates)) if len(rates) > 1 else np.nan
        else:
            rate_mean = np.nan
            rate_sem = np.nan
        rate_df.loc[simulation_type] = [rate_mean, rate_sem]

    # --- ADDED: Save the initial summary dataframes ---
    flux_df.to_csv(output_dir / "flux_summary.csv")
    shoot1_df.to_csv(output_dir / "shoot1_summary.csv")
    shoot2_df.to_csv(output_dir / "shoot2_summary.csv")
    shoot3_df.to_csv(output_dir / "shoot3_summary.csv")
    rate_df.to_csv(output_dir / "rate_summary.csv")
    print("Saved initial summary dataframes.")
    print('************************************************************')


    # Define the groups for plotting
    groups = {
        'C': ['at1', 'p1', 'gc3', 'gc5b', 'ev1'],
        'C.U': ['at1U', 'p1U', 'gc3U', 'gc5bU', 'ev1U'],
        'MC': ['at1hyb','p1hyb', 'gc3hyb','gc5bhyb', 'ev1hyb'],
        'MC.U': ['at1hybU','p1hybU','gc3hybU','gc5bhybU', 'ev1hybU'],
        'O': ['at1nobub', 'p1nobub','gc3nobub', 'gc5bnobub','ev1nobub'],
        'O.U': ['at1nobubU','p1nobubU', 'gc3nobubU','gc5bnobubU', 'ev1nobubU']
    }

    base = ['at1', 'p1', 'gc3', 'gc5b', 'ev1']

    # --- MODIFIED: Added a filename parameter to save the processed dataframe ---
    def convert(df, title='', y_label='', filename=None):
        """
        Processes a dataframe for plotting and optionally saves it to a CSV file.
        """
        # Create a new DataFrame with 'base' simulations as the index
        new_df = pd.DataFrame(index=base)

        # Iterate through the groups and fill in the corresponding columns
        for group, simulations in groups.items():

            mean_values = []
            sem_values = []
            for sim_base in base:
                # Find the simulation that matches the base simulation
                matched_sim = None
                for sim in simulations:
                    if sim.startswith(sim_base):
                        matched_sim = sim
                        break
                if matched_sim and matched_sim in df.index:
                    mean = df.loc[matched_sim, 'Mean']
                    sem = df.loc[matched_sim, 'SEM']
                else:
                    mean = np.nan
                    sem = np.nan
                mean_values.append(mean)
                sem_values.append(sem)
            new_df[f'{group} Mean'] = mean_values
            new_df[f'{group} SEM'] = sem_values

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(base))  # Positions for the x-axis
        labels = base  # X-axis labels

        colors = {
            'C': 'blue',
            'C.U': 'red',
            'MC': 'orange',
            'MC.U': 'magenta',
            'O': 'green',
            'O.U': 'black'
        }

        # Plot error bars for each group
        for group, color in colors.items():
            mean_col = f'{group} Mean'
            sem_col = f'{group} SEM'
            ax.errorbar(
                x, new_df[mean_col], yerr=new_df[sem_col],
                label=group, fmt='o--', capsize=4, color=color
            )

        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_xlabel('Simulation')
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.legend()

        # Set y-axis to logarithmic scale if plotting rates
        # A more robust check for the rate dataframe
        if 'Rate' in title:
            ax.set_yscale('log')

        plot_filename = title.replace(' ', '_').replace('/', '_') + ".png"
        plot_path = plots_dir / plot_filename
        plt.savefig(plot_path)
        plt.close(fig)

        # Display the resulting DataFrame
        print(new_df)

        # --- ADDED: Save the processed dataframe if a filename is provided ---
        if filename:
            save_path = output_dir / filename
            new_df.to_csv(save_path)
            print(f"Saved processed dataframe to {save_path}")

        return new_df

    print('FLUX values:')
    print(flux_df)
    print('************************************************************')

    print('Probability of Success - SHOOT1:')
    print(shoot1_df)
    print('************************************************************')

    print('Probability of Success - SHOOT2:')
    print(shoot2_df)
    print('************************************************************')

    print('Probability of Success - SHOOT3:')
    print(shoot3_df)
    print('************************************************************')

    print('Total Rate Values:')
    print(rate_df)
    print('************************************************************')

    # --- MODIFIED: Calls to convert now include a filename for saving ---
    print('1/FLUX:')
    flux_new_df = convert(flux_df, title='1/FLUX', y_label='1/FLUX Value', filename='flux_processed.csv')
    print('************************************************************')

    print('Prob(Shoot1)')
    shoot1_new_df = convert(shoot1_df, title='Probability of Success - SHOOT1', y_label='Probability', filename='shoot1_processed.csv')
    print('************************************************************')

    print('Prob(Shoot2)')
    shoot2_new_df = convert(shoot2_df, title='Probability of Success - SHOOT2', y_label='Probability', filename='shoot2_processed.csv')
    print('************************************************************')

    print('Prob(Shoot3)')
    shoot3_new_df = convert(shoot3_df, title='Probability of Success - SHOOT3', y_label='Probability', filename='shoot3_processed.csv')
    print('************************************************************')

    print('Rate')
    rate_new_df = convert(rate_df, title='Rate', y_label='Rate', filename='rate_processed.csv')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze simulation data and generate plots.")
    parser.add_argument("master_summary_path", type=Path, help="Path to the master simulation summary CSV file.")
    parser.add_argument("--output_dir", type=Path, default=Path("./analysis_results"), help="Directory to save analysis results.")
    parser.add_argument("--plots_dir", type=Path, default=Path("./plots"), help="Directory to save generated plots.")
    args = parser.parse_args()

    main(args.master_summary_path, args.output_dir, args.plots_dir)

