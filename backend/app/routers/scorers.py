"""CRUD endpoints for top scorers. Same pattern as teams.py."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Scorer
from ..schemas import ScorerIn, ScorerOut

router = APIRouter(prefix="/api/scorers", tags=["scorers"])


def get_scorer_or_404(db, scorer_id):
    scorer = db.get(Scorer, scorer_id)
    if scorer is None:
        raise HTTPException(status_code=404, detail=f"Scorer {scorer_id} not found")
    return scorer


@router.get("", response_model=list[ScorerOut])
def list_scorers(db: Session = Depends(get_db)):
    """READ all scorers, most goals first."""
    return db.scalars(select(Scorer).order_by(Scorer.rank, Scorer.player)).all()


@router.get("/{scorer_id}", response_model=ScorerOut)
def get_scorer(scorer_id: int, db: Session = Depends(get_db)):
    return get_scorer_or_404(db, scorer_id)


@router.post("", response_model=ScorerOut, status_code=201)
def create_scorer(data: ScorerIn, db: Session = Depends(get_db)):
    scorer = Scorer(**data.model_dump())
    db.add(scorer)
    db.commit()
    db.refresh(scorer)
    return scorer


@router.put("/{scorer_id}", response_model=ScorerOut)
def update_scorer(scorer_id: int, data: ScorerIn, db: Session = Depends(get_db)):
    scorer = get_scorer_or_404(db, scorer_id)
    for field, value in data.model_dump().items():
        setattr(scorer, field, value)
    db.commit()
    db.refresh(scorer)
    return scorer


@router.delete("/{scorer_id}", status_code=204)
def delete_scorer(scorer_id: int, db: Session = Depends(get_db)):
    scorer = get_scorer_or_404(db, scorer_id)
    db.delete(scorer)
    db.commit()
    return Response(status_code=204)
