# agents/analysis_agent.py

# We might need to import external libraries for more complex analysis later (e.g., NLTK, spaCy, sklearn)
# import nltk # Example for natural language processing
# nltk.download('punkt') # Download necessary data for nltk if used

class AnalysisAgent:
    """
    The Analysis Agent is responsible for processing data from the Research Agent,
    applying analytical algorithms (trend detection, anomaly identification),
    and generating intermediate insights.
    """
    def __init__(self):
        print("Analysis Agent initialized.")

    async def analyze_data_and_generate_insights(self, research_data: list):
        """
        Analyzes the preprocessed data from the Research Agent and generates insights.

        Args:
            research_data (list): A list of dictionaries, where each dict represents
                                a preprocessed article/data point from the Research Agent.

        Returns:
            list: A list of dictionaries, each representing a generated insight.
                  Returns an empty list if no insights are generated.
        """
        print(f"Analysis Agent: Analyzing {len(research_data)} data points...")
        insights = []

        if not research_data:
            print("Analysis Agent: No research data provided for analysis.")
            return []

        # --- Placeholder for Innovative Algorithms ---
        # This is where your "innovative algorithms" will go.
        # For now, we'll implement very basic logic:
        # 1. Count keywords (simple trend detection)
        # 2. Summarize each article into an insight
        # --------------------------------------------

        keyword_counts = {}
        for item in research_data:
            # Basic keyword extraction from title and summary
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()

            # Simple keyword counting - replace with more sophisticated NLP later
            if "ai" in text:
                keyword_counts["ai"] = keyword_counts.get("ai", 0) + 1
            if "innovation" in text:
                keyword_counts["innovation"] = keyword_counts.get("innovation", 0) + 1
            if "breakthrough" in text:
                keyword_counts["breakthrough"] = keyword_counts.get("breakthrough", 0) + 1
            # Add more keywords relevant to your project

            # Generate a simple insight for each article
            insight = {
                "source_title": item.get('title'),
                "insight_summary": f"Key takeaway: {item.get('summary', '')[:150]}...", # Truncate summary
                "relevance_score": 0.5, # Placeholder score
                "data_source_url": item.get('source_url'),
                # You could add a sentiment score here later using a library like TextBlob
                # "sentiment": "neutral"
            }
            insights.append(insight)

        # Add a general trend insight based on keyword counts
        if keyword_counts:
            trend_insight = {
                "type": "overall_trend_analysis",
                "description": "Identified popular keywords in current research data.",
                "keywords_found": keyword_counts,
                "strongest_trend": max(keyword_counts, key=keyword_counts.get) if keyword_counts else None
            }
            insights.append(trend_insight)
            print(f"Analysis Agent: Identified trends: {keyword_counts}")

        print(f"Analysis Agent: Generated {len(insights)} insights.")
        return insights

# Example usage for testing this agent directly (optional)
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        # Dummy data to simulate output from Research Agent
        dummy_research_data = [
            {"title": "AI's new breakthrough in medical imaging", "summary": "Researchers achieve high accuracy with a novel AI algorithm.", "source_url": "http://example.com/ai-med"},
            {"title": "Innovation in renewable energy storage", "summary": "New battery tech promises longer lifespan for green energy.", "source_url": "http://example.com/energy-tech"},
            {"title": "The future of AI ethics: a new perspective", "summary": "Experts debate the moral implications of advanced AI systems.", "source_url": "http://example.com/ai-ethics"},
        ]

        agent = AnalysisAgent()
        insights = await agent.analyze_data_and_generate_insights(dummy_research_data)

        for i, insight in enumerate(insights):
            print(f"\n--- Insight {i+1} ---")
            print(f"Type: {insight.get('type', 'Article Insight')}")
            print(f"Summary/Description: {insight.get('insight_summary', insight.get('description'))}")
            if 'keywords_found' in insight:
                print(f"Keywords: {insight['keywords_found']}")

    asyncio.run(test_agent())