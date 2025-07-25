from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship # NEW: Import relationship
from datetime import datetime # NEW: Import datetime

DATABASE_URL = "sqlite:///./local_database.db" # This will create a file

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Define a relationship to Feedback
    feedbacks = relationship("Feedback", back_populates="user")

# CLASS: Feedback Model
class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Link to the User table
    
    # Store information about the idea being feedbacked
    query = Column(String) # The original query that generated the ideas
    idea_title = Column(String, nullable=True) # Title of the specific idea (if available)
    idea_description_snippet = Column(String, nullable=True) # A snippet of the idea's description
    
    # Feedback details
    feedback_type = Column(String) # e.g., "positive", "negative", "needs_refinement"
    comment = Column(String, nullable=True) # Optional text comment
    
    timestamp = Column(DateTime, default=datetime.utcnow) # When the feedback was given

    # Define relationship to User
    user = relationship("User", back_populates="feedbacks")

def create_db_tables():
    Base.metadata.create_all(bind=engine)