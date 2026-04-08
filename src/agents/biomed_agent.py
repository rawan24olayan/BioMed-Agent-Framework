import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from Bio import Entrez  # pip install biopython

# Locate the environment file to manage API keys securely
current_dir = Path(__file__).resolve().parent
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path)

class BioMedAgent:
    def __init__(self):
        # We need the Google key for the LLM and an email for the PubMed API
        api_key = os.getenv("GOOGLE_API_KEY")
        Entrez.email = os.getenv("EMAIL_ADDRESS", "researcher@example.com")
        
        if not api_key:
            print("Configuration Error: GOOGLE_API_KEY not found.")
            return

        # Using 2.5-flash-lite to maximize our request quota
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Mapping the file structure for the R-to-Python pipeline
        project_root = current_dir.parent.parent
        self.discovery_path = project_root / "data" / "reports" / "latest_discovery.json"
        self.report_path = project_root / "data" / "reports" / "ai_reasoning_memo.txt"

    def fetch_literature_context(self, gene, condition):
        """
        Queries PubMed to find the most recent evidence. 
        This prevents the model from relying solely on its training data.
        """
        try:
            search_query = f"{gene} AND {condition}"
            handle = Entrez.esearch(db="pubmed", term=search_query, retmax=3)
            record = Entrez.read(handle)
            handle.close()

            if not record["IdList"]:
                return "No specific literature found on PubMed."

            summary_handle = Entrez.esummary(db="pubmed", id=",".join(record["IdList"]))
            summaries = Entrez.read(summary_handle)
            summary_handle.close()

            return " | ".join([s['Title'] for s in summaries])
        except Exception:
            return "Literature search currently unavailable."

    def safe_generate(self, prompt):
        """
        Manages the digital handshake with the LLM. 
        Includes a cooldown to respect the free tier rate limits.
        """
        try:
            time.sleep(2) 
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e).lower():
                print("Quota limit reached. Pausing for 15 seconds...")
                time.sleep(15)
                return self.model.generate_content(prompt).text
            return f"Error: {e}"

    def synthesize_reasoning(self, discovery_data):
        """
        The core engine. It bridges the R-stats with live research 
        and performs a self-critique to minimize hallucinations.
        """
        gene = discovery_data.get("gene", "Unknown")
        condition = discovery_data.get("condition", "Unknown")
        jaccard = discovery_data.get("jaccard_score", "N/A")
        
        # Step 1: Gather context
        print(f"🧬 Analyzing {gene} for {condition}...")
        papers = self.fetch_literature_context(gene, condition)
        
        # Phase 1: The initial draft
        draft_prompt = (
            f"Draft a clinical memo for {gene} in {condition}. "
            f"Evidence: Jaccard overlap={jaccard}. "
            f"Recent Titles: {papers}"
        )
        draft = self.safe_generate(draft_prompt)
        
        # Phase 2: The peer-review check
        print("🔍 Reviewing for scientific consistency...")
        critique = self.safe_generate(f"Critique this memo for biological errors: {draft}")
        
        # Phase 3: The final refinement
        print("🖋️ Finalizing reasoning memo...")
        final_prompt = (
            f"Original: {draft}\nFeedback: {critique}\n"
            "Produce a final version that incorporates the feedback and is ready for clinical review."
        )
        final_memo = self.safe_generate(final_prompt)
        
        return final_memo

    def run(self):
        """Orchestrates the data loading, processing, and saving."""
        if not self.discovery_path.exists():
            print(f"Data source missing: {self.discovery_path}")
            return

        with open(self.discovery_path, 'r') as f:
            data = json.load(f)

        memo = self.synthesize_reasoning(data)

        # Write the final result to the report folder
        os.makedirs(self.report_path.parent, exist_ok=True)
        with open(self.report_path, 'w') as f:
            f.write(memo)
        
        print(f"✅ Process Complete. Results saved to {self.report_path.name}")

if __name__ == "__main__":
    agent = BioMedAgent()
    if hasattr(agent, 'model'):
        agent.run()