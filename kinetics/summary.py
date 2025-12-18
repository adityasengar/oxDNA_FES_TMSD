import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple

def parse_flux_summary(file_path: Path) -> Tuple[int, float]:
    """Reads a flux_summary.txt file and returns the count and value."""
    if not file_path.is_file():
        return 0, 0.0
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    flux_count = int(lines[0].split(':')[1].strip())
    flux_value = float(lines[1].split(':')[1].strip())
    
    return flux_count, flux_value

def analyze_ffs_log(file_path: Path) -> Tuple[int, int]:
    """Reads a synthetic ffs.log and returns the count of success and failure events."""
    if not file_path.is_file():
        return 0, 0
        
    success_count = 0
    failure_count = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith("SUCCESS:"):
                success_count += 1
            elif line.startswith("FAILURE:"):
                failure_count += 1
                
    return success_count, failure_count

def main(case_path: Path, output_dir: Path):
    """
    Main function to analyze the synthetic dataset and reconstruct the summary table.
    """
    # Define the number of canonical runs to process
    NUM_RUNS = 5

    print("="*60)
    print("Starting Synthetic Data Analysis Script")
    print(f"Reading from: {case_path}")
    print(f"Will write to: {output_dir}")
    print("="*60)

    if not case_path.is_dir():
        print(f"[ERROR] Synthetic data path not found: {case_path}")
        return None
    
    # Define the number of canonical runs to process
    NUM_RUNS = 5

    all_runs_data: List[Dict] = []

    # --- MAIN ANALYSIS LOOP ---
    for i in range(1, NUM_RUNS + 1):
        print(f"\n--- Analyzing Canonical Run #{i} ---")
        run_data = {}

        # 1. Process FLUX data
        flux_summary_path = case_path / f"FLUX/FLUX_{i}/flux_summary.txt"
        flux_count, flux_value = parse_flux_summary(flux_summary_path)
        run_data['Flux count'] = flux_count
        run_data['Flux value'] = flux_value
        print(f"  - FLUX: Found count={flux_count}, value={flux_value}")

        # 2. Process SHOOT stages
        shoot_stages = ['SHOOT1', 'SHOOT2', 'SHOOT3']
        all_probs = []
        for stage in shoot_stages:
            log_path = case_path / f"{stage}/SHOOT_{i}/ffs.log"
            success, failure = analyze_ffs_log(log_path)
            total = success + failure
            prob = success / total if total > 0 else 0
            
            run_data[f'{stage} success'] = success
            run_data[f'{stage} total'] = total
            run_data[f'{stage} prob'] = prob
            all_probs.append(prob)
            print(f"  - {stage}: Found success={success}, total={total}, prob={prob:.6f}")

        # 3. Calculate the final rate
        # The rate is calculated as (1 / Flux value) * P(SHOOT1) * P(SHOOT2) * P(SHOOT3)
        rate = (1 / flux_value) if flux_value != 0 else 0
        for p in all_probs:
            rate *= p
        run_data['rate'] = rate
        print(f"  - Calculated final rate: {rate:.2e}")
        
        all_runs_data.append(run_data)

    # 4. Create and save the final DataFrame
    if not all_runs_data:
        print("\n[ERROR] No data was processed. Exiting.")
        return None

    # Define the exact column order to match the original table
    column_order = [
        'Flux count', 'Flux value',
        'SHOOT1 success', 'SHOOT1 total', 'SHOOT1 prob',
        'SHOOT2 success', 'SHOOT2 total', 'SHOOT2 prob',
        'SHOOT3 success', 'SHOOT3 total', 'SHOOT3 prob',
        'rate'
    ]
    
    final_df = pd.DataFrame(all_runs_data)
    final_df = final_df[column_order] # Enforce column order

    # Save to CSV
    output_csv_file = output_dir / f"{case_path.name}.csv"
    final_df.to_csv(output_csv_file, index=False, float_format='%.6g')

    print("\n" + "="*60)
    print(f"Script finished. Reconstructed summary table saved to:")
    print(f"{output_csv_file.resolve()}")
    print("="*60)
    print("\nFinal Reconstructed Table:")
    print(final_df.to_string())
    return final_df


if __name__ == "__main__":
    main()

