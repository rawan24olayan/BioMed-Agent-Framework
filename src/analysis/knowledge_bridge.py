import os
import sys
import scanpy as sc
import argparse

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.ingestion.ehr_parser import parse_fhir_bundle

def normalize_medical_term(term):
    """
    Normalizes clinical terms (e.g., 'Alzheimer's disease, unspecified') 
    to a searchable research term (e.g., 'alzheimer').
    """
    # Remove common clinical suffixes and split by commas/spaces
    clean_term = term.lower().replace("disease", "").replace("unspecified", "")
    clean_term = clean_term.split(',')[0].strip().split(' ')[0]
    return clean_term

def get_top_genes_from_omics(omics_path, top_n=5):
    """Automated extraction of high-expression markers from AnnData."""
    if not os.path.exists(omics_path):
        return []
    adata = sc.read_h5ad(omics_path)
    mean_expr = adata.X.mean(axis=0)
    if hasattr(mean_expr, "A1"): 
        mean_expr = mean_expr.A1
    
    top_indices = mean_expr.argsort()[-top_n:][::-1]
    return [adata.var_names[i] for i in top_indices]

def run_knowledge_bridge(genes=None, ehr_path="data/ehr_mock/patient_alpha.json", omics_path="data/raw_omics/sample_alzheimers_cells.h5ad"):
    print("\n" + "="*60)
    print("🧠 BIOMEDICAL KNOWLEDGE BRIDGE (FINAL V1)")
    print("="*60)

    # 1. CLINICAL CONTEXT & NORMALIZATION
    if not os.path.exists(ehr_path):
        print(f"ERROR: EHR file missing at {ehr_path}")
        return
    
    ehr_data = parse_fhir_bundle(ehr_path)
    raw_diagnosis = ehr_data["diagnoses"][0] if ehr_data["diagnoses"] else "Unknown"
    searchable_diagnosis = normalize_medical_term(raw_diagnosis)
    
    # 2. SELECT GENES
    if genes:
        target_genes = [g.strip().upper() for g in genes.split(",")]
        mode = "USER-SPECIFIED HYPOTHESIS"
    else:
        target_genes = get_top_genes_from_omics(omics_path)
        mode = "AUTOMATED DISCOVERY"
    
    print(f"MODE:      {mode}")
    print(f"CLINICAL:  {raw_diagnosis}")
    print(f"SEARCHING: {searchable_diagnosis} + {target_genes}")

    # 3. FUZZY SEARCH LOGIC
    results = {}
    corpus_dir = "data/medical_corpus/"
    if os.path.exists(corpus_dir):
        for gene in target_genes:
            matches = []
            for file in os.listdir(corpus_dir):
                if file.endswith(".txt"):
                    with open(os.path.join(corpus_dir, file), "r") as f:
                        content = f.read().lower()
                        # Match the gene AND the normalized diagnosis
                        if gene.lower() in content and searchable_diagnosis in content:
                            matches.append(file)
            results[gene] = matches

    # 4. FINAL RESULTS TABLE
    print(f"\n{'GENE':<12} | {'LITERATURE EVIDENCE'}")
    print("-" * 40)
    for gene, files in results.items():
        evidence = f"✅ FOUND in {len(files)} docs" if files else "❌ NO MATCH (Check Corpus)"
        print(f"{gene:<12} | {evidence}")

    print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--genes", help="Comma-separated list of genes")
    args = parser.parse_args()
    run_knowledge_bridge(genes=args.genes)
