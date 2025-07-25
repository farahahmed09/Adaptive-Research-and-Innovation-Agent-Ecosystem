# agents/analysis_agent.py

# ONLY basic analysis (no external NLP/ML libraries like spacy, sklearn, NLTK)
import logging # Import logging

# Configure logging for this module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# No global spaCy model loaded here for this basic version

class AnalysisAgent:
    """
    The Analysis Agent is responsible for processing data from the Research Agent,
    applying analytical algorithms (trend detection, anomaly identification),
    and generating intermediate insights.
    """
    def __init__(self):
        logging.info("Analysis Agent initialized (basic version).")
        # No NLTK/spaCy/sklearn initialization needed for this basic version


    async def analyze_data_and_generate_insights(self, research_data: list):
        logging.info(f"Analysis Agent: Analyzing {len(research_data)} data points...")
        logging.debug(f"Analysis Agent received research_data (first 2): {research_data[:2]}")
        insights = []

        if not research_data:
            logging.info("Analysis Agent: No research data provided for analysis.")
            return []

        # Wrap item processing in a try/except to catch errors per item
        for item in research_data:
            try:
                if not isinstance(item, dict):
                    logging.warning(f"Analysis Agent received non-dictionary item: {item}. Skipping.")
                    continue

                logging.debug(f"Processing item: Source='{item.get('source', 'N/A')}', Title='{item.get('title', 'N/A')[:50]}...'")

                title = str(item.get('title', ''))
                summary = str(item.get('summary', ''))
                content = str(item.get('content', ''))
                url = item.get('url')

                full_text = f"{title} {summary} {content}".lower()
                
                # Basic keyword extraction (no spaCy/NLTK for this version)
                words = full_text.split()
                basic_stop_words = set(['a', 'an', 'the', 'is', 'are', 'and', 'or', 'in', 'of', 'to', 'for', 'on', 'with', 'by']) # Very basic list
                filtered_words = [word for word in words if word.isalnum() and word not in basic_stop_words]

                entities = [] # No entities for this basic version
                
                insight = {
                    "source": item.get('source', 'N/A'),
                    "title": title,
                    "insight_summary": f"Key takeaway: {summary[:150]}...",
                    "extracted_keywords": list(set(filtered_words[:5])),
                    "named_entities": entities, # This will be an empty list for now
                    "data_source_url": url,
                    "relevance_score": 0.5,
                }
                insights.append(insight)
            except Exception as e:
                logging.error(f"Error processing individual item from source '{item.get('source', 'Unknown')}' with title '{item.get('title', 'Unknown')[:50]}...': {e}")
                logging.exception("Full traceback for item processing error:")
                continue # Skip this problematic item, try next one

        # --- Overall Analysis (simple keyword counting) ---
        if insights:
            all_extracted_keywords_flat = []
            for insight in insights:
                all_extracted_keywords_flat.extend(insight.get('extracted_keywords', []))
            
            from collections import Counter
            keyword_counts = Counter(all_extracted_keywords_flat)
            
            if keyword_counts:
                overall_top_terms = [word for word, count in keyword_counts.most_common(10)]
                overall_trend_insight = {
                    "type": "overall_trend_analysis",
                    "description": "Identified popular keywords/themes across all collected data.",
                    "overall_top_terms": overall_top_terms,
                    "num_processed_items": len(insights)
                }
                insights.append(overall_trend_insight)
            else:
                logging.info("No common keywords found for overall trend analysis.")

        logging.info(f"Analysis Agent: Generated {len(insights)} insights.")
        return insights

# Example usage for testing this agent directly (optional)
# if __name__ == "__main__":
#     import asyncio
#     import sys
#     import os
#     sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#     async def test_agent():
#         dummy_research_data = [
#             {"source": "NewsAPI", "title": "Sample AI Article 1", "summary": "AI is transforming healthcare.", "content": "Long content about AI in medicine."},
#             {"source": "ArXiv", "title": "Machine Learning in Genomics", "summary": "Deep dive into ML applications for DNA sequencing.", "content": "Abstract of academic paper."},
#             {"source": "Custom", "title": "Article with no summary", "summary": None, "content": "Just some content here."},
#             "This is not a dictionary item and should be skipped by the agent"
#         ]
            
#         agent = AnalysisAgent()
#         insights = await agent.analyze_data_and_generate_insights(dummy_research_data)
        
#         for i, insight in enumerate(insights):
#             print(f"\n--- Insight {i+1} ---")
#             print(f"Source: {insight.get('source', 'N/A')}")
#             print(f"Title: {insight.get('title', 'N/A')}")
#             print(f"Summary: {insight.get('insight_summary', 'N/A')}")
#             if 'extracted_keywords' in insight:
#                 print(f"Keywords: {insight['extracted_keywords']}")
#             if 'named_entities' in insight and insight['named_entities']:
#                 print(f"Entities: {insight['named_entities']}")

#     asyncio.run(test_agent())