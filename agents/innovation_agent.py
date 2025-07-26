# agents/innovation_agent.py

import google.generativeai as genai
import json
import datetime
import asyncio
import sys
import os

class InnovationAgent:
    """
    The Innovation Agent integrates insights from the Analysis Agent,
    dynamically generates research ideas or improvement proposals,
    and generates reports in Markdown format.
    """
    def __init__(self, gemini_api_key: str):
        if not gemini_api_key:
            print("ERROR: Gemini API key is missing for Innovation Agent initialization.")
            self.model = None
        else:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash') # Using 'gemini-2.5-flash' for stability
            print("Innovation Agent initialized with Gemini client.")

    async def generate_ideas_from_insights(self, insights: list, creativity_level: str = "medium"):
        print(f"Innovation Agent: Generating ideas from {len(insights)} insights with {creativity_level} creativity...")

        if not self.model:
            print("Innovation Agent: Gemini model not initialized due to missing API key. Cannot generate ideas.")
            return []

        if not insights:
            print("Innovation Agent: No insights provided for idea generation.")
            return []

        insights_text = json.dumps(insights, indent=2)

        temperature = 0.7
        if creativity_level == "low":
            temperature = 0.3
        elif creativity_level == "high":
            temperature = 1.0

        try:
            prompt_parts = [
                {"role": "user", "parts": [
                    "You are an expert innovation specialist. Your task is to generate concise, actionable research ideas or improvement proposals based on provided market and trend analysis insights. Focus on novelty and feasibility."
                    "\n\nHere are the latest analysis insights:\n"
                    f"{insights_text}\n\n"
                    "Based on these insights, generate 7 to 10 distinct and innovative research ideas or improvement proposals. For each idea, provide a 'title', a 'brief_description', and 'potential_impact'. Format your response as a JSON array of objects."
                    "\n\nExample desired JSON format:\n"
                    "[\n  {\n    \"title\": \"Example Title\",\n    \"brief_description\": \"Example description for the idea.\",\n    \"potential_impact\": \"Example assessment of the idea's impact.\"\n  }\n]"
                ]}
            ]
            
            response = await self.model.generate_content_async(
                prompt_parts,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )

            generated_content = response.text
            print(f"Innovation Agent: Raw generated content: {generated_content[:200]}...")

            if generated_content.strip().startswith('```json') and generated_content.strip().endswith('```'):
                generated_content = generated_content.strip()[7:-3].strip()

            ideas = json.loads(generated_content)

            if not isinstance(ideas, list):
                print("WARNING: LLM did not return a list. Trying to extract from a potential outer object.")
                if isinstance(ideas, dict) and "ideas" in ideas:
                    ideas = ideas["ideas"]
                else:
                    ideas = []

            print(f"Innovation Agent: Generated {len(ideas)} ideas.")
            return ideas

        except Exception as e:
            print(f"An error occurred during Gemini idea generation: {e}")
            return []

    async def generate_markdown_report(self, ideas: list, query: str):
        """
        Generates a Markdown formatted report based on the generated ideas.
        FIXED: This method now correctly formats each idea, not just pasting the list.
        """
        print("Innovation Agent: Generating Markdown report...")
        
        current_time = await asyncio.to_thread(lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        report_content = f"# Research & Innovation Report for: '{query}'\n\n"
        report_content += f"**Date:** {current_time}\n\n"
        report_content += "--- \n\n"

        if not ideas:
            report_content += "No innovative ideas or proposals were generated based on the current analysis.\n"
            return report_content

        report_content += "## Generated Ideas & Proposals:\n\n"

        # FIX STARTS HERE: Iterate and format each idea correctly
        for i, idea in enumerate(ideas):
            report_content += f"### {i+1}. {idea.get('title', 'Untitled Idea')}\n"
            report_content += f"**Description:** {idea.get('brief_description', 'No description provided.')}\n\n"
            report_content += f"**Potential Impact:** {idea.get('potential_impact', 'No impact assessment provided.')}\n\n"
            report_content += "---\n\n"
        # FIX ENDS HERE

        report_content += "## Next Steps:\n"
        report_content += "- Further validation and feasibility studies for promising ideas.\n"
        report_content += "- Detailed market research.\n"
        report_content += "- Exploration of required resources and technologies.\n"
        report_content += "\n*This report was generated by the Innovation Agent.*"

        print("Innovation Agent: Markdown report generated.")
        return report_content

# Example usage for testing this agent directly (optional)
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from config import GEMINI_API_KEY

    async def test_agent():
        if not GEMINI_API_KEY:
            print("GEMINI_API_KEY not found in .env. Cannot test Innovation Agent.")
            return

        dummy_insights = [
            {"source_title": "AI in Medical Imaging", "insight_summary": "Deep learning models show promise in early cancer detection, but require large, diverse datasets."},
            {"source_title": "Quantum Computing Breakthrough", "insight_summary": "New qubit stability achieved, pushing quantum computing closer to practical applications, but cooling remains an issue."},
            {"source_title": "Sustainable Energy Storage", "insight_summary": "Novel solid-state battery technology offers high energy density and faster charging for EVs and grid storage, but manufacturing is complex."}
        ]
        
        agent = InnovationAgent(GEMINI_API_KEY)
        ideas = await agent.generate_ideas_from_insights(dummy_insights, creativity_level="high")
        
        if ideas:
            print("\n--- Generated Ideas ---")
            for idea in ideas:
                print(f"Title: {idea.get('title')}")
                print(f"Description: {idea.get('brief_description')}")
                print(f"Impact: {idea.get('potential_impact')}\n")
            
            report = await agent.generate_markdown_report(ideas, "AI, Quantum, and Energy Innovation")
            print("\n--- Generated Markdown Report ---")
            print(report)
        else:
            print("No ideas generated.")

    asyncio.run(test_agent())