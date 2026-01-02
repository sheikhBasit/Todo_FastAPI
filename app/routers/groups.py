from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..config import database
from ..utils import auth
from ..models import model as models
from ..schemas import groups as schemas

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("/", response_model=schemas.Group)
def create_group(group: schemas.GroupCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_group = models.Group(**group.model_dump(), user_id=current_user.id)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

@router.get("/", response_model=List[schemas.Group])
def list_groups(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # ACCESS CONTROL: Users only see their own groups
    return db.query(models.Group).filter(models.Group.user_id == current_user.id).all()

@router.put("/{id}", response_model=schemas.Group)
def update_group(id: int, group: schemas.GroupCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_group = db.query(models.Group).filter(models.Group.id == id, models.Group.user_id == current_user.id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    db_group.name = group.name
    db.commit()
    db.refresh(db_group)
    return db_group

@router.delete("/{id}")
def delete_group(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    group = db.query(models.Group).filter(models.Group.id == id, models.Group.user_id == current_user.id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Optional: Logic to handle tasks inside this group could be added here
    db.delete(group)
    db.commit()
    return {"message": "Group deleted successfully"}