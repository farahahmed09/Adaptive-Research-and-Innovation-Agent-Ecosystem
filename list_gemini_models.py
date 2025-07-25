# list_gemini_models.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env. Please set it.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Configured Gemini API key. Listing available models...")

    try:
        print("\n--- Available Gemini Models ---")
        for m in genai.list_models():
            # Filter for models that support text generation (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"Name: {m.name}")
                print(f"  Description: {m.description}")
                print(f"  Supported methods: {m.supported_generation_methods}")
                print("-" * 30)
        print("------------------------------")
    except Exception as e:
        print(f"An error occurred while listing models: {e}")
        print("Please ensure your GEMINI_API_KEY is correct and has the necessary permissions.")