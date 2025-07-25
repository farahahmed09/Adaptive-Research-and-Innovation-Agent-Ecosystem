# Gen AI Adaptive Research & Innovation Agent Ecosystem

## Project Overview

This project implements a sophisticated **multi-agent system** designed to autonomously gather information, analyze emerging trends, and dynamically generate innovative research directions and improvement proposals. It simulates a research and development (R&D) ecosystem where distinct AI agents collaborate to adapt their strategies based on real-time inputs from external sources.

The goal is to provide a powerful, interactive tool that leverages Generative AI to accelerate the brainstorming and early-stage research process.

## Core Features Implemented

* **Multi-Agent Architecture:**
    * **Research Agent:** Continuously fetches and preprocesses data from diverse third-party external sources.
    * **Analysis Agent:** Processes incoming data, extracts key insights, trends, and relevant information.
    * **Innovation Agent:** Integrates insights from the Analysis Agent, dynamically generates novel research ideas and proposals using a Generative AI model, and compiles comprehensive reports.
* **Diverse Data Sources:** Integrates with leading APIs to gather rich and varied information:
    * **NewsAPI:** For general news and current events.
    * **ArXiv API:** For academic papers and scientific preprints.
    * *(Note: The system is designed for easy expansion to other APIs like GNews, Crossref, etc.)*
* **Generative AI Integration:** Leverages **Google Gemini** (or other LLMs) to power the creative idea generation and summarization capabilities of the Innovation Agent.
* **User-Friendly Web Interface:**
    * A secure **Login and Registration** system to manage user access.
    * An interactive, **chat-based dashboard** for users to submit research queries.
    * Dynamic display of generated ideas and detailed Markdown reports.
* **Dynamic Reporting & Download:** Generates structured Markdown reports of the generated ideas, which can be **downloaded as a PDF** directly from the dashboard.
* **User Feedback Mechanism:** Allows users to provide explicit feedback (e.g., "useful," "not useful") on individual generated ideas, which is stored in the database.
* **Robustness & Error Handling:** Implements defensive coding practices to ensure the system remains stable even if individual external data sources fail or return unexpected data.
* **Modular Design:** Built with Python and FastAPI, promoting clear separation of concerns, scalability, and maintainability.

## How It Works (The Robot Assistant in Action)

1.  **User Query:** A user logs into the web dashboard and submits a research query (e.g., "AI in healthcare").
2.  **Research Phase:** The **Research Agent** (via `api/agents/research/data` endpoint) fetches relevant articles and papers from NewsAPI and ArXiv.
3.  **Analysis Phase:** The **Analysis Agent** (via `api/agents/analysis/insights` endpoint) receives the collected data, extracts keywords, and compiles structured insights.
4.  **Innovation Phase:** The **Innovation Agent** (via `api/agents/innovation/ideas` endpoint) takes these insights, prompts the **Google Gemini LLM** to brainstorm innovative ideas, and formats these ideas into a comprehensive Markdown report.
5.  **Display & Interaction:** The generated ideas and the formatted report are displayed on the user's dashboard. Users can then provide feedback on specific ideas.
6.  **Download:** Users can download the full report as a PDF for offline viewing or sharing.

## Technologies Used

* **Backend:**
    * Python 3.9+
    * FastAPI: High-performance web framework for APIs.
    * Uvicorn: ASGI server to run the FastAPI application.
    * SQLAlchemy: ORM for database interactions.
    * SQLite: Lightweight local database.
    * `httpx`: Asynchronous HTTP client for inter-agent communication.
    * `python-dotenv`: For managing environment variables.
* **Generative AI:**
    * `google-generativeai`: Python SDK for Google Gemini LLMs.
* **Data Sources:**
    * NewsAPI
    * ArXiv API
    * `requests`: HTTP client for external API calls.
* **Natural Language Processing (Basic):**
    * Basic string manipulation and keyword extraction.
* **Frontend:**
    * HTML5, CSS3, JavaScript
    * Jinja2: Templating engine for HTML pages.
    * `marked.js`: JavaScript library for rendering Markdown to HTML.
    * `html2canvas`: JavaScript library for capturing HTML content as a canvas image.
    * `jsPDF`: JavaScript library for generating PDF documents from canvas images.

## Setup and Installation

Follow these steps to get your **Gen AI Adaptive Research & Innovation Agent Ecosystem** up and running locally.

### Prerequisites

* Python 3.9 or higher installed.
* `pip` (Python package installer) installed.
* Git installed.

### 1. Clone the Repository

```bash
git clone <your_repository_url_here>
cd <your_repository_name> # e.g., cd Gen-AI-Adaptive-Research-Innovation-Agent-Ecosystem
