"""CRUD endpoints for teams: Create, Read, Update, Delete."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Team
from ..schemas import TeamIn, TeamOut

# Every route below starts with /api/teams
router = APIRouter(prefix="/api/teams", tags=["teams"])


def get_team_or_404(db, team_id):
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return team


@router.get("", response_model=list[TeamOut])
def list_teams(db: Session = Depends(get_db)):
    """READ all teams, in league order."""
    return db.scalars(select(Team).order_by(Team.position)).all()


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """READ one team by id."""
    return get_team_or_404(db, team_id)


@router.post("", response_model=TeamOut, status_code=201)
def create_team(data: TeamIn, db: Session = Depends(get_db)):
    """CREATE a team. `data` has already been validated by Pydantic."""
    team = Team(**data.model_dump())  # model_dump() turns the schema into a dict
    db.add(team)
    try:
        db.commit()  # save to the database
    except IntegrityError:  # e.g. a team with this name already exists
        db.rollback()
        raise HTTPException(status_code=409, detail=f"A team named '{data.name}' already exists")
    db.refresh(team)  # reload so `team.id` is filled in
    return team


@router.put("/{team_id}", response_model=TeamOut)
def update_team(team_id: int, data: TeamIn, db: Session = Depends(get_db)):
    """UPDATE every field of an existing team."""
    team = get_team_or_404(db, team_id)
    for field, value in data.model_dump().items():
        setattr(team, field, value)  # same as team.<field> = value
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"A team named '{data.name}' already exists")
    db.refresh(team)
    return team


@router.delete("/{team_id}", status_code=204)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """DELETE a team. 204 means 'done, nothing to send back'."""
    team = get_team_or_404(db, team_id)
    db.delete(team)
    db.commit()
    return Response(status_code=204)
