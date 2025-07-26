# agents/research_agent.py

from utils.external_api_client import NewsApiClient, ArxivClient, GNewsClient
import asyncio
import random 
import time 
from config import GNEWS_API_KEY 

class ResearchAgent:
    """
    The Research Agent is responsible for continuously fetching raw data
    from external sources and performing initial preprocessing.
    """
    def __init__(self, news_api_key: str):
        # Initialize all external API clients
        self.news_client = NewsApiClient(news_api_key)
        self.arxiv_client = ArxivClient()
        self.gnews_client = GNewsClient(GNEWS_API_KEY) # NEW: Initialize GNewsClient with GNEWS_API_KEY
        print("Research Agent initialized with data sources (NewsAPI, ArXiv, GNews).") # UPDATED message

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
        
        # Distribute remaining count among the other 2 sources (ArXiv, GNews)
        other_sources_individual_count = max(1, min(remaining_total_count // 2, 5)) # Now 2 other sources
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

        # --- Fetch from ArXiv (with robustness) ---
        try:
            arxiv_data = await self.arxiv_client.search_articles(query=query, limit=other_sources_individual_count)
            all_processed_data.extend(arxiv_data)
            print(f"  - Fetched {len(arxiv_data)} items from ArXiv (requested {other_sources_individual_count}).")
        except Exception as e:
            print(f"ERROR: ArXiv fetch failed for query '{query}': {e}")
            pass
        await asyncio.sleep(random.uniform(0.5, 1.5)) # Small delay

        # --- Fetch from GNews API (ADDED with robustness) ---
        try:
            gnews_data = await self.gnews_client.search_articles(query=query, page_size=other_sources_individual_count) # Use calculated count
            all_processed_data.extend(gnews_data)
            print(f"  - Fetched {len(gnews_data)} items from GNews API (requested {other_sources_individual_count}).")
        except Exception as e:
            print(f"ERROR: GNews API fetch failed for query '{query}': {e}")
            pass
        await asyncio.sleep(random.uniform(0.5, 1.5)) # Small delay

        print(f"Research Agent: Finished gathering. Total {len(all_processed_data)} combined entries.")
        return all_processed_data

