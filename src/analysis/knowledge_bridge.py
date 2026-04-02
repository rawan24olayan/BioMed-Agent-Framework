import os
import sys
import json
import scanpy as sc
import argparse
from datetime import datetime

# Ensure we can import from src
sys.path.append(os.getcwd())
from src.ingestion.ehr_parser import parse_fhir_bundle

def get_gene_metrics(omics_path, gene_list):
    """Extracts mean expression metrics for specific genes."""
    if not os.path.exists(omics_path): return {}
    adata = sc.read_h5ad(omics_path)
    metrics = {}
    for gene in gene_list:
        if gene in adata.var_names:
            # Calculate mean expression for this specific gene
            val = adata[:, gene].X.mean()
            metrics[gene] = round(float(val), 4)
    return metrics

def run_improved_bridge(genes=None):
    # Paths
    ehr_path = "data/ehr_mock/patient_alpha.json"
    omics_path = "data/raw_omics/sample_alzheimers_cells.h5ad"
    corpus_dir = "data/medical_corpus/"
    report_dir = "data/reports/"
    os.makedirs(report_dir, exist_ok=True)

    # 1. Clinical & Molecular Context
    ehr_data = parse_fhir_bundle(ehr_path)
    raw_dx = ehr_data["diagnoses"][0] if ehr_data["diagnoses"] else "Unknown"
    search_dx = raw_dx.lower().split(',')[0].split(' ')[0] # Fuzzy normalization

    # Determine Gene List
    if genes:
        target_genes = [g.strip().upper() for g in genes.split(",")]
    else:
        # Default to top 3 automated
        adata = sc.read_h5ad(omics_path)
        target_genes = [adata.var_names[i] for i in adata.X.mean(axis=0).argsort()[-3:][::-1]]

    gene_stats = get_gene_metrics(omics_path, target_genes)

    # 2. Evidence Gathering
    findings = []
    for gene in target_genes:
        matches = []
        if os.path.exists(corpus_dir):
            for f in os.listdir(corpus_dir):
                if f.endswith(".txt"):
                    with open(os.path.join(corpus_dir, f), "r") as file:
                        content = file.read().lower()
                        if gene.lower() in content and search_dx in content:
                            matches.append(f)
        
        findings.append({
            "gene": gene,
            "mean_expression": gene_stats.get(gene, 0.0),
            "evidence_count": len(matches),
            "sources": matches
        })

    # 3. IMPROVED CONSOLE OUTPUT
    print(f"\n{'='*70}")
    print(f"🧬 BIOMEDICAL INSIGHTS REPORT | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}")
    print(f"PATIENT DIAGNOSIS: {raw_dx}")
    print(f"SEARCH PARAMETER:  {search_dx}")
    print(f"{'-'*70}")
    print(f"{'GENE':<10} | {'EXPR':<8} | {'EVIDENCE':<12} | {'PRIMARY SOURCE'}")
    print(f"{'-'*70}")
    
    for f in findings:
        source = f["sources"][0] if f["sources"] else "N/A"
        print(f"{f['gene']:<10} | {f['mean_expression']:<8} | {f['evidence_count']:<12} | {source}")

    # 4. EXPORT JSON REPORT
    report_path = os.path.join(report_dir, "latest_discovery.json")
    with open(report_path, "w") as jf:
        json.dump({"diagnosis": raw_dx, "findings": findings}, jf, indent=4)
    
    print(f"{'-'*70}")
    print(f"📝 Full discovery report saved to: {report_path}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--genes", help="Comma-separated genes")
    args = parser.parse_args()
    run_improved_bridge(genes=args.genes)
