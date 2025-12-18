import pandas as pd
from pathlib import Path
from summary import main as run_summary_analysis

def main():
    project_root = Path("./")
    output_base_dir = project_root / "FFS_values"
    
    # List all case directories (e.g., at1, at1hyb, etc.)
    case_dirs = [
        d for d in project_root.iterdir() 
        if d.is_dir() and d.name not in ["FFS_values", ".git", ".idea", "__pycache__"]
    ]
    
    all_systems_data = []

    print(f"Found {len(case_dirs)} simulation cases to process.")

    for case_path in sorted(case_dirs):
        print(f"\n{'='*80}")
        print(f"Processing case: {case_path.name}")
        print(f"{ '='*80}")
        
        # Run the modified summary script for each case
        case_df = run_summary_analysis(case_path, output_base_dir)
        
        if case_df is not None:
            case_df['System'] = case_path.name
            all_systems_data.append(case_df)
        else:
            print(f"[WARNING] No data returned for case: {case_path.name}")

    if all_systems_data:
        # Combine all individual DataFrames into a master DataFrame
        master_df = pd.concat(all_systems_data, ignore_index=True)
        
        # Reorder columns to have 'System' first
        cols = ['System'] + [col for col in master_df.columns if col != 'System']
        master_df = master_df[cols]

        master_output_path = output_base_dir / "master_simulation_summary.csv"
        master_df.to_csv(master_output_path, index=False, float_format='%.6g')
        print(f"\n{'='*80}")
        print(f"Master summary file saved to: {master_output_path.resolve()}")
        print(f"{ '='*80}")
        print("\nMaster Summary Table:")
        print(master_df.to_string())
    else:
        print("\n[ERROR] No data was collected for the master summary. Exiting.")

if __name__ == "__main__":
    main()
