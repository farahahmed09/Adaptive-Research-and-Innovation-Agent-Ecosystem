# config.py

from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Ensure this is your Gemini key
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY") # NEW: GNews API key (commented out as per only NewsAPI+ArXiv)

# Constants for API URLs
ARXIV_API_BASE_URL = "http://export.arxiv.org/api/query"

