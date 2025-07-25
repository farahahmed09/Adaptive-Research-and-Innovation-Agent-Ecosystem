# agents/research_agent.py

from utils.external_api_client import NewsApiClient # Import our NewsAPI client
import asyncio # For running async operations if needed for testing

class ResearchAgent:
    """
    The Research Agent is responsible for continuously fetching raw data
    from external sources and performing initial preprocessing.
    """
    def __init__(self, news_api_key: str):
        # Initialize the NewsAPI client with the provided key
        self.news_client = NewsApiClient(news_api_key)
        print("Research Agent initialized.")

    async def gather_and_preprocess_data(self, query: str = "AI trends", count: int = 5):
        """
        Gathers raw data using the NewsAPI client and performs basic preprocessing.

        Args:
            query (str): The research topic/query.
            count (int): The number of articles to fetch.

        Returns:
            list: A list of dictionaries, each representing a preprocessed article.
                  Returns an empty list if no data is found or an error occurs.
        """
        print(f"Research Agent: Gathering and preprocessing data for query '{query}' (count: {count})...")

        # Fetch raw articles using the external API client
        raw_articles = await self.news_client.fetch_top_headlines(query=query, page_size=count)

        processed_data = []
        if raw_articles:
            for article in raw_articles:
                # Basic preprocessing: extract relevant fields and clean up
                title = article.get('title')
                description = article.get('description')
                content = article.get('content') # Full content (often truncated by NewsAPI free tier)
                url = article.get('url')
                published_at = article.get('publishedAt')

                # Simple filtering: only include articles with a title and description
                if title and description:
                    processed_data.append({
                        "title": title,
                        "summary": description, # Renamed to summary for clarity
                        "full_text_snippet": content, # A snippet of the full text
                        "source_url": url,
                        "published_date": published_at,
                        # Add more preprocessing like removing HTML tags,
                        # lowercasing, tokenization here later.
                    })

        print(f"Research Agent: Finished processing. Found {len(processed_data)} relevant entries.")
        return processed_data

# Example usage for testing the agent directly (optional)
if __name__ == "__main__":
    import asyncio
    from config import NEWS_API_KEY

    async def test_agent():
        if NEWS_API_KEY:
            agent = ResearchAgent(NEWS_API_KEY)
            data = await agent.gather_and_preprocess_data(query="generative AI breakthroughs", count=2)
            for i, item in enumerate(data):
                print(f"\n--- Processed Item {i+1} ---")
                print(f"Title: {item.get('title')}")
                print(f"Summary: {item.get('summary')[:100]}...") # Print first 100 chars
        else:
            print("NEWS_API_KEY not found in .env. Cannot test Research Agent.")

    asyncio.run(test_agent())