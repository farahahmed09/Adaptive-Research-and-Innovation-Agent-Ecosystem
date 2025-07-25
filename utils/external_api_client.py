# utils/external_api_client.py

import requests
import time # For basic rate limiting/backoff
import random # For simple delay
import xml.etree.ElementTree as ET # NEW: For parsing XML (ArXiv uses Atom feed)

class NewsApiClient:
    """
    Client for interacting with the NewsAPI.org service.
    This handles fetching headlines and basic error checking.
    """
    def __init__(self, api_key: str):
        self.base_url = "https://newsapi.org/v2/"
        self.api_key = api_key
        if not self.api_key:
            print("WARNING: News API key is missing. NewsApiClient may not function correctly.")

    async def fetch_top_headlines(self, query: str = "technology", language: str = "en", page_size: int = 5):
        print(f"NewsApiClient: Fetching headlines for query '{query}'...")
        endpoint = "everything"

        params = {
            "q": query,
            "language": language,
            "pageSize": page_size,
            "apiKey": self.api_key
        }

        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "error":
                print(f"NewsAPI error: {data.get('code')} - {data.get('message')}")
                return []

            articles = data.get("articles", [])
            processed_articles = []
            for article in articles:
                processed_articles.append({
                    "source": "NewsAPI",
                    "title": article.get('title'),
                    "summary": article.get('description'),
                    "content": article.get('content'),
                    "url": article.get('url'),
                    "published_date": article.get('publishedAt'),
                    "authors": article.get('author')
                })
            return processed_articles

        except requests.exceptions.RequestException as e:
            print(f"NewsAPI request error: {e}")
            return []
        except Exception as e:
            print(f"An unknown error occurred during NewsAPI call: {e}")
            return []


# NEW CLIENT: ArXiv API Client (ONLY additional source)
class ArxivClient:
    """
    Client for interacting with the ArXiv API.
    Used for fetching preprints and scholarly articles.
    """
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.ATOM_NAMESPACE = {'atom': 'http://www.w3.org/2005/Atom'}

    async def search_articles(self, query: str, limit: int = 5):
        print(f"ArxivClient: Searching articles for query '{query}'...")
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            articles = []
            for entry in root.findall('atom:entry', self.ATOM_NAMESPACE):
                title = entry.find('atom:title', self.ATOM_NAMESPACE).text if entry.find('atom:title', self.ATOM_NAMESPACE) is not None else None
                summary = entry.find('atom:summary', self.ATOM_NAMESPACE).text if entry.find('atom:summary', self.ATOM_NAMESPACE) is not None else None
                
                url = None
                for link in entry.findall('atom:link', self.ATOM_NAMESPACE):
                    if link.get('title') == 'Original' or link.get('rel') == 'alternate':
                        url = link.get('href')
                        break

                published = entry.find('atom:published', self.ATOM_NAMESPACE).text if entry.find('atom:published', self.ATOM_NAMESPACE) is not None else None
                
                authors = []
                for author_elem in entry.findall('atom:author', self.ATOM_NAMESPACE):
                    name = author_elem.find('atom:name', self.ATOM_NAMESPACE).text
                    if name:
                        authors.append(name)
                
                articles.append({
                    "source": "ArXiv",
                    "title": title.strip() if title else None,
                    "summary": summary.strip() if summary else None,
                    "content": summary.strip() if summary else None,
                    "url": url,
                    "published_date": published,
                    "authors": authors if authors else None
                })
            return articles

        except requests.exceptions.RequestException as e:
            print(f"ArXiv request error: {e}")
            return []
        except ET.ParseError as e:
            print(f"ArXiv XML parse error: {e}")
            return []
        except Exception as e:
            print(f"An unknown error occurred during ArXiv call: {e}")
            return []

# Example usage for testing (Optional - for direct test of this file)
if __name__ == "__main__":
    import asyncio
    from config import NEWS_API_KEY
    
    async def test_clients():
        print("\n--- Testing NewsAPI Client ---")
        news_client = NewsApiClient(NEWS_API_KEY)
        news_articles = await news_client.fetch_top_headlines(query="AI ethics", page_size=2)
        print(f"Fetched {len(news_articles)} news articles.")
        for article in news_articles:
            print(f"- [NewsAPI] {article.get('title')}")

        print("\n--- Testing ArXiv Client ---")
        arxiv_client = ArxivClient()
        arxiv_articles = await arxiv_client.search_articles(query="quantum machine learning", limit=2)
        print(f"Fetched {len(arxiv_articles)} ArXiv articles.")
        for article in arxiv_articles:
            print(f"- [ArXiv] {article.get('title')}")

    asyncio.run(test_clients())