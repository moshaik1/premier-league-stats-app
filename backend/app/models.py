"""Database tables. Each class becomes one table, each attribute one column."""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Team(Base):
    """One row of the league table."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)  # unique number for each row, assigned by the database
    position: Mapped[int]
    name: Mapped[str] = mapped_column(String(100), unique=True)  # no two teams with the same name
    played: Mapped[int]
    won: Mapped[int]
    drawn: Mapped[int]
    lost: Mapped[int]
    goals_for: Mapped[int]
    goals_against: Mapped[int]
    goal_difference: Mapped[int]
    points: Mapped[int]
    wiki_url: Mapped[str | None] = mapped_column(String(300))  # "| None" means this column is optional


class Scorer(Base):
    """One player in the top scorers chart."""

    __tablename__ = "scorers"

    id: Mapped[int] = mapped_column(primary_key=True)
    rank: Mapped[int]
    player: Mapped[str] = mapped_column(String(100))
    club: Mapped[str] = mapped_column(String(100))
    goals: Mapped[int]
