import scanpy as sc
import os
import sys

def load_and_summarize_omics(file_path=None):
    """
    Dynamically loads scRNA-seq data. 
    Accepts a path via argument or defaults to the sample data.
    """
    # Default fallback path
    if file_path is None:
        file_path = "data/raw_omics/sample_alzheimers_cells.h5ad"

    if not os.path.exists(file_path):
        print(f"ERROR: File not found at {file_path}")
        print("Tip: Run 'python3 src/utils/generate_test_data.py' to create the sample.")
        return None

    print(f"\n--- DYNAMIC LOAD: {os.path.basename(file_path)} ---")
    
    try:
        adata = sc.read_h5ad(file_path)
        print(f"Cells: {adata.n_obs} | Genes: {adata.n_vars}")
        
        # Quick check for Alzheimer's specific signal
        if "condition" in adata.obs.columns and "TREM2" in adata.var_names:
            ad_mean = adata[adata.obs['condition'] == 'Alzheimer', 'TREM2'].X.mean()
            print(f"TREM2 Mean Expression (AD Group): {ad_mean:.4f}")
            
        return adata
    except Exception as e:
        print(f"Failed to parse AnnData: {e}")
        return None

if __name__ == "__main__":
    # Check if a filename was passed via command line (e.g., python3 omics_loader.py my_data.h5ad)
    target_file = sys.argv[1] if len(sys.argv) > 1 else None
    load_and_summarize_omics(target_file)
