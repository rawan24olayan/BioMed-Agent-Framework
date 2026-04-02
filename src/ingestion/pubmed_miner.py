import os
from Bio import Entrez

# Harvard JD check: Automating medical journal processing & text datasets
def fetch_pubmed_abstracts(query, max_results=3):
    """
    Search PubMed and download abstracts for the Agent to 'read'.
    """
    # Required by NCBI: Identifies who is making the request
    Entrez.email = "rawan.s.olayan@gmail.com" 
    
    print(f"\n--- SEARCHING PUBMED FOR: {query} ---")
    
    try:
        # 1. Search for PubMed IDs (PMIDs)
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        if not id_list:
            print("No results found.")
            return None
        
        # 2. Fetch the actual abstracts
        handle = Entrez.efetch(db="pubmed", id=id_list, rettype="abstract", retmode="text")
        abstracts = handle.read()
        handle.close()
        
        # 3. Save to our data directory for the Agent
        file_name = f"{query.replace(' ', '_')}_abstracts.txt"
        output_path = os.path.join("data", "medical_corpus", file_name)
        
        with open(output_path, "w") as f:
            f.write(abstracts)
        
        print(f"SUCCESS: Saved {len(id_list)} abstracts to {output_path}")
        return output_path

    except Exception as e:
        print(f"Error fetching from PubMed: {e}")
        return None

if __name__ == "__main__":
    # Test: Searching for biomarkers related to the diagnosis in our EHR
# Example: Searching for a specific gene-disease-drug triad
    # This is exactly how we start 'Target Validation'
    complex_query = '("Alzheimer Disease"[MeSH]) AND (TREM2) AND (Immunotherapy)'
    
    fetch_pubmed_abstracts(complex_query, max_results=5)
