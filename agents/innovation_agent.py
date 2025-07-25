# agents/innovation_agent.py

import google.generativeai as genai # CHANGED: Import Gemini SDK instead of openai
import json # For handling JSON data
import datetime # For current date in report (synchronous call, will wrap for async)
import asyncio # For asyncio.to_thread in report
import sys # NEW: For direct testing setup
import os # NEW: For direct testing setup

class InnovationAgent:
    """
    The Innovation Agent integrates insights from the Analysis Agent,
    dynamically generates research ideas or improvement proposals,
    and generates reports in Markdown format.
    """
    def __init__(self, gemini_api_key: str): # CHANGED: Takes gemini_api_key as input
        # Initialize the Gemini client/model
        # It's important to ensure gemini_api_key is not None before passing
        """
        Initializes the Innovation Agent with a Gemini client.

        Args:
            gemini_api_key (str): The API key for the Gemini client.
        """
        if not gemini_api_key:
            print("ERROR: Gemini API key is missing for Innovation Agent initialization.") # CHANGED message
            self.model = None # CHANGED: Set model to None
        else:
            genai.configure(api_key=gemini_api_key) # CHANGED: Configure the Gemini API key
            # Get the GenerativeModel instance. 'gemini-2.0-flash' is a good general-purpose model.
            self.model = genai.GenerativeModel('gemini-2.0-flash') # CHANGED: Initialize Gemini Model
            print("Innovation Agent initialized with Gemini client.") # CHANGED message

    async def generate_ideas_from_insights(self, insights: list, creativity_level: str = "medium"):
        """
        Generates research ideas or proposals based on the provided insights using a Gen AI model.

        Args:
            insights (list): A list of insights (dictionaries) from the Analysis Agent.
            creativity_level (str): Controls the creativity of ideas (e.g., "low", "medium", "high").

        Returns:
            list: A list of generated ideas (dictionaries).
        """
        print(f"Innovation Agent: Generating ideas from {len(insights)} insights with {creativity_level} creativity...")

        if not self.model: # CHANGED: Check self.model for availability
            print("Innovation Agent: Gemini model not initialized due to missing API key. Cannot generate ideas.") # CHANGED message
            return []

        if not insights:
            print("Innovation Agent: No insights provided for idea generation.")
            return []

        # Prepare insights for the LLM
        insights_text = json.dumps(insights, indent=2) # Convert insights list to a formatted JSON string

        # --- Prompt Engineering for Generative AI ---
        # This is CRUCIAL. The quality of ideas depends on how well you phrase the prompt.
        # We'll adjust 'temperature' based on creativity_level.
        temperature = 0.7 # Default medium creativity
        if creativity_level == "low":
            temperature = 0.3
        elif creativity_level == "high":
            temperature = 1.0

        try:
            # CHANGED: Use Gemini's generate_content_async API
            # Gemini's prompt structure is typically a list of dicts with 'role' and 'parts'.
            # We explicitly ask for JSON output and provide an example format.
            prompt_parts = [
                {"role": "user", "parts": [
                    "You are an expert innovation specialist. Your task is to generate concise, actionable research ideas or improvement proposals based on provided market and trend analysis insights. Focus on novelty and feasibility."
                    "\n\nHere are the latest analysis insights:\n"
                    f"{insights_text}\n\n"
                    "Based on these insights, generate 3-5 distinct and innovative research ideas or improvement proposals. For each idea, provide a 'title', a 'brief_description', and 'potential_impact'. Format your response as a JSON array of objects."
                    "\n\nExample desired JSON format:\n"
                    "[\n  {\n    \"title\": \"Example Title\",\n    \"brief_description\": \"Example description for the idea.\",\n    \"potential_impact\": \"Example assessment of the idea's impact.\"\n  }\n]"
                ]}
            ]
            
            response = await self.model.generate_content_async( # CHANGED: Gemini API call
                prompt_parts, # Pass the structured prompt
                generation_config=genai.types.GenerationConfig(temperature=temperature) # Configure temperature
            )

            # Extract the generated content
            # Gemini's response.text directly gives the generated string
            generated_content = response.text
            print(f"Innovation Agent: Raw generated content: {generated_content[:200]}...") # Log snippet

            # Attempt to parse the JSON output from the model
            # Gemini models might also sometimes enclose JSON in ```json ... ``` blocks
            if generated_content.strip().startswith('```json') and generated_content.strip().endswith('```'):
                generated_content = generated_content.strip()[7:-3].strip() # Remove code block fence

            ideas = json.loads(generated_content)

            # Basic validation: ensure it's a list and contains required keys
            if not isinstance(ideas, list):
                print("WARNING: LLM did not return a list. Trying to extract from a potential outer object.")
                if isinstance(ideas, dict) and "ideas" in ideas:
                    ideas = ideas["ideas"]
                else:
                    ideas = [] # Fallback to empty list

            print(f"Innovation Agent: Generated {len(ideas)} ideas.")
            return ideas

        except Exception as e: # CHANGED: Catch a more general Exception for Gemini errors (was openai.APIStatusError)
            print(f"An error occurred during Gemini idea generation: {e}") # CHANGED message
            # You can try to print more details from the response if available
            # if 'response' in locals() and hasattr(response, 'candidates'):
            #     print(f"Gemini candidates: {response.candidates}")
            return []

    async def generate_markdown_report(self, ideas: list, query: str):
        """
        Generates a Markdown formatted report based on the generated ideas.
        (This method remains the same as it does not interact with the LLM)
        """
        print("Innovation Agent: Generating Markdown report...")
        
        # Get current time for the report (using asyncio.to_thread for synchronous datetime.now())
        current_time = await asyncio.to_thread(lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        report_content = f"# Research & Innovation Report for: '{query}'\n\n"
        report_content += f"**Date:** {current_time}\n\n"
        report_content += "--- \n\n"

        if not ideas:
            report_content += "No innovative ideas or proposals were generated based on the current analysis.\n"
            return report_content

        report_content += "## Generated Ideas & Proposals:\n\n"

        for i, idea in enumerate(ideas):
            report_content += f"### {i+1}. {idea.get('title', 'Untitled Idea')}\n"
            report_content += f"**Description:** {idea.get('brief_description', 'No description provided.')}\n\n"
            report_content += f"**Potential Impact:** {idea.get('potential_impact', 'No impact assessment provided.')}\n\n"
            report_content += "---\n\n"

        report_content += "## Next Steps:\n"
        report_content += "- Further validation and feasibility studies for promising ideas.\n"
        report_content += "- Detailed market research.\n"
        report_content += "- Exploration of required resources and technologies.\n"
        report_content += "\n*This report was generated by the Innovation Agent.*"

        print("Innovation Agent: Markdown report generated.")
        return report_content

# Example usage for testing this agent directly (optional)
if __name__ == "__main__":
    # Add these lines for direct testing of the module
    # This allows importing modules from the project root like 'config'
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from config import GEMINI_API_KEY # CHANGED: Import GEMINI_API_KEY for testing

    async def test_agent():
        if not GEMINI_API_KEY:
            print("GEMINI_API_KEY not found in .env. Cannot test Innovation Agent.") # CHANGED message
            return

        # Dummy insights data (simulating output from Analysis Agent)
        dummy_insights = [
            {"source_title": "AI in Medical Imaging", "insight_summary": "Deep learning models show promise in early cancer detection, but require large, diverse datasets."},
            {"source_title": "Quantum Computing Breakthrough", "insight_summary": "New qubit stability achieved, pushing quantum computing closer to practical applications, but cooling remains an issue."},
            {"source_title": "Sustainable Energy Storage", "insight_summary": "Novel solid-state battery technology offers high energy density and faster charging for EVs and grid storage, but manufacturing is complex."}
        ]
        
        agent = InnovationAgent(GEMINI_API_KEY) # CHANGED: Pass GEMINI_API_KEY to constructor
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