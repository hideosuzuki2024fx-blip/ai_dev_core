"""
Main application entrypoint for the ReWriteMe backend.

This module defines a FastAPI application that exposes endpoints for
rewriting user‑supplied text, performing simple sentiment classification
and storing/retrieving rewrite history.  The implementation is kept
intentionally light‑weight so that it can run in a container without
external dependencies beyond the OpenAI Python client and standard
libraries.  All state persists to a SQLite database on disk.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, database, utils

# Create all tables up front
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ReWriteMe API", description="Endpoints for rewriting and analysis", version="1.0.0")

# Allow CORS for any origin in development. In production this should be restricted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """
    Dependency that yields a database session and ensures it is closed
    after the request.  This allows dependency injection to work
    seamlessly with FastAPI.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/rewrite", response_model=schemas.RewriteResponse)
async def rewrite_text(request: schemas.RewriteRequest, db: Session = Depends(get_db)):
    """
    Accept user text and produce three rewrite options using the OpenAI API.
    Each suggestion includes a short explanation for why it differs from
    the original and a basic emotion analysis of the rewrite itself.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="No text provided")

    # Ask OpenAI for three rewrite candidates.  The utils module handles
    # API interaction and fallback behaviour.
    rewrites = await utils.generate_rewrites(request.text)

    # Compute sentiment for each rewrite.  utils.emotion_analysis returns a
    # dictionary keyed by rewrite index.
    sentiments = await utils.emotion_analysis(rewrites)

    # Create history entry in database
    history_entry = crud.create_history_entry(db=db, original=request.text, rewrites=rewrites, sentiments=sentiments)

    # Build response object
    response = schemas.RewriteResponse(
        original=request.text,
        options=[schemas.RewriteOption(text=rw, reason="See analysis", emotion=sentiments[idx])
                 for idx, rw in enumerate(rewrites)],
        history_id=history_entry.id,
    )
    return response


@app.post("/emotion", response_model=schemas.EmotionResponse)
async def emotion_endpoint(request: schemas.EmotionRequest):
    """
    Accept text and return an emotion analysis.  This endpoint is useful
    for stand‑alone emotion classification separate from rewriting.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="No text provided")
    emotion = await utils.analyse_single_emotion(request.text)
    return schemas.EmotionResponse(emotion=emotion)


@app.post("/history", response_model=schemas.HistoryResponse)
def save_history(request: schemas.SaveHistoryRequest, db: Session = Depends(get_db)):
    """
    Persist a previously returned rewrite result.  Clients should call
    this endpoint to mark a particular rewrite as 'accepted' or to
    persist voice memory.  The implementation stores the selected
    rewrite and any user feedback in the database.
    """
    history = crud.get_history_entry(db, history_id=request.history_id)
    if history is None:
        raise HTTPException(status_code=404, detail="History entry not found")
    crud.finalise_history_entry(db, history, selected_option=request.selected_option)
    return schemas.HistoryResponse(message="History updated")


@app.get("/history/{history_id}", response_model=schemas.HistoryDetail)
def read_history(history_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific history record by its identifier.
    """
    history = crud.get_history_entry(db, history_id=history_id)
    if history is None:
        raise HTTPException(status_code=404, detail="History entry not found")
    return schemas.HistoryDetail(
        id=history.id,
        original=history.original,
        rewrites=history.rewrites,
        sentiments=history.sentiments,
        selected_option=history.selected_option,
        created_at=history.created_at,
    )