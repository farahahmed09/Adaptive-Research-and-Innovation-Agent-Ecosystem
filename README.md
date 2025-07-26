# Gen AI Adaptive Research & Innovation Agent Ecosystem

## Project Overview

This project implements a sophisticated **multi-agent system** designed to autonomously gather information, analyze emerging trends, and dynamically generate innovative research directions and improvement proposals. It simulates a dynamic Research & Development (R&D) environment, where distinct AI agents collaborate, *and coordinate their efforts*, based on real-time inputs from external sources.

The goal is to provide a powerful, interactive tool that leverages Generative AI to accelerate the brainstorming and early-stage research process, delivering structured insights and actionable ideas.

## Core Features Implemented

* **Multi-Agent Architecture:**
    * **Research Agent:** Continuously fetches and preprocesses data from diverse third-party external sources.
    * **Analysis Agent:** Processes incoming data, extracts key insights, trends, and relevant information using advanced analytical algorithms.
    * **Innovation Agent:** Integrates insights from the Analysis Agent, dynamically generates novel research ideas and proposals using a Generative AI model, and compiles comprehensive reports.
* **Diverse Data Sources:** Integrates with leading APIs to gather rich and varied information:
    * **NewsAPI:** For general news and current events.
    * **ArXiv API:** For academic papers and scientific preprints.
    * **GNews API:** Another robust source for current news articles.
* **Advanced Analysis Capabilities (Analysis Agent):**
    * Utilizes **scikit-learn** for sophisticated overall analysis, including TF-IDF vectorization to identify important terms and KMeans clustering for detecting major themes within the collected data.
    * Performs basic keyword extraction and named entity recognition per item.
* **Generative AI Integration:** Leverages **Google Gemini** (specifically the `gemini-pro` or `gemini-2.5-flash` model as configured) to power the creative idea generation and summarization capabilities of the Innovation Agent.
* **Agent Coordination & Negotiation:**
    * Implements an **Orchestrated Refinement Loop** where the Innovation Agent (via the main orchestrator) assesses the quality of initial insights. If the insights are deemed of low quality, it can "negotiate" by formulating a more targeted refinement query, sending it back to the Analysis Agent for a second round of analysis, and then generating ideas from the improved insights. This demonstrates dynamic adaptation and collaboration.
* **User-Friendly Web Interface:**
    * A secure **Login and Registration** system to manage user access.
    * An interactive, **chat-based dashboard** for users to submit research queries.
    * Dynamic display of generated ideas and detailed Markdown reports with professional styling.
* **Dynamic Reporting & Download:** Generates structured Markdown reports of the generated ideas, which can be **downloaded as a PDF** directly from the dashboard.
* **User Feedback Mechanism:** Allows users to provide explicit feedback (e.g., "useful," "not useful") on individual generated ideas. This feedback is stored in the local database, enabling future evaluation and potential improvements to the AI's performance.
* **Robustness & Error Handling:** Implements comprehensive `try-except` blocks and detailed logging at each stage to ensure the system remains stable even if individual external data sources fail or unexpected data is encountered.
* **Modular Design:** Built with Python and FastAPI, promoting clear separation of concerns, scalability, and maintainability across distinct agent modules.

## How It Works (The Robot Assistant in Action)

1.  **User Query:** A user logs into the web dashboard and submits a research query (e.g., "AI in healthcare").
2.  **Research Phase:** The **Research Agent** (via its API endpoint) fetches relevant articles and papers from NewsAPI, GNews API, and ArXiv, handling any individual source failures gracefully.
3.  **Analysis Phase (Initial):** The **Analysis Agent** (via its API endpoint) receives the collected data. It processes this data, extracting basic keywords, named entities, and then performs overall analysis using **scikit-learn** (TF-IDF, clustering) to identify major themes. It then compiles these into structured insights, including an `insight_quality_score`.
4.  **Innovation Phase (Orchestration & Refinement):** The main application orchestrator (FastAPI endpoint) assesses the `insight_quality_score` from the Analysis Agent.
    * If the score is below a defined threshold, it **triggers a negotiation (refinement loop)**: it formulates a more targeted query for the Analysis Agent and requests further, refined insights.
    * The **Innovation Agent** then takes the (potentially refined) insights and prompts the **Google Gemini LLM** to brainstorm innovative ideas.
5.  **Report Generation & Display:** The Innovation Agent formats these generated ideas into a comprehensive Markdown report. Both the ideas and the formatted report are displayed dynamically on the user's dashboard.
6.  **User Interaction:** Users can then provide structured feedback on the usefulness of individual ideas, which is recorded in the database.
7.  **Download:** Users can download the full report as a PDF for offline viewing or sharing.

## Technologies Used

* **Backend:**
    * Python 3.9+
    * FastAPI: High-performance web framework for APIs.
    * Uvicorn: ASGI server to run the FastAPI application.
    * SQLAlchemy: ORM for database interactions.
    * SQLite: Lightweight local database (`local_database.db`).
    * `httpx`: Asynchronous HTTP client for inter-agent communication.
    * `python-dotenv`: For managing environment variables.
* **Generative AI:**
    * `google-generativeai`: Python SDK for Google Gemini LLMs (configured to use `gemini-pro` or `gemini-2.5-flash`).
* **Data Sources:**
    * NewsAPI
    * ArXiv API
    * GNews API
    * `requests`: HTTP client for external API calls.
* **Natural Language Processing & Machine Learning:**
    * `scikit-learn`: For TF-IDF vectorization and KMeans clustering in overall text analysis.
    * `numpy`: Numerical computing library (dependency for scikit-learn).
    * *(Note: The system has a placeholder for spaCy integration for per-item NLP, which can be re-enabled for further enhancement.)*
* **Frontend:**
    * HTML5, CSS3, JavaScript
    * Jinja2: Templating engine for HTML pages.
    * `marked.js`: JavaScript library for rendering Markdown to HTML.
    * `html2canvas`: JavaScript library for capturing HTML content as a canvas image for PDF.
    * `jsPDF`: JavaScript library for generating PDF documents from canvas images.

## Setup and Installation

Follow these steps to get your **Gen AI Adaptive Research & Innovation Agent Ecosystem** up and running locally.

### Prerequisites

* Python 3.9 or higher installed.
* `pip` (Python package installer) installed.
* Git installed.

### 1. Clone the Repository

```bash
git clone [https://github.com/farahahmed09/Adaptive-Research-and-Innovation-Agent-Ecosystem.git](https://github.com/farahahmed09/Adaptive-Research-and-Innovation-Agent-Ecosystem.git)
cd Adaptive-Research-and-Innovation-Agent-Ecosystem