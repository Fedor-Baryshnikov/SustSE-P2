import pandas as pd
import os
import glob

def analyze_csv(filepath):
    df = pd.read_csv(filepath)
    
    cpu_joules = 0
    if 'PACKAGE_ENERGY (J)' in df.columns:
        cpu_joules = df['PACKAGE_ENERGY (J)'].iloc[-1] - df['PACKAGE_ENERGY (J)'].iloc[0]
        
    dram_joules = 0
    if 'DRAM_ENERGY (J)' in df.columns:
        dram_joules = df['DRAM_ENERGY (J)'].iloc[-1] - df['DRAM_ENERGY (J)'].iloc[0]
        
    gpu_joules = 0
    if 'GPU0_ENERGY (J)' in df.columns:
        gpu_joules = df['GPU0_ENERGY (J)'].iloc[-1] - df['GPU0_ENERGY (J)'].iloc[0]
    elif 'GPU0_POWER (mWatts)' in df.columns and 'Delta' in df.columns:
        gpu_joules = (df['GPU0_POWER (mWatts)'] * df['Delta']).sum() / 1_000_000
        
    total_joules = cpu_joules + dram_joules + gpu_joules
    
    return {
        "cpu_j": cpu_joules,
        "dram_j": dram_joules,
        "gpu_j": gpu_joules,
        "total_j": total_joules,
    }

def read_tokens(prefix):
    tokens_file = f"{prefix}_tokens.txt"
    result = {}
    if os.path.exists(tokens_file):
        with open(tokens_file) as f:
            for line in f:
                if ":" in line:
                    model, tok = line.strip().split(":")
                    result[model] = int(tok)
    return result

def main():
    results_dir = "results_comparison"
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    
    summary = []
    for f in sorted(csv_files):
        try:
            stats = analyze_csv(f)
            label = os.path.basename(f).replace(".csv", "")
            stats["label"] = label
            stats["strategy"] = label.split("_")[0]

            prefix = os.path.join(results_dir, "_".join(label.split("_")[:-1]))
            token_counts = read_tokens(prefix)
            stats.update(token_counts)

            summary.append(stats)
        except Exception as e:
            print(f"Error analyzing {f}: {e}")
            
    if not summary:
        print("No results found.")
        return
        
    df = pd.DataFrame(summary)

    print("\n--- Raw Results ---")
    display_cols = ["label", "strategy", "total_j"] + [c for c in df.columns if c not in ["label", "strategy", "total_j", "cpu_j","dram_j","gpu_j"]]
    print(df[display_cols])

    grouped = df.groupby("strategy")

    stats = grouped["total_j"].agg([
        ("mean_j", "mean"),
        ("std_j", "std"),
        ("min_j", "min"),
        ("max_j", "max"),
        ("p25_j", lambda x: x.quantile(0.25)),
        ("median_j", "median"),
        ("p75_j", lambda x: x.quantile(0.75))
    ])

    final = stats

    print("\nEnergy Statistics per Strategy:")
    print(final.round(3))

    output_file = os.path.join(results_dir, "summary_stats.csv")
    final.to_csv(output_file)
    print(f"\nSaved summary to {output_file}")

if __name__ == "__main__":
    main()