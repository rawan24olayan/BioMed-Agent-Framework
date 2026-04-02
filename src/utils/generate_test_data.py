import scanpy as sc
import numpy as np
import pandas as pd
import anndata as ad
import os

def create_synthetic_omics():
    """Generates a small AnnData file to test the pipeline."""
    print("Generating synthetic scRNA-seq data...")
    
    n_cells = 100
    n_genes = 20
    
    # 1. Create random expression matrix (Cells x Genes)
    data = np.random.poisson(lam=1.0, size=(n_cells, n_genes))
    
    # 2. Define Gene Names (Including TREM2 for our AD research)
    gene_names = [f"GENE_{i}" for i in range(n_genes-1)] + ["TREM2"]
    
    # 3. Define Cell Metadata (50 Control, 50 Alzheimer's)
    obs = pd.DataFrame(index=[f"cell_{i}" for i in range(n_cells)])
    obs['condition'] = ['Control'] * 50 + ['Alzheimer'] * 50
    obs['cell_type'] = np.random.choice(['Microglia', 'Neuron', 'Astrocyte'], n_cells)

    # 4. Create the AnnData object
    adata = ad.AnnData(X=data, obs=obs, var=pd.DataFrame(index=gene_names))
    
    # 5. Save to the raw_omics folder
    output_path = "data/raw_omics/sample_alzheimers_cells.h5ad"
    adata.write(output_path)
    
    print(f"SUCCESS: Created synthetic omics data at {output_path}")

if __name__ == "__main__":
    create_synthetic_omics()
