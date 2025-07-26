# agents/analysis_agent.py

# Import scikit-learn components
import spacy 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np # For numerical operations with sklearn
import logging
from collections import Counter

# Configure logging for this module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load a spaCy language model globally once
try:
    nlp = spacy.load("en_core_web_sm")
    logging.info("SpaCy model 'en_core_web_sm' loaded successfully.")
except Exception as e:
    logging.error(f"Could not load spaCy model. Ensure 'python -m spacy download en_core_web_sm' was run. Error: {e}")
    logging.exception("Full traceback for spaCy model loading error:")
    nlp = None


class AnalysisAgent:
    """
    The Analysis Agent is responsible for processing data from the Research Agent,
    applying analytical algorithms (trend detection, anomaly identification),
    and generating intermediate insights.
    """
    def __init__(self):
        logging.info("Analysis Agent initialized with advanced spaCy and scikit-learn tools.")


    async def analyze_data_and_generate_insights(self, research_data: list):
        logging.info(f"Analysis Agent: Analyzing {len(research_data)} data points with advanced tools...")
        logging.debug(f"Analysis Agent received research_data (first 2): {research_data[:2]}")
        insights = []
        all_text_content = [] # To aggregate text for overall analysis

        overall_quality_score = 0.0 

        if not research_data:
            logging.info("Analysis Agent: No research data provided for analysis.")
            insights.append({"type": "overall_analysis_summary", "description": "No data found for initial analysis.", "insight_quality_score": 0.1})
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
                all_text_content.append(full_text)

                entities = []
                filtered_words = []
                if nlp: # Only run if spaCy model loaded
                    doc = nlp(full_text)
                    for ent in doc.ents:
                        entities.append({"text": str(ent.text), "label": str(ent.label_)}) # Ensure text and label are strings
                    
                    for token in doc:
                        if token.is_alpha and not token.is_stop:
                            filtered_words.append(str(token.lemma_)) # Ensure lemma is string
                else: # Fallback if spaCy model failed to load
                    words = full_text.split()
                    basic_stop_words = set(['a', 'an', 'the', 'is', 'are', 'and', 'or', 'in', 'of', 'to', 'for', 'on', 'with', 'by'])
                    filtered_words = [word for word in words if word.isalnum() and word not in basic_stop_words]
                
                insight = {
                    "source": item.get('source', 'N/A'),
                    "title": title,
                    "insight_summary": f"Key takeaway: {summary[:150]}...",
                    "extracted_keywords": list(set(filtered_words[:5])), # Convert set to list
                    "named_entities": entities, # List of dicts, elements ensured string
                    "data_source_url": url,
                    "relevance_score": 0.5,
                }
                insights.append(insight)
            except Exception as e:
                logging.error(f"Error processing individual item from source '{item.get('source', 'Unknown')}' with title '{item.get('title', 'Unknown')[:50]}...': {e}")
                logging.exception("Full traceback for item processing error:")
                continue

        # --- Overall Analysis Across All Data (using scikit-learn) ---
        if all_text_content and len(all_text_content) > 1:
            try:
                vectorizer_stopwords = list(nlp.Defaults.stop_words) if nlp else 'english'
                vectorizer = TfidfVectorizer(max_features=1000, stop_words=vectorizer_stopwords)
                tfidf_matrix = vectorizer.fit_transform(all_text_content)
                feature_names = vectorizer.get_feature_names_out()

                overall_top_terms = []
                sums_tfidf = tfidf_matrix.sum(axis=0)
                # Ensure sorted_indices is a standard Python list of integers from numpy array
                sorted_indices_list = np.argsort(sums_tfidf).flatten().tolist() 
                for i in sorted_indices_list[:10]:
                    # Ensure each feature name is explicitly a string
                    overall_top_terms.append(str(feature_names[i]))

                num_clusters_val = min(len(all_text_content), 3)
                if num_clusters_val >= 2:
                    kmeans = KMeans(n_clusters=num_clusters_val, random_state=0, n_init=10)
                    kmeans.fit(tfidf_matrix)
                    overall_trend_insight = {
                        "type": "overall_trend_analysis",
                        "description": "Identified major themes and important terms across all collected data using TF-IDF and KMeans.",
                        "overall_top_terms": overall_top_terms,
                        "num_clusters_identified": int(num_clusters_val), 
                    }
                    insights.append(overall_trend_insight)
                else:
                    if overall_top_terms:
                        simple_overall_insight = {
                            "type": "overall_summary",
                            "description": "Identified most frequent and important terms in the collected data using TF-IDF.",
                            "overall_top_terms": overall_top_terms
                        }
                        insights.append(simple_overall_insight)

            except Exception as e:
                logging.warning(f"Error during advanced overall analysis (TF-IDF/Clustering): {type(e).__name__}: {e}")
                logging.exception("Full traceback for overall analysis error:")
        else:
             logging.info("Not enough text content for advanced overall analysis (TF-IDF/Clustering).")


        final_overall_analysis_insight = next((i for i in insights if i.get("type") in ["overall_trend_analysis", "overall_analysis_summary"]), None)
        if final_overall_analysis_insight:
            overall_quality_score = final_overall_analysis_insight.get("insight_quality_score", 0.0)
            if final_overall_analysis_insight.get("type") == "overall_trend_analysis":
                overall_quality_score = min(1.0, 
                                            len(insights) / 10.0 + 
                                            len(final_overall_analysis_insight.get('overall_top_terms', [])) / 10.0 + 
                                            final_overall_analysis_insight.get('num_clusters_identified', 0) / 3.0
                                        )
                final_overall_analysis_insight['insight_quality_score'] = overall_quality_score
            
        else:
            overall_quality_score = 0.05
            insights.append({"type": "overall_analysis_summary", "description": "No overall themes identified due to lack of data.", "insight_quality_score": overall_quality_score})


        logging.info(f"Analysis Agent: Generated {len(insights)} insights. Overall quality score: {overall_quality_score:.2f}")
        return insights