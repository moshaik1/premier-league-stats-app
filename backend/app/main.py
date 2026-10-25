"""Entry point for the API. Run with:  uvicorn app.main:app --reload"""
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session
import requests

from .database import Base, engine, get_db
from .models import Scorer, Team
from .routers import scorers, teams
from .schemas import ScrapeResult
from .scraper import SEASON, scrape_season

# Create the tables in PostgreSQL if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Premier League Stats API")
app.include_router(teams.router)
app.include_router(scorers.router)


@app.get("/api/health")
def health():
    """Quick check that the server is running."""
    return {"status": "ok"}


@app.post("/api/scrape", response_model=ScrapeResult)
def refresh_from_wikipedia(db: Session = Depends(get_db)):
    """Re-scrape Wikipedia and replace everything in both tables with the fresh data.

    Note: this overwrites any manual edits you've made.
    """
    try:
        team_rows, scorer_rows = scrape_season()
    except requests.RequestException as error:
        # 502 = "the server we depend on (Wikipedia) had a problem"
        raise HTTPException(status_code=502, detail=f"Couldn't reach Wikipedia: {error}")
    except ValueError as error:
        raise HTTPException(status_code=502, detail=str(error))

    # Delete old rows and insert new ones in one transaction:
    # if anything fails, nothing is committed and the old data stays.
    db.execute(delete(Team))
    db.execute(delete(Scorer))
    db.add_all(Team(**row) for row in team_rows)
    db.add_all(Scorer(**row) for row in scorer_rows)
    db.commit()

    return ScrapeResult(season=SEASON, teams=len(team_rows), scorers=len(scorer_rows))
