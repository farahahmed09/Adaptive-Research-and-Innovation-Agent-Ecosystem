# agents/analysis_agent.py

# Basic analysis (no external NLP libraries like spacy, NLTK)
import logging # Import logging
from collections import Counter # For basic keyword counting

# NEW: Import scikit-learn components
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np # For numerical operations with sklearn

# Configure logging for this module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# NO global spaCy model loaded here as it's not being used in this version

class AnalysisAgent:
    """
    The Analysis Agent is responsible for processing data from the Research Agent,
    applying analytical algorithms (trend detection, anomaly identification),
    and generating intermediate insights.
    """
    def __init__(self):
        logging.info("Analysis Agent initialized with scikit-learn tools (no spaCy/NLTK).") # UPDATED message


    async def analyze_data_and_generate_insights(self, research_data: list):
        logging.info(f"Analysis Agent: Analyzing {len(research_data)} data points with scikit-learn...") # UPDATED message
        logging.debug(f"Analysis Agent received research_data (first 2): {research_data[:2]}")
        insights = []
        all_text_content = [] # To aggregate text for overall analysis

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
                all_text_content.append(full_text) # Add to list for overall analysis
                
                # Basic keyword extraction (as in previous version, no spaCy/NLTK)
                words = full_text.split()
                basic_stop_words = set(['a', 'an', 'the', 'is', 'are', 'and', 'or', 'in', 'of', 'to', 'for', 'on', 'with', 'by']) # Very basic list
                filtered_words = [word for word in words if word.isalnum() and word not in basic_stop_words]

                entities = [] # This remains an empty list as spaCy is not used
                
                insight = {
                    "source": item.get('source', 'N/A'),
                    "title": title,
                    "insight_summary": f"Key takeaway: {summary[:150]}...",
                    "extracted_keywords": list(set(filtered_words[:5])),
                    "named_entities": entities, # Will always be empty list
                    "data_source_url": url,
                    "relevance_score": 0.5,
                }
                insights.append(insight)
            except Exception as e:
                logging.error(f"Error processing individual item from source '{item.get('source', 'Unknown')}' with title '{item.get('title', 'Unknown')[:50]}...': {e}")
                logging.exception("Full traceback for item processing error:")
                continue

        # --- Overall Analysis Across All Data (using scikit-learn) ---
        # THIS SECTION IS NOW FULLY ENABLED AND USES SCIPY LEARN
        if all_text_content and len(all_text_content) > 1: # Need at least 2 documents for vectorizer/clustering
            try:
                # 1. TF-IDF Vectorization for Important Terms
                # Use 'english' for stop_words as spaCy's nlp object is not available in this version
                vectorizer_stopwords = 'english'
                vectorizer = TfidfVectorizer(max_features=1000, stop_words=vectorizer_stopwords)
                tfidf_matrix = vectorizer.fit_transform(all_text_content)
                feature_names = vectorizer.get_feature_names_out()

                # Find top TF-IDF terms (basic topic indication)
                overall_top_terms = []
                sums_tfidf = tfidf_matrix.sum(axis=0)
                # Convert numpy array to a standard Python list of integers explicitly
                sorted_indices_list = np.argsort(sums_tfidf).flatten().tolist() 
                for i in sorted_indices_list[:10]: # Iterate over standard Python list
                    # Ensure each feature name is explicitly a string
                    overall_top_terms.append(str(feature_names[i]))

                # 2. Basic Clustering (e.g., K-Means for grouping similar articles)
                num_clusters = min(len(all_text_content), 3) # Max 3 clusters, minimum 2 for clustering
                if num_clusters >= 2: # Only cluster if we have enough items for at least 2 clusters
                    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10) # n_init for robustness
                    kmeans.fit(tfidf_matrix)
                    overall_trend_insight = {
                        "type": "overall_trend_analysis",
                        "description": "Identified major themes and important terms across all collected data using TF-IDF and KMeans.", # UPDATED description
                        "overall_top_terms": overall_top_terms,
                        "num_clusters_identified": int(num_clusters), # Ensure this is a standard int
                    }
                    insights.append(overall_trend_insight)
                else:
                    if overall_top_terms: # If not enough for clustering, just add top terms as a simple overall insight
                        simple_overall_insight = {
                            "type": "overall_summary",
                            "description": "Identified most frequent and important terms in the collected data using TF-IDF.", # UPDATED description
                            "overall_top_terms": overall_top_terms
                        }
                        insights.append(simple_overall_insight)

            except Exception as e:
                logging.warning(f"Error during advanced overall analysis (TF-IDF/Clustering): {type(e).__name__}: {e}")
                logging.exception("Full traceback for overall analysis error:")
        else: # If all_text_content is empty or too short for clustering
             logging.info("Not enough text content (less than 2 items) for advanced overall analysis (TF-IDF/Clustering).")


        # Update overall_quality_score based on the final set of insights
        final_overall_analysis_insight = next((i for i in insights if i.get("type") in ["overall_trend_analysis", "overall_analysis_summary"]), None)
        if final_overall_analysis_insight:
            overall_quality_score = final_overall_analysis_insight.get("insight_quality_score", 0.0)
            # Recalculate score to factor in advanced features if they ran successfully
            if final_overall_analysis_insight.get("type") == "overall_trend_analysis" or final_overall_analysis_insight.get("overall_top_terms"):
                overall_quality_score = min(1.0, 
                                            len(insights) / 10.0 + # Base on number of insights
                                            len(final_overall_analysis_insight.get('overall_top_terms', [])) / 10.0 + # Base on quality of terms
                                            final_overall_analysis_insight.get('num_clusters_identified', 0) / 3.0 # Base on number of clusters (will be 0 if not enough clusters)
                                        )
                final_overall_analysis_insight['insight_quality_score'] = overall_quality_score
            
        else: # No overall insight generated at all (very rare with current logic, but fallback)
            overall_quality_score = 0.05 # Very low score if no overall insight could be generated
            insights.append({"type": "overall_analysis_summary", "description": "No overall themes identified due to lack of data.", "insight_quality_score": overall_quality_score})


        logging.info(f"Analysis Agent: Generated {len(insights)} insights. Overall quality score: {overall_quality_score:.2f}")
        return insights