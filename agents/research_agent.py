# agents/research_agent.py

# UPDATED: Import NewsApiClient and ArxivClient ONLY
from utils.external_api_client import NewsApiClient, ArxivClient
import asyncio
import random # For simple delay
import time # For simple delay

class ResearchAgent:
    """
    The Research Agent is responsible for continuously fetching raw data
    from external sources and performing initial preprocessing.
    """
    def __init__(self, news_api_key: str):
        self.news_client = NewsApiClient(news_api_key)
        self.arxiv_client = ArxivClient() # NEW: Initialize ArxivClient
        print("Research Agent initialized with data sources (NewsAPI, ArXiv).") # UPDATED message

    async def gather_and_preprocess_data(self, query: str = "AI trends", count: int = 5):
        """
        Gathers raw data from multiple sources and performs basic preprocessing.

        Args:
            query (str): The research topic/query.
            count (int): The target number of articles/items to fetch overall (approx evenly distributed).

        Returns:
            list: A list of dictionaries, each representing a preprocessed data point.
        """
        print(f"Research Agent: Gathering and preprocessing data for query '{query}' from multiple sources...")
        all_processed_data = []

        # --- Logic for Fetch Counts (prioritizing NewsAPI) ---
        news_api_target_count = 5 # We specifically want 5 from NewsAPI

        remaining_total_count = max(0, count - news_api_target_count)
        
        # Distribute remaining count among the other 1 source (ArXiv)
        # Ensure at least 1 item for ArXiv if remaining_total_count allows, max 5
        arxiv_individual_count = max(1, min(remaining_total_count, 5)) # Only one other source
        # --- END Logic ---

        # --- Fetch from NewsAPI (with fixed count and robustness) ---
        try:
            news_data = await self.news_client.fetch_top_headlines(query=query, page_size=news_api_target_count)
            all_processed_data.extend(news_data)
            print(f"  - Fetched {len(news_data)} items from NewsAPI (requested {news_api_target_count}).")
        except Exception as e:
            print(f"ERROR: NewsAPI fetch failed for query '{query}': {e}")
            pass # Continue if this source fails
        await asyncio.sleep(random.uniform(0.5, 1.5)) # Small delay

        # --- Fetch from ArXiv (ADDED with robustness) ---
        try:
            arxiv_data = await self.arxiv_client.search_articles(query=query, limit=arxiv_individual_count)
            all_processed_data.extend(arxiv_data)
            print(f"  - Fetched {len(arxiv_data)} items from ArXiv (requested {arxiv_individual_count}).")
        except Exception as e:
            print(f"ERROR: ArXiv fetch failed for query '{query}': {e}")
            pass
        await asyncio.sleep(random.uniform(0.5, 1.5)) # Small delay

        print(f"Research Agent: Finished gathering. Total {len(all_processed_data)} combined entries.")
        return all_processed_data

# Example usage for testing the agent directly (optional)
if __name__ == "__main__":
    import asyncio
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from config import NEWS_API_KEY # Only NEWS_API_KEY needed for this version

    async def test_agent():
        if NEWS_API_KEY:
            agent = ResearchAgent(NEWS_API_KEY)
            # Test query relevant for both sources
            data = await agent.gather_and_preprocess_data(query="artificial intelligence in medicine", count=10)
            for i, item in enumerate(data):
                print(f"\n--- Processed Item {i+1} ---")
                print(f"Source: {item.get('source', 'N/A')}")
                print(f"Title: {item.get('title', 'N/A')}")
                print(f"Summary: {item.get('summary', 'N/A')[:100]}...")
                print(f"URL: {item.get('url', 'N/A')}")
        else:
            print("NEWS_API_KEY not found in .env. Cannot test Research Agent fully.")

    asyncio.run(test_agent())