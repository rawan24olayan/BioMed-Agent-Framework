import os
import json
import sys
from datetime import datetime

# Ensure we can import from project root
sys.path.append(os.getcwd())

class BioMedAgent:
    """
    Autonomous Agent that synthesizes Clinical, Molecular, and Literature 
    insights into a structured Medical Memo.
    """
    def __init__(self, discovery_path="data/reports/latest_discovery.json"):
        self.discovery_path = discovery_path
        self.corpus_dir = "data/medical_corpus/"
        self.report_dir = "data/reports/"

    def load_discovery_data(self):
        if not os.path.exists(self.discovery_path):
            print(f"❌ Error: Discovery file {self.discovery_path} not found.")
            return None
        with open(self.discovery_path, "r") as f:
            return json.load(f)

    def generate_memo(self):
        data = self.load_discovery_data()
        if not data: return

        diagnosis = data.get("diagnosis", "Unknown Condition")
        findings = data.get("findings", [])

        # Create the header
        memo = f"============================================================\n"
        memo += f"🤖 BIOMEDICAL AGENT: CLINICAL HYPOTHESIS MEMO\n"
        memo += f"REPORT GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        memo += f"============================================================\n\n"
        
        memo += f"SUBJECT: Molecular Profile Correlation for {diagnosis}\n\n"
        
        memo += "EXECUTIVE SUMMARY:\n"
        memo += f"The system has analyzed the patient's single-cell transcriptomics \n"
        memo += f"against the provided clinical diagnosis and current literature.\n\n"

        memo += "KEY FINDINGS:\n"
        for f in findings:
            gene = f['gene']
            expr = f['mean_expression']
            sources = f['sources']
            
            memo += f"• BIOMARKER: {gene}\n"
            memo += f"  - Expression Level: {expr} (Mean log-normalized)\n"
            
            if sources:
                memo += f"  - Evidence Status: ✅ VALIDATED in {len(sources)} source(s)\n"
                memo += f"  - Primary Source: {sources[0]}\n"
            else:
                memo += f"  - Evidence Status: ⚠️ NO DIRECT MATCH in local corpus\n"
            memo += "\n"

        memo += "REASONING & NEXT STEPS:\n"
        validated_genes = [f['gene'] for f in findings if f['sources']]
        if validated_genes:
            memo += f"The significant activity of {', '.join(validated_genes)} \n"
            memo += "suggests a high correlation with established literature for this condition.\n"
            memo += "Recommended Action: Review pathway-specific inhibitors in clinical trials.\n"
        else:
            memo += "No direct literature correlation found. Recommend broader PubMed mining.\n"

        # Print to console
        print(memo)

        # Save to file
        output_path = os.path.join(self.report_dir, "clinical_memo.txt")
        with open(output_path, "w") as out:
            out.write(memo)
        print(f"✅ FINAL MEMO SAVED TO: {output_path}")

if __name__ == "__main__":
    agent = BioMedAgent()
    agent.generate_memo()
