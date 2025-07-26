# agents/analysis_agent.py

# Basic analysis only (no external NLP/ML libraries like spacy, sklearn, NLTK)
import logging # Import logging
from collections import Counter # For basic keyword counting

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


    async def analyze_data_and_generate_insights(self, research_data: list):
        logging.info(f"Analysis Agent: Analyzing {len(research_data)} data points...")
        logging.debug(f"Analysis Agent received research_data (first 2): {research_data[:2]}")
        insights = []

        # Ensure insights list starts with overall summary even if no data
        overall_quality_score = 0.0 

        if not research_data:
            logging.info("Analysis Agent: No research data provided for analysis.")
            insights.append({"type": "overall_analysis_summary", "description": "No data found for initial analysis.", "insight_quality_score": 0.1}) # Low score
            logging.info(f"Analysis Agent: Generated {len(insights)} insights. Overall quality score: {0.1:.2f}")
            return insights


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
                continue

        # --- Overall Analysis (simple keyword counting) ---
        if insights:
            all_extracted_keywords_flat = []
            for insight in insights:
                all_extracted_keywords_flat.extend(insight.get('extracted_keywords', []))
            
            keyword_counts = Counter(all_extracted_keywords_flat)
            
            if keyword_counts:
                overall_top_terms = [word for word, count in keyword_counts.most_common(10)]
                # Calculate a simple quality score based on number of insights and unique keywords
                overall_quality_score = min(1.0, len(insights) / 10.0 + len(keyword_counts) / 20.0) # Example heuristic
                overall_trend_insight = {
                    "type": "overall_trend_analysis",
                    "description": "Identified popular keywords/themes across all collected data.",
                    "overall_top_terms": overall_top_terms,
                    "num_processed_items": len(insights),
                    "insight_quality_score": overall_quality_score # Add quality score
                }
                insights.append(overall_trend_insight)
            else:
                logging.info("No common keywords found for overall trend analysis.")
                overall_quality_score = 0.2 # Low score if no keywords
                insights.append({"type": "overall_analysis_summary", "description": "No significant themes identified.", "insight_quality_score": overall_quality_score})

        logging.info(f"Analysis Agent: Generated {len(insights)} insights. Overall quality score: {overall_quality_score:.2f}")
        return insights