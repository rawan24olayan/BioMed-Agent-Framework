import os
import sys
import scanpy as sc
import argparse

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.ingestion.ehr_parser import parse_fhir_bundle

def get_top_genes_from_omics(omics_path, top_n=5):
    """Automated extraction of high-expression markers from AnnData."""
    if not os.path.exists(omics_path):
        return []
    adata = sc.read_h5ad(omics_path)
    # Calculate mean expression across all cells
    mean_expr = adata.X.mean(axis=0)
    # Handle both numpy arrays and matrices (common in scanpy)
    if hasattr(mean_expr, "A1"): 
        mean_expr = mean_expr.A1
    
    top_indices = mean_expr.argsort()[-top_n:][::-1]
    return [adata.var_names[i] for i in top_indices]

def run_flexible_bridge(genes=None, ehr_path="data/ehr_mock/patient_alpha.json", omics_path="data/raw_omics/sample_alzheimers_cells.h5ad"):
    print("\n" + "="*60)
    print("🎯 TARGETED BIOMEDICAL KNOWLEDGE BRIDGE")
    print("="*60)

    # 1. CLINICAL CONTEXT
    if not os.path.exists(ehr_path):
        print(f"ERROR: EHR file not found at {ehr_path}")
        return
    
    ehr_data = parse_fhir_bundle(ehr_path)
    diagnosis = ehr_data["diagnoses"][0] if ehr_data["diagnoses"] else "Unknown"
    
    # 2. SELECT GENES (User Specified OR Automated)
    if genes:
        target_genes = [g.strip().upper() for g in genes.split(",")]
        print(f"MODE: USER-SPECIFIED HYPOTHESIS")
    else:
        target_genes = get_top_genes_from_omics(omics_path)
        print(f"MODE: AUTOMATED DISCOVERY")
    
    print(f"Diagnosis: {diagnosis}")
    print(f"Genes to Analyze: {', '.join(target_genes)}")

    # 3. SEARCH LOGIC
    results = {}
    corpus_dir = "data/medical_corpus/"
    if os.path.exists(corpus_dir):
        for gene in target_genes:
            matches = []
            for file in os.listdir(corpus_dir):
                if file.endswith(".txt"):
                    with open(os.path.join(corpus_dir, file), "r") as f:
                        content = f.read().lower()
                        if gene.lower() in content and diagnosis.lower() in content:
                            matches.append(file)
            results[gene] = matches

    # 4. RESULTS TABLE
    print(f"\n{'GENE':<12} | {'LITERATURE EVIDENCE'}")
    print("-" * 40)
    for gene, files in results.items():
        evidence = f"✅ FOUND in {len(files)} docs" if files else "❌ NO MATCH"
        print(f"{gene:<12} | {evidence}")

    print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--genes", help="Comma-separated list of genes to search (e.g. TREM2,APOE)")
    args = parser.parse_args()
    
    run_flexible_bridge(genes=args.genes)

