# utils/external_api_client.py

import requests # Import the requests library for making HTTP requests

class NewsApiClient:
    """
    Client for interacting with the NewsAPI.org service.
    This handles fetching headlines and basic error checking.
    """
    def __init__(self, api_key: str):
        # The base URL for the NewsAPI endpoints
        self.base_url = "https://newsapi.org/v2/"
        self.api_key = api_key # Store the API key provided during initialization

        # Basic check for API key presence
        if not self.api_key:
            print("WARNING: News API key is missing. NewsApiClient may not function correctly.")

    async def fetch_top_headlines(self, query: str = "technology", language: str = "en", page_size: int = 5):
        """
        Fetches top headlines related to a specific query from NewsAPI.org.

        Args:
            query (str): The keyword to search for (e.g., "AI trends", "renewable energy").
                         NewsAPI uses this for the 'q' parameter in 'everything' endpoint,
                         or as a category hint for 'top-headlines'.
            language (str): The language of the articles (e.g., "en" for English).
            page_size (int): The number of articles to return (max 100 for NewsAPI free tier).

        Returns:
            list: A list of dictionaries, where each dictionary represents an article.
                  Returns an empty list if there's an error or no articles found.
        """
        print(f"NewsApiClient: Fetching headlines for query '{query}'...")
        endpoint = "everything" # Using the 'everything' endpoint for more specific queries

        params = {
            "q": query,           # The search query
            "language": language, # Article language
            "pageSize": page_size,# Number of results
            "apiKey": self.api_key # Your API key
        }

        try:
            # Make the GET request to the NewsAPI
            # We use await requests.get if we were using an async HTTP client like httpx,
            # but 'requests' is synchronous. We'll simulate async for consistency with FastAPI.
            # In a real async app, you'd wrap synchronous calls in run_in_threadpool or use httpx.
            response = requests.get(f"{self.base_url}{endpoint}", params=params)

            # raise_for_status() will raise an HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Check for NewsAPI specific errors
            if data.get("status") == "error":
                print(f"NewsAPI error: {data.get('code')} - {data.get('message')}")
                return []

            # Return the list of articles
            return data.get("articles", [])

        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
            print(f"HTTP error occurred: {http_err} - Response: {response.text}")
            return []
        except requests.exceptions.ConnectionError as conn_err:
            # Handle network-related errors (e.g., no internet connection)
            print(f"Connection error occurred: {conn_err}")
            return []
        except requests.exceptions.Timeout as timeout_err:
            # Handle request timeout errors
            print(f"Timeout error occurred: {timeout_err}")
            return []
        except requests.exceptions.RequestException as req_err:
            # Handle any other general request exceptions
            print(f"An unexpected error occurred: {req_err}")
            return []
        except Exception as e:
            # Catch any other unforeseen errors
            print(f"An unknown error occurred during API call: {e}")
            return []

# Example usage for testing this client directly (optional)
if __name__ == "__main__":
    import asyncio
    from config import NEWS_API_KEY # Ensure config.py can be imported

    async def test_client():
        client = NewsApiClient(NEWS_API_KEY)
        articles = await client.fetch_top_headlines(query="artificial intelligence", page_size=3)
        if articles:
            for i, article in enumerate(articles):
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {article.get('title', 'N/A')}")
                print(f"Source: {article.get('source', {}).get('name', 'N/A')}")
                print(f"Description: {article.get('description', 'N/A')[:100]}...")
        else:
            print("No articles fetched or an error occurred.")

    asyncio.run(test_client())