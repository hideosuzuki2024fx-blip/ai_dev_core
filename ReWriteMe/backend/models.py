"""
SQLAlchemy models for persistence of rewrite history and user profiles.

The History model stores the original text, three rewrite suggestions,
associated sentiment scores and the selected rewrite option.  It
captures metadata such as creation timestamp for chronological
sorting.  Additional tables can be added later to support voice
profiles or user accounts.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    original = Column(Text, nullable=False)
    rewrites = Column(JSON, nullable=False)  # List[str]
    sentiments = Column(JSON, nullable=False)  # List[str] or mapping
    selected_option = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "original": self.original,
            "rewrites": self.rewrites,
            "sentiments": self.sentiments,
            "selected_option": self.selected_option,
            "created_at": self.created_at,
        }