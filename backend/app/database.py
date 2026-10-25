"""Database connection setup, shared by the rest of the app."""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Read settings from the .env file (e.g. DATABASE_URL) into environment variables
load_dotenv()

# The connection string tells SQLAlchemy which database to use, e.g.
# postgresql+psycopg://postgres:yourpassword@localhost:5432/premier_league
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")

# The engine manages the actual connections to PostgreSQL
engine = create_engine(DATABASE_URL)

# Each request gets its own session (a short conversation with the database)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Parent class for all table models in models.py."""


def get_db():
    """Give a route a database session, and always close it when the request is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
