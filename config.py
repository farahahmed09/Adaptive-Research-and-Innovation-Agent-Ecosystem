# config.py

from dotenv import load_dotenv # Import function to load .env file
import os # Import os module to access environment variables

# Load environment variables from a .env file if it exists.
load_dotenv()

# Retrieve API keys from environment variables.
# os.getenv() safely gets the variable; it returns None if not found.
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Other configuration variables can go here
# e.g., DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_database.db")