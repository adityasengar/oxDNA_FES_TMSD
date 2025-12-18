import os
import glob
import numpy as np
import argparse

def log_sum_exp(x):
    """
    Numerically stable implementation of log-sum-exp.
    """
    if not x:
        return -np.inf
    # Ensure x is a numpy array for vectorized operations
    x = np.array(x)
    c = np.max(x)
    return c + np.log(np.sum(np.exp(x - c)))

def calculate_free_energy_for_folder(base_folder):
    """
    Calculates the raw, volume-dependent free energy difference for a single 
    simulation folder. Returns the delta_F value if successful, otherwise returns None.
    """
    neg_log_weights_A = []
    neg_log_weights_B = []
    
    weights_map = {}
    wfile_path = os.path.join(base_folder, 'wfile.dat')
    if not os.path.exists(wfile_path):
        return None # Cannot proceed without weights
    
    try:
        with open(wfile_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 9:
                    op_key = tuple(int(p) for p in parts[0:8])
                    weight_W = float(parts[8])
                    if weight_W > 0:
                        weights_map[op_key] = np.log(weight_W)
                    else:
                        weights_map[op_key] = -np.inf
    except Exception as e:
        print(f"  Warning: Error reading weights file {wfile_path}: {e}")
        return None

    energy_files_to_process = []
    for dirpath, _, filenames in os.walk(base_folder):
        for filename in filenames:
            if filename == 'energy.dat':
                energy_files_to_process.append(os.path.join(dirpath, filename))

    if not energy_files_to_process:
        return None
        
    for file_path in energy_files_to_process:
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    columns = line.strip().split()
                    if len(columns) >= 13:
                        try:
                            op_values = tuple(int(c) for c in columns[5:13])
                            op4_value = int(columns[8])
                            log_weight = weights_map.get(op_values)

                            if log_weight is not None:
                                neg_log_weight = -log_weight
                                if op4_value == 0:
                                    neg_log_weights_A.append(neg_log_weight)
                                elif op4_value > 1:
                                    neg_log_weights_B.append(neg_log_weight)
                        except (ValueError, IndexError):
                            pass
        except Exception as e:
            print(f"  Warning: Error reading energy file {file_path}: {e}")
            continue

    if not neg_log_weights_A or not neg_log_weights_B:
        return None # A state was not observed in this folder

    log_total_prob_A = log_sum_exp(neg_log_weights_A)
    log_total_prob_B = log_sum_exp(neg_log_weights_B)
    
    # This is the raw, volume-dependent dF/kT
    return -(log_total_prob_B - log_total_prob_A)


def main(base_path: str):
    """
    Main function to find, analyze, correct, and average different sets of simulations.
    """
    # Define the reference volume for standardization
    REF_BOX_SIDE = 25.0
    V_REF = REF_BOX_SIDE**3
    
    analysis_sets = {
        'ev':  {'contains': 'ev', 'box_side': 30.0},
        'p':   {'contains': 'p', 'box_side': 40.0},
        'at':  {'contains': 'at', 'box_side': 30.0},
        'gc':  {'contains': 'gc', 'not_contains': 'gc5', 'box_side': 40.0},
        'gc5': {'contains': 'gc5', 'box_side': 40.0}
    }

    all_folders_in_path = glob.glob(os.path.join(base_path, 'bub_*'))

    for set_name, rules in analysis_sets.items():
        print("\n" + "#"*60)
        print(f"### Preparing analysis for set: '{set_name.upper()}' ###")
        
        # --- Volume Correction Setup ---
        sim_box_side = rules['box_side']
        V_SIM = sim_box_side**3
        volume_correction = np.log(V_REF / V_SIM)
        print(f"Reference box: {REF_BOX_SIDE}^3. This set's box: {sim_box_side}^3.")
        print(f"Applying correction term ln(V_ref/V_sim) = {volume_correction:.4f} to dF/kT.")
        
        filtered_folders = []
        for folder in all_folders_in_path:
            folder_name = os.path.basename(folder)
            if 'hyb' in folder_name: continue
            if rules['contains'] not in folder_name: continue
            if 'not_contains' in rules and rules['not_contains'] in folder_name: continue
            filtered_folders.append(folder)
            
        print(f"Found {len(filtered_folders)} potential folders for this set.")
        
        corrected_delta_F_values = []
        print("Analyzing individual folders...")
        for folder in sorted(filtered_folders):
            folder_name = os.path.basename(folder)
            raw_delta_F = calculate_free_energy_for_folder(folder)
            
            if raw_delta_F is not None and np.isfinite(raw_delta_F):
                corrected_delta_F = raw_delta_F + volume_correction
                corrected_delta_F_values.append(corrected_delta_F)
                print(f"  - OK: {folder_name:<12} -> Raw dF/kT = {raw_delta_F:8.4f}, Corrected dF/kT = {corrected_delta_F:8.4f}")
            else:
                print(f"  - SKIPPED: {folder_name} (Did not sample both states A and B)")

        print("\n" + "="*60)
        print(f"Final Standardized Result for Set: '{set_name.upper()}'")
        print("="*60)

        if not corrected_delta_F_values:
            print("No valid folders found to calculate a final average.")
        elif len(corrected_delta_F_values) == 1:
            print(f"Only one valid folder was found. Cannot calculate SEM.")
            print(f"  -> Standardized Free Energy (ΔF/kT) = {corrected_delta_F_values[0]:.4f}")
            print(f"  (Based on 1 folder)")
        else:
            mean_delta_F = np.mean(corrected_delta_F_values)
            std_dev = np.std(corrected_delta_F_values, ddof=1)
            sem = std_dev / np.sqrt(len(corrected_delta_F_values))
            
            print(f"  -> Standardized Free Energy (ΔF/kT) = {mean_delta_F:.4f} ± {sem:.4f}")
            print(f"  (Calculated from {len(corrected_delta_F_values)} of {len(filtered_folders)} folders)")

    print("\n" + "#"*60)
    print("### All analysis sets complete. ###")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate free energy from simulation data.")
    parser.add_argument("base_path", type=str, help="Path to the directory containing simulation folders.")
    args = parser.parse_args()
    main(args.base_path)


