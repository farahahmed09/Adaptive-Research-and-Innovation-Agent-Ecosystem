# database/models.py

from sqlalchemy import create_engine, Column, Integer, String # Import necessary SQLAlchemy components
from sqlalchemy.ext.declarative import declarative_base # For defining base class for models
from sqlalchemy.orm import sessionmaker # For creating database sessions

# ----------------------------------------------------
# 1. Database Configuration
# ----------------------------------------------------
# DATABASE_URL specifies the connection string for our SQLite database.
DATABASE_URL = "sqlite:///./local_database.db"

# create_engine creates a SQLAlchemy Engine, which is the actual database connection.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a class that will be used to create database sessions.
# Each session is a "conversation" with the database.
# `autocommit=False` means changes aren't saved until explicitly committed.
# `autoflush=False` prevents the session from flushing changes automatically.
# `bind=engine` links the session maker to our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the base class for our SQLAlchemy models.
# All our database models (tables) will inherit from this.
Base = declarative_base()

# ----------------------------------------------------
# 2. Define Database Models (Tables)
# ----------------------------------------------------

# This class represents the 'users' table in our database.
class User(Base):
    __tablename__ = "users" # Specifies the actual table name in the database

    # Define columns for the table
    # Column(Integer, primary_key=True, index=True): Auto-incrementing integer, primary key, indexed for fast lookups.
    id = Column(Integer, primary_key=True, index=True)
    # Column(String, unique=True, index=True): String type, must be unique, indexed.
    username = Column(String, unique=True, index=True)
    # Column(String): String type for storing hashed passwords.
    hashed_password = Column(String)

# ----------------------------------------------------
# 3. Function to Create Database Tables
# ----------------------------------------------------

def create_db_tables():
    Base.metadata.create_all(bind=engine)
