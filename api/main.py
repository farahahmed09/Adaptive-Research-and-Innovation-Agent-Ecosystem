from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import httpx
import asyncio

# Import database components
from database.models import SessionLocal, create_db_tables, User

# Import agents
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.innovation_agent import InnovationAgent

# Import configuration (API keys)
from config import NEWS_API_KEY, GEMINI_API_KEY # IMPORTANT: Ensure GEMINI_API_KEY is here

# ----------------------------------------------------
# 1. FastAPI Application Instance
# ----------------------------------------------------
app = FastAPI(title="Gen AI R&D Ecosystem API")

# ----------------------------------------------------
# 2. Configure Static Files and Templates for Web Interface
# ----------------------------------------------------
# Mount the 'static' directory to serve static files (CSS, JS, images).
# Requests to /static/ will be mapped to files in web_interface/static/.
app.mount("/static", StaticFiles(directory="web_interface/static"), name="static")

# Configure Jinja2Templates to load HTML templates from the 'templates' directory.
templates = Jinja2Templates(directory="web_interface/templates")


# ----------------------------------------------------
# 3. Global Agent Instances
# ----------------------------------------------------
# These will be initialized once on application startup
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
    # Database Table Creation
    if not os.path.exists("./local_database.db"):
        create_db_tables()
        print("INFO: Database tables created.")
    else:
        print("INFO: Database file already exists. Tables skipped creation.")

    # Initialize Research Agent
    global research_agent_instance
    if NEWS_API_KEY:
        research_agent_instance = ResearchAgent(NEWS_API_KEY)
        print("INFO: Research Agent successfully initialized.")
    else:
        print("WARNING: NEWS_API_KEY not found. Research Agent will not be fully functional.")
        
    # Initialize Analysis Agent
    global analysis_agent_instance
    analysis_agent_instance = AnalysisAgent()
    print("INFO: Analysis Agent successfully initialized.")

    # Initialize Innovation Agent (UPDATED for Gemini)
    global innovation_agent_instance
    if GEMINI_API_KEY: # CHECKING for GEMINI_API_KEY
        innovation_agent_instance = InnovationAgent(GEMINI_API_KEY) # PASSING GEMINI_API_KEY
        print("INFO: Innovation Agent successfully initialized with Gemini.")
    else:
        print("WARNING: GEMINI_API_KEY not found. Innovation Agent will not be fully functional.")


# ----------------------------------------------------
# 5. Database Dependency
# ----------------------------------------------------
# This dependency function provides a database session for endpoints that need it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------
# 6. Authentication Helper (Very Basic - Not for Production!)
# ----------------------------------------------------
# This is a very simple way to check if a user is "logged in" via cookie.
# In a real application, you would use secure session tokens, JWTs, etc.
async def get_current_user_id(request: Request) -> str | None: # Returns user_id or None
    user_id = request.cookies.get("user_id")
    return user_id

# Middleware-like function to protect routes (redirect if not logged in)
async def require_login(request: Request, user_id: str | None = Depends(get_current_user_id)):
    if user_id is None:
        # Redirect to login page
        response = RedirectResponse(url="/login", status_code=303)
        # Clear any potentially stale user_id cookie
        response.delete_cookie(key="user_id")
        # FastAPI's HTTPException can be used to raise an error that can be caught
        # by the framework to perform the redirect, typically with `detail` and `headers`
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"Location": "/login"})
    return user_id # Return user_id if authenticated

# ----------------------------------------------------
# 7. Define API Endpoints & Web Routes
# ----------------------------------------------------

# Root API endpoint (for basic API health check / welcome message)
# Changed "/" to redirect to login if not logged in
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
        # Check database connection
        db.query(User).first()
        
        # Check Research Agent readiness
        research_agent_ready = research_agent_instance is not None and research_agent_instance.news_client.api_key is not None
        
        # Check Analysis Agent readiness
        analysis_agent_ready = analysis_agent_instance is not None
        
        # Check Innovation Agent readiness (UPDATED: check .model attribute for Gemini)
        innovation_agent_ready = innovation_agent_instance is not None and innovation_agent_instance.model is not None

        return {
            "status": "ok",
            "db_connected": True,
            "research_agent_ready": research_agent_ready,
            "analysis_agent_ready": analysis_agent_ready,
            "innovation_agent_ready": innovation_agent_ready
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service or database connection error: {e}")

# Web Route: Login Page (GET request to display the form)
@app.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request, msg: str = None): # Added msg parameter for messages
    """
    Displays the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

# Web Route: Handle Login Form Submission (POST request)
@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Handles user login.
    Note: Passwords are not hashed for simplicity in this example. DO NOT use in production.
    """
    user = db.query(User).filter(User.username == username).first()

    # Basic login check (placeholder for real hashing and comparison)
    if user and user.hashed_password == password + "_TEMPORARY_HASH":
        # Successful login - Redirect to dashboard
        response = RedirectResponse(url="/dashboard", status_code=303)
        # Set a cookie to indicate the user is logged in
        response.set_cookie(key="user_id", value=str(user.id), httponly=True, max_age=3600) # Valid for 1 hour
        return response
    else:
        # Failed login - Render login page again with an error message
        msg = "Invalid username or password"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

# Web Route: Registration Page (GET request to display the form)
@app.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request, msg: str = None): # Added msg parameter for messages
    """
    Displays the registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

# Web Route: Handle Registration Form Submission (POST request)
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

    hashed_password = password + "_TEMPORARY_HASH" # STILL A PLACEHOLDER FOR REAL HASHING
    new_user = User(username=username, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Redirect to login page after successful registration
    response = RedirectResponse(url="/login?msg=Registration successful! Please log in.", status_code=303)
    return response

# NEW WEB ROUTE: Dashboard (main user interaction page)
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_page(request: Request, user_id: str = Depends(require_login)): # Protected route
    """
    Displays the main user dashboard with chat-based interaction.
    Requires login.
    """
    # In a real app, you might fetch user-specific data here based on user_id
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user_id})

# NEW WEB ROUTE: Logout
@app.post("/logout", response_class=RedirectResponse)
async def logout_user():
    """
    Logs out the user by clearing the session cookie and redirects to login.
    """
    response = RedirectResponse(url="/login?msg=You have been logged out.", status_code=303)
    response.delete_cookie(key="user_id") # Clear the cookie
    return response


# API Endpoint: Create User (via API, e.g., for testing in Swagger UI)
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

# API Endpoint for the Research Agent
@app.get("/agents/research/data")
async def get_research_data(query: str = "latest AI breakthroughs", count: int = 5):
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

    async with httpx.AsyncClient() as client:
        try:
            # Call the Research Agent's endpoint (this API's own endpoint)
            research_api_url = f"http://127.0.0.1:8000/agents/research/data?query={query}&count={research_count}"
            print(f"Analysis Agent calling Research Agent at: {research_api_url}")
            
            response = await client.get(research_api_url)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx, 5xx)
            research_data_response = response.json()
            
            research_data = research_data_response.get("data", [])
            print(f"Analysis Agent received {len(research_data)} items from Research Agent.")

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error calling Research Agent: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error when calling Research Agent: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error when getting data from Research Agent: {e}")

    insights = await analysis_agent_instance.analyze_data_and_generate_insights(research_data)
    
    return {"query": query, "insights": insights, "insights_count": len(insights)}

# API Endpoint for the Innovation Agent
@app.get("/agents/innovation/ideas")
async def get_innovation_ideas( # THIS MUST BE 'async def'
    query: str = "AI innovation",
    research_count: int = 3, # Number of articles to research
    creativity_level: str = "medium" # Passed to Innovation Agent
):
    """
    API endpoint for the Innovation Agent to get insights from the Analysis Agent,
    generate ideas using Gen AI, and produce a Markdown report.
    """
    # Check if Innovation Agent is initialized (UPDATED for Gemini: check .model attribute)
    if innovation_agent_instance is None or innovation_agent_instance.model is None:
        raise HTTPException(
            status_code=503,
            detail="Innovation Agent is not configured or initialized. GEMINI_API_KEY might be missing."
        )
    
    # Step 1: Call the Analysis Agent's endpoint to get insights
    async with httpx.AsyncClient() as client:
        try:
            analysis_api_url = f"http://127.0.0.1:8000/agents/analysis/insights?query={query}&research_count={research_count}"
            print(f"Innovation Agent calling Analysis Agent at: {analysis_api_url}")
            
            response = await client.get(analysis_api_url)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx, 5xx)
            analysis_insights_response = response.json()
            
            insights = analysis_insights_response.get("insights", [])
            print(f"Innovation Agent received {len(insights)} insights from Analysis Agent.")

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error calling Analysis Agent: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error when calling Analysis Agent: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error when getting insights from Analysis Agent: {e}")

    # Step 2: Pass insights to the Innovation Agent to generate ideas
    generated_ideas = await innovation_agent_instance.generate_ideas_from_insights(
        insights,
        creativity_level=creativity_level
    )

    # Step 3: Generate the Markdown report
    markdown_report = await innovation_agent_instance.generate_markdown_report(generated_ideas, query)
    
    return {
        "query": query,
        "generated_ideas": generated_ideas,
        "ideas_count": len(generated_ideas),
        "markdown_report": markdown_report
    }

# ----------------------------------------------------
# 8. Running the Application (Typically via Uvicorn)
# ----------------------------------------------------
# This block is commented out because Uvicorn is typically run via command line:
# uvicorn api.main:app --reload
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)