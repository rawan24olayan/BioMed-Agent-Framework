import scanpy as sc
import os

# Harvard JD check: Handling large-scale multi-omics datasets
def load_and_summarize_omics(file_path):
    """
    Loads a scRNA-seq (AnnData) file and performs a basic QC summary.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return None

    print(f"--- LOADING OMICS DATA: {os.path.basename(file_path)} ---")
    
    # Load the AnnData object (Cells x Genes)
    adata = sc.read_h5ad(file_path)
    
    # Basic QC Metrics
    print(f"Dataset Shape: {adata.n_obs} cells x {adata.n_vars} genes")
    print(f"Metadata Columns: {list(adata.obs.columns)}")
    
    # Check for specific markers (e.g., TREM2 for Alzheimer's)
    target_gene = "TREM2"
    if target_gene in adata.var_names:
        avg_expr = adata[:, target_gene].X.mean()
        print(f"Target Gene '{target_gene}' detected. Mean Expression: {avg_expr:.4f}")
    
    return adata

if __name__ == "__main__":
    # Note: For testing, we usually use a small sample dataset
    # You can download a sample or use a path to your own .h5ad file
    print("Ready to ingest scRNA-seq data.")
