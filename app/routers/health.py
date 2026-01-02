from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..config.database import get_db

router = APIRouter()

@router.get("/db-status")
def check_db_status(db: Session = Depends(get_db)):
    try:
        # Perform a simple query to verify the connection
        db.execute(text("SELECT 1"))
        return {"status": "connected", "database": "Neon PostgreSQL"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}