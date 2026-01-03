"""
Database engine and session configuration for the ReWriteMe backend.

This module exports a SQLAlchemy engine pointing to a local SQLite
database and a SessionLocal class for creating sessions.  The
database path is set relative to the project root and can be
overridden via the DATABASE_URL environment variable.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Default to a SQLite database in the project directory.  It can be
# overridden by setting DATABASE_URL environment variable.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./rewrite_me.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite needs special flags for concurrency in SQLAlchemy
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)