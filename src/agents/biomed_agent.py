import time
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# 1. SETUP: Robust path finding for the .env file
# This works whether you run from the root or inside src/agents/
current_dir = Path(__file__).resolve().parent
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path)

class BioMedAgent:
    def __init__(self):
        # 2. CREDENTIALS: Load the key from the environment
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print(f"❌ ERROR: GOOGLE_API_KEY not found in {env_path}")
            return

        # 3. CONFIGURATION: Using Gemini 2.0 Flash for 2026 standards
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # 4. PATHS: Points to your data folders (adjusting for src/agents location)
        self.discovery_path = current_dir.parent.parent / "data/reports/latest_discovery.json"
        self.report_path = current_dir.parent.parent / "data/reports/ai_reasoning_memo.txt"

    def load_genomic_data(self):
        """Reads the gene expression results from your pipeline."""
        if os.path.exists(self.discovery_path):
            with open(self.discovery_path, 'r') as f:
                return json.load(f)
        return None

    def synthesize_reasoning(self, discovery_data):
        """Sends biological context to Gemini to generate a clinical memo."""
        gene = discovery_data.get("gene", "Unknown")
        condition = discovery_data.get("condition", "Unknown")
        
        prompt = f"""
        Role: Bioinformatics Research Lead
        Task: Analyze the connection between GENE: {gene} and CONDITION: {condition}.
        
        Provide a concise clinical reasoning memo explaining the potential 
        mechanism of action and significance in a disease-state manifold.
        """
        
        print(f"🧬 [INFO] Gemini is analyzing {gene} for {condition}...")
        
        # RATE LIMIT PROTECTION: Sleep for 2 seconds before the API call
        time.sleep(2) 
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ AI Analysis failed: {str(e)}"

    def run(self):
        """Execute the agent logic."""
        data = self.load_genomic_data()
        if not data:
            print(f"⚠️ No data found at {self.discovery_path}. Check your pipeline.")
            return

        # Generate the AI reasoning
        reasoning = self.synthesize_reasoning(data)

        # Save the final report
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        with open(self.report_path, 'w') as f:
            f.write(reasoning)
        
        print(f"✅ Success! Memo saved to: {self.report_path}")

if __name__ == "__main__":
    agent = BioMedAgent()
    if hasattr(agent, 'model'):
        agent.run()