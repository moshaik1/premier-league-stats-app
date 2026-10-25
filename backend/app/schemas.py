"""Pydantic schemas: the shape of the JSON the API accepts and returns.

Models (models.py) describe the database. Schemas describe the API.
FastAPI uses these to check incoming data and return a 422 error if it's wrong.
"""
from pydantic import BaseModel, ConfigDict, Field


class TeamIn(BaseModel):
    """What the client sends to create or update a team."""

    position: int = Field(ge=1)  # ge=1 means "greater than or equal to 1"
    name: str = Field(min_length=1, max_length=100)
    played: int = Field(ge=0)
    won: int = Field(ge=0)
    drawn: int = Field(ge=0)
    lost: int = Field(ge=0)
    goals_for: int = Field(ge=0)
    goals_against: int = Field(ge=0)
    goal_difference: int  # can be negative
    points: int = Field(ge=0)
    wiki_url: str | None = None


class TeamOut(TeamIn):
    """What the API sends back: everything in TeamIn plus the database id."""

    # Lets Pydantic read values straight from a SQLAlchemy object (team.name, team.points, ...)
    model_config = ConfigDict(from_attributes=True)

    id: int


class ScorerIn(BaseModel):
    rank: int = Field(ge=1)
    player: str = Field(min_length=1, max_length=100)
    club: str = Field(min_length=1, max_length=100)
    goals: int = Field(ge=0)


class ScorerOut(ScorerIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ScrapeResult(BaseModel):
    """Summary returned after refreshing from Wikipedia."""

    season: str
    teams: int
    scorers: int
