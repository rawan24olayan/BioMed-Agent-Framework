import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# --- 1. CONFIGURATION & PATHS ---
# Ensures the script finds the .env file even if run from different folders
current_dir = Path(__file__).resolve().parent
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path)

class BioMedAgent:
    def __init__(self):
        # API Key Setup
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(f"❌ ERROR: GOOGLE_API_KEY not found at {env_path}")
            return

        # Initialize the 2026-standard model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Absolute path resolution for the BioMed-Agent-Framework structure
        project_root = current_dir.parent.parent
        self.discovery_path = project_root / "data" / "reports" / "latest_discovery.json"
        self.report_path = project_root / "data" / "reports" / "ai_reasoning_memo.txt"

    def load_genomic_data(self):
        """Loads discovery data from the pipeline."""
        if self.discovery_path.exists():
            with open(self.discovery_path, 'r') as f:
                return json.load(f)
        return None

    def safe_generate(self, prompt, phase_name):
        """
        Communicates with the LLM with built-in rate-limit protection 
        and error handling. (Key Skill: AI System Resilience)
        """
        try:
            # Respect Free Tier limits with a mandatory pause
            time.sleep(2) 
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⏳ Quota hit during {phase_name}. Waiting 15s...")
                time.sleep(15)
                # One recursive retry
                return self.model.generate_content(prompt).text
            print(f"⚠️ {phase_name} failed: {error_msg}")
            return f"Error occurred during {phase_name}."

    def synthesize_reasoning(self, discovery_data):
        """
        The Agentic 'Critique & Refine' Loop.
        (Key Skill: LLM-based approaches & Hallucination Mitigation)
        """
        gene = discovery_data.get("gene", "Unknown")
        condition = discovery_data.get("condition", "Unknown")
        
        # --- PHASE 1: DRAFTING ---
        print("🧬 [PHASE 1] Generating initial reasoning...")
        draft_prompt = f"As a bioinformatician, draft a clinical reasoning memo for {gene} in {condition}."
        initial_draft = self.safe_generate(draft_prompt, "Drafting")
        
        # --- PHASE 2: CRITIQUING ---
        print("🔍 [PHASE 2] Identifying potential scientific errors...")
        critique_prompt = f"""
        Role: Scientific Peer Reviewer
        Analyze this memo for biological accuracy regarding {gene}:
        {initial_draft}
        
        Point out errors or missing pathway context.
        """
        critique = self.safe_generate(critique_prompt, "Critique")
        
        # --- PHASE 3: FINALIZING ---
        print("🖋️ [PHASE 3] Refining final memo...")
        final_prompt = f"""
        Original Draft: {initial_draft}
        Critique: {critique}
        
        Task: Create a final, verified memo that fixes the errors identified in the critique.
        """
        final_memo = self.safe_generate(final_prompt, "Finalization")
        
        return initial_draft, critique, final_memo

    def run(self):
        """Executes the full agent workflow."""
        data = self.load_genomic_data()
        if not data:
            print(f"⚠️ No discovery data found at {self.discovery_path}")
            return

        # Run the reasoning loop
        draft, critique, final = self.synthesize_reasoning(data)

        # Save the final product
        os.makedirs(self.report_path.parent, exist_ok=True)
        with open(self.report_path, 'w') as f:
            f.write(final)
        
        print(f"✅ Success! Verified memo saved to: {self.report_path}")
        return draft, critique, final

if __name__ == "__main__":
    agent = BioMedAgent()
    # Check if model was initialized before running
    if hasattr(agent, 'model'):
        agent.run()