from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import httpx
import asyncio
import logging # NEW: For enhanced debugging
import traceback # NEW: For capturing full error details
from pydantic import BaseModel # NEW: For defining data structure for feedback

# Configure basic logging for main.py. Set to DEBUG for maximum verbosity.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Import database components
from database.models import SessionLocal, create_db_tables, User, Feedback # NEW: Import Feedback model

# Import agents
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.innovation_agent import InnovationAgent

# Import configuration (API keys)
from config import NEWS_API_KEY, GEMINI_API_KEY
# GNEWS_API_KEY is imported by ResearchAgent internally, so not needed here directly
# from config import GNEWS_API_KEY # (Optional: if needed for direct main.py logic)

# ----------------------------------------------------
# Pydantic Model for Feedback Request (NEW)
# ----------------------------------------------------
# This defines the expected structure of the JSON data coming in for feedback
class FeedbackRequest(BaseModel):
    query: str
    idea_title: str | None = None
    idea_description_snippet: str | None = None
    feedback_type: str # e.g., "positive", "negative", "neutral"
    comment: str | None = None

# ----------------------------------------------------
# 1. FastAPI Application Instance
# ----------------------------------------------------
app = FastAPI(title="Gen AI R&D Ecosystem API")

# ----------------------------------------------------
# 2. Configure Static Files and Templates for Web Interface
# ----------------------------------------------------
app.mount("/static", StaticFiles(directory="web_interface/static"), name="static")
templates = Jinja2Templates(directory="web_interface/templates")


# ----------------------------------------------------
# 3. Global Agent Instances
# ----------------------------------------------------
research_agent_instance: ResearchAgent = None
analysis_agent_instance: AnalysisAgent = None
innovation_agent_instance: InnovationAgent = None

# ----------------------------------------------------
# 4. Database & Agent Initialization on Startup Event
# ----------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """
    Perform startup tasks: create database tables and initialize agents.
    """
    try: # Wrap startup in try-except for logging
        if not os.path.exists("./local_database.db"):
            create_db_tables()
            logging.info("Database tables created.")
        else:
            logging.info("Database file already exists. Tables skipped creation.")

        global research_agent_instance
        # Research Agent now takes NEWS_API_KEY. It internally initializes other clients.
        if NEWS_API_KEY: # Only check NEWS_API_KEY for basic ResearchAgent functionality
            research_agent_instance = ResearchAgent(NEWS_API_KEY) 
            logging.info("Research Agent successfully initialized with multi-source config.")
        else:
            logging.warning("NEWS_API_KEY not found. Research Agent will not be fully functional.")
            
        global analysis_agent_instance
        analysis_agent_instance = AnalysisAgent()
        logging.info("Analysis Agent successfully initialized.")

        global innovation_agent_instance
        if GEMINI_API_KEY:
            innovation_agent_instance = InnovationAgent(GEMINI_API_KEY)
            logging.info("Innovation Agent successfully initialized with Gemini.")
        else:
            logging.warning("GEMINI_API_KEY not found. Innovation Agent will not be fully functional.")
    except Exception as e:
        logging.critical(f"CRITICAL ERROR during application startup: {type(e).__name__}: {e}")
        logging.critical(traceback.format_exc())
        raise RuntimeError(f"Application failed to start: {e}")


# ----------------------------------------------------
# 5. Database Dependency
# ----------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------
# 6. Authentication Helper (Very Basic - Not for Production!)
# ----------------------------------------------------
async def get_current_user_id(request: Request) -> str | None:
    user_id = request.cookies.get("user_id")
    return user_id

async def require_login(request: Request, user_id: str | None = Depends(get_current_user_id)):
    if user_id is None:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(key="user_id")
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"Location": "/login"})
    return user_id

# ----------------------------------------------------
# 7. Define API Endpoints & Web Routes
# ----------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root_redirect(request: Request, user_id: str | None = Depends(get_current_user_id)):
    if user_id:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint.
    Returns 'ok' if the API is running, database is connected, and all agents are initialized.
    """
    try:
        db.query(User).first()
        
        research_agent_ready = research_agent_instance is not None and research_agent_instance.news_client.api_key is not None
        analysis_agent_ready = analysis_agent_instance is not None
        innovation_agent_ready = innovation_agent_instance is not None and innovation_agent_instance.model is not None

        return {
            "status": "ok",
            "db_connected": True,
            "research_agent_ready": research_agent_ready,
            "analysis_agent_ready": analysis_agent_ready,
            "innovation_agent_ready": innovation_agent_ready
        }
    except Exception as e:
        logging.error(f"Service or database connection error in health check: {type(e).__name__}: {e}")
        logging.exception("Full traceback for health check error:")
        raise HTTPException(status_code=500, detail=f"Service or database connection error: {type(e).__name__}: {e}")

@app.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request, msg: str = None):
    """
    Displays the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Handles user login.
    Note: Passwords are not hashed for simplicity in this example. DO NOT use in production.
    """
    user = db.query(User).filter(User.username == username).first()

    if user and user.hashed_password == password + "_TEMPORARY_HASH":
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="user_id", value=str(user.id), httponly=True, max_age=3600)
        return response
    else:
        msg = "Invalid username or password"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@app.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request, msg: str = None):
    """
    Displays the registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Handles user registration.
    Note: Passwords are not hashed for simplicity in this example. DO NOT use in production.
    """
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        msg = "Username already exists. Please choose a different one."
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    hashed_password = password + "_TEMPORARY_HASH"
    new_user = User(username=username, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    response = RedirectResponse(url="/login?msg=Registration successful! Please log in.", status_code=303)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_page(request: Request, user_id: str = Depends(require_login)):
    """
    Displays the main user dashboard with chat-based interaction.
    Requires login.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user_id})

@app.post("/logout", response_class=RedirectResponse)
async def logout_user():
    """
    Logs out the user by clearing the session cookie and redirects to login.
    """
    response = RedirectResponse(url="/login?msg=You have been logged out.", status_code=303)
    response.delete_cookie(key="user_id")
    return response


@app.post("/users/")
async def create_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Creates a new user in the database via API.
    (This endpoint exists in parallel to the web registration form for API-based user creation)
    Note: Passwords are not hashed for simplicity in this example. DO NOT use in production.
    """
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = password + "_TEMPORARY_HASH"
    new_user = User(username=username, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id, "username": new_user.username}

@app.get("/agents/research/data")
async def get_research_data(query: str = "latest AI breakthroughs", count: int = 10):
    """
    API endpoint for the Research Agent to gather and preprocess data.
    This endpoint can be called by the Analysis Agent or directly for testing.
    """
    if research_agent_instance is None or research_agent_instance.news_client.api_key is None:
        raise HTTPException(
            status_code=503,
            detail="Research Agent is not configured or initialized. NEWS_API_KEY might be missing."
        )
    data = await research_agent_instance.gather_and_preprocess_data(query=query, count=count)
    return {"query": query, "data": data, "count": len(data)}

# API Endpoint for the Analysis Agent
@app.get("/agents/analysis/insights")
async def get_analysis_insights(query: str = "AI innovation", research_count: int = 5):
    """
    API endpoint for the Analysis Agent to process data from the Research Agent
    and generate insights. This can be called by the Innovation Agent.
    """
    if analysis_agent_instance is None:
        raise HTTPException(status_code=503, detail="Analysis Agent is not initialized.")

    # DEBUGGING BLOCK: Catch and display specific errors from analysis pipeline
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                research_api_url = f"http://127.0.0.1:8000/agents/research/data?query={query}&count={research_count}"
                logging.info(f"Analysis Agent calling Research Agent at: {research_api_url}")
                
                response = await client.get(research_api_url)
                response.raise_for_status()
                research_data_response = response.json()
                
                research_data = research_data_response.get("data", [])
                logging.info(f"Analysis Agent received {len(research_data)} items from Research Agent.")

            except httpx.HTTPStatusError as e:
                logging.error(f"Research Agent returned HTTP error: {e.response.status_code} - {e.response.text}")
                logging.error(traceback.format_exc())
                raise HTTPException(status_code=e.response.status_code, detail=f"Error calling Research Agent: {e.response.text}")
            except httpx.RequestError as e:
                logging.error(f"Network error calling Research Agent: {e}")
                logging.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Network error when calling Research Agent: {e}")
            except Exception as e:
                logging.error(f"Unexpected error when getting data from Research Agent: {type(e).__name__}: {e}")
                logging.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Unexpected error when getting data from Research Agent: {type(e).__name__}: {e}")

        # This call might be the source of the error if it's within analysis_agent.py
        insights = await analysis_agent_instance.analyze_data_and_generate_insights(research_data)
        
        return {
            "query": query,
            "insights": insights,
            "insights_count": len(insights)
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.critical(f"CRITICAL ERROR in Analysis Agent endpoint pipeline: {type(e).__name__}: {e}")
        logging.critical(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error during insight generation: {type(e).__name__}: {e}")


# API Endpoint for the Innovation Agent
@app.get("/agents/innovation/ideas")
async def get_innovation_ideas(  # THIS MUST BE 'async def'
    query: str = "AI innovation",
    research_count: int = 3,  # Number of articles to research
    creativity_level: str = "medium"  # Passed to Innovation Agent
):
    """
    API endpoint for the Innovation Agent to get insights from the Analysis Agent,
    generate ideas using Gen AI, and produce a Markdown report.
    """
    if innovation_agent_instance is None or innovation_agent_instance.model is None:
        raise HTTPException(
            status_code=503,
            detail="Innovation Agent is not configured or initialized. GEMINI_API_KEY might be missing."
        )

    # DEBUGGING BLOCK: Catch and display specific errors from agent pipeline
    try:
        # Step 1: Call the Analysis Agent's endpoint to get insights
        async with httpx.AsyncClient(timeout=30.0) as client:  # Set a 30-second timeout
            try:
                analysis_api_url = (
                    f"http://127.0.0.1:8000/agents/analysis/insights?"
                    f"query={query}&research_count={research_count}"
                )
                print(f"Innovation Agent calling Analysis Agent at: {analysis_api_url}")

                response = await client.get(analysis_api_url)
                response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)
                analysis_insights_response = response.json()

                insights = analysis_insights_response.get("insights", [])
                print(f"Innovation Agent received {len(insights)} insights from Analysis Agent.")

            except httpx.HTTPStatusError as e:
                print(f"Analysis Agent returned HTTP error: {e.response.status_code} - {e.response.text}")
                print(traceback.format_exc())
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Error calling Analysis Agent: {e.response.text}"
                )
            except httpx.RequestError as e:
                print(f"Network error calling Analysis Agent: {e}")
                print(traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail=f"Network error when calling Analysis Agent: {e}"
                )
            except Exception as e:
                print(f"Unexpected error when getting insights from Analysis Agent: {type(e).__name__}: {e}")
                print(traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected error when getting insights from Analysis Agent: {type(e).__name__}: {e}"
                )

        # Step 2: Pass insights to the Innovation Agent to generate ideas
        generated_ideas = await innovation_agent_instance.generate_ideas_from_insights(
            insights,
            creativity_level=creativity_level
        )

        # Step 3: Generate the Markdown report
        markdown_report = await innovation_agent_instance.generate_markdown_report(
            generated_ideas,
            query
        )

        return {
            "query": query,
            "generated_ideas": generated_ideas,
            "ideas_count": len(generated_ideas),
            "markdown_report": markdown_report
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"CRITICAL ERROR in Innovation Agent endpoint pipeline: {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during idea generation: {type(e).__name__}: {e}"
        )
    
@app.post("/feedback/")
async def submit_feedback(
    feedback_data: FeedbackRequest, # Data comes in as a Pydantic model
    user_id: str = Depends(require_login), # Requires authenticated user
    db: Session = Depends(get_db) # Requires database session
):
    """
    Receives and stores user feedback on generated ideas.
    """
    try:
        # Get the actual User object
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Create a new Feedback entry
        new_feedback = Feedback(
            user_id=user.id,
            query=feedback_data.query,
            idea_title=feedback_data.idea_title,
            idea_description_snippet=feedback_data.idea_description_snippet,
            feedback_type=feedback_data.feedback_type,
            comment=feedback_data.comment
        )

        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)

        logging.info(f"Feedback submitted by user {user.username} (ID: {user.id}). Type: {new_feedback.feedback_type}")
        return {"message": "Feedback submitted successfully!", "feedback_id": new_feedback.id}

    except Exception as e:
        logging.error(f"Error submitting feedback: {type(e).__name__}: {e}")
        logging.exception("Full traceback for feedback submission error:")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {type(e).__name__}: {e}")
    
# ----------------------------------------------------
# 8. Running the Application (Typically via Uvicorn)
# ----------------------------------------------------
# This block is commented out because Uvicorn is typically run via command line:
# use this command to run: uvicorn api.main:app --reload
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)