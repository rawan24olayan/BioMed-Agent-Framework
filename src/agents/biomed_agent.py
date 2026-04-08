import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Setup paths relative to this file to avoid issues running from the root
current_dir = Path(__file__).resolve().parent
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path)

class BioMedAgent:
    def __init__(self):
        # We need the key from the .env to talk to Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(f"Missing API key in {env_path}")
            return

        # Switching to flash-lite to keep the quota happy while developing
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Mapping out where our data lives
        project_root = current_dir.parent.parent
        self.discovery_path = project_root / "data" / "reports" / "latest_discovery.json"
        self.report_path = project_root / "data" / "reports" / "ai_reasoning_memo.txt"

    def load_genomic_data(self):
        """Grabs the JSON output from the R pipeline."""
        if self.discovery_path.exists():
            with open(self.discovery_path, 'r') as f:
                return json.load(f)
        return None

    def safe_generate(self, prompt):
        """
        Wrapping the API call to handle rate limits gracefully.
        Free tier is picky, so we'll wait a bit if we hit a wall.
        """
        try:
            time.sleep(2) 
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                print("Quota limit reached. Taking a 15s breather...")
                time.sleep(15)
                return self.model.generate_content(prompt).text
            print(f"API Error: {e}")
            return "Generation failed."

    def synthesize_reasoning(self, discovery_data):
        """
        Runs a multi-step check to catch hallucinations before saving.
        First we draft, then we review, then we clean it up.
        """
        gene = discovery_data.get("gene", "Unknown")
        condition = discovery_data.get("condition", "Unknown")
        jaccard = discovery_data.get("jaccard_score", "N/A")
        p_val = discovery_data.get("p_value", "N/A")
        
        # Phase 1: The initial take on the data
        print(f"🧬 Analyzing {gene} for {condition}...")
        draft_prompt = (
            f"Write a clinical memo for {gene} in {condition}. "
            f"Statistical context: Jaccard={jaccard}, p-value={p_val}."
        )
        initial_draft = self.safe_generate(draft_prompt)
        
        # Phase 2: Double-checking for scientific nonsense
        print("🔍 Reviewing for technical accuracy...")
        critique_prompt = f"Review this for biological errors or missing context: {initial_draft}"
        critique = self.safe_generate(critique_prompt)
        
        # Phase 3: Merging the draft and the feedback
        print("🖋️ Finalizing report...")
        final_prompt = (
            f"Refine this draft: {initial_draft} \n\n"
            f"Based on this critique: {critique} \n\n"
            "Make sure the final version is polished and biologically sound."
        )
        final_memo = self.safe_generate(final_prompt)
        
        return initial_draft, critique, final_memo

    def run(self):
        """Main entry point to process the data and save the result."""
        data = self.load_genomic_data()
        if not data:
            print(f"No data found at {self.discovery_path}")
            return

        draft, critique, final = self.synthesize_reasoning(data)

        # Ensure the output folder exists before writing
        os.makedirs(self.report_path.parent, exist_ok=True)
        with open(self.report_path, 'w') as f:
            f.write(final)
        
        print(f"✅ Success! Report saved to {self.report_path.name}")
        return draft, critique, final

if __name__ == "__main__":
    agent = BioMedAgent()
    if hasattr(agent, 'model'):
        agent.run()