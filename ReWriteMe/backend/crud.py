"""
CRUD (Create, Read, Update, Delete) functions encapsulate database
operations.  Each function accepts a database session and models
entities to perform actions.  Keeping CRUD in a separate module
simplifies unit testing and separates data access from business logic.
"""

from sqlalchemy.orm import Session
from . import models
from typing import List, Dict


def create_history_entry(db: Session, original: str, rewrites: List[str], sentiments: List[str]):
    """Create and persist a new History entry."""
    history = models.History(
        original=original,
        rewrites=rewrites,
        sentiments=sentiments,
        selected_option=None,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_history_entry(db: Session, history_id: int) -> models.History:
    return db.query(models.History).filter(models.History.id == history_id).first()


def finalise_history_entry(db: Session, history: models.History, selected_option: int) -> None:
    """
    Mark a History entry as finalised by recording the selected rewrite.
    The database row is updated and committed.
    """
    history.selected_option = selected_option
    db.commit()
    db.refresh(history)