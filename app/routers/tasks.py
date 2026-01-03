from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..config import database, config
from ..utils import auth
from ..models import model as models
from ..schemas import tasks as schemas


router = APIRouter(prefix="/tasks", tags=["Tasks"])

# --- CATEGORY-BASED HEURISTIC ENGINE ---
def analyze_tasks_heuristically(tasks: List[models.Task]) -> str:
    if not tasks:
        return "Your schedule is clear! It's a great time to start a new project in your 'Learning' group."

    # 1. Scoring Logic
    HIGH_PRIORITY_KEYWORDS = ["finish", "submit", "deadline", "urgent", "important", "review", "bill"]
    
    # 2. Category Advice (Based on Seed Data Groups)
    CATEGORY_TIPS = {
        "Work": "Focus on deep work sessions for your professional projects.",
        "Personal": "Don't forget to balance your productivity with self-care.",
        "Fitness": "Physical activity boosts mental clarity. Keep moving!",
        "Learning": "Consistency is key to mastering new skills. Spend 15 minutes on this today.",
        "Shopping": "Try to batch your errands to save time and energy."
    }

    scored_tasks = []
    category_counts = {}

    for task in tasks:
        score = 0
        # Title/Description weight
        content = (task.title + " " + (task.description or "")).lower()
        if any(word in content for word in HIGH_PRIORITY_KEYWORDS):
            score += 5
        
        # Category weight (Work/Learning often have higher priority)
        group_name = task.group.name if task.group else "General"
        if group_name in ["Work", "Learning"]:
            score += 2
        
        # Count categories to find dominant focus
        category_counts[group_name] = category_counts.get(group_name, 0) + 1
        
        scored_tasks.append({"score": score, "title": task.title, "group": group_name})

    # Sort to find the highest priority task
    scored_tasks.sort(key=lambda x: x["score"], reverse=True)
    top_item = scored_tasks[0]
    
    # Find most crowded category
    dominant_cat = max(category_counts, key=category_counts.get)
    cat_tip = CATEGORY_TIPS.get(dominant_cat, "Keep up the great work!")

    # Generate the "AI" response
    return (
        f"AI Suggestion: Based on your {dominant_cat} focus, {cat_tip} "
        f"I recommend starting with '{top_item['title']}' as it appears most critical."
    )

@router.get("/suggestions")
async def get_ai_suggestions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Requirement: Use JOINs to fetch tasks with group details for the heuristic
    tasks = db.query(models.Task).options(joinedload(models.Task.group)).filter(
        models.Task.user_id == current_user.id,
        models.Task.is_completed == False
    ).all()

    tip = analyze_tasks_heuristically(tasks)

    return {
        "tip": tip,
        "user": current_user.username,
        "active_tasks": len(tasks),
        "engine": "Category-Aware Heuristic Stub v2.0"
    }


@router.post("/", response_model=schemas.Task, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # ACCESS CONTROL: Verify the target group actually belongs to the logged-in user
    group = db.query(models.Group).filter(
        models.Group.id == task.group_id, 
        models.Group.user_id == current_user.id
    ).first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")
    
    new_task = models.Task(**task.model_dump(), user_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[schemas.Task])
def get_tasks(
    # Pagination parameters with defaults
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max number of items to return"),
    group_id: Optional[int] = None, 
    completed: Optional[bool] = None,
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Start the query with joins
    query = db.query(models.Task).options(joinedload(models.Task.group)).filter(models.Task.user_id == current_user.id)
    
    # 2. Apply Filters
    if group_id:
        query = query.filter(models.Task.group_id == group_id)
    if completed is not None:
        query = query.filter(models.Task.is_completed == completed)
    
    # 3. Apply Pagination and Execute
    # .offset() skips the first X rows, .limit() takes the next Y rows
    tasks = query.offset(skip).limit(limit).all()
    
    return tasks

@router.get("/{id}", response_model=schemas.Task)
def get_task(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id, models.Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task



@router.put("/{id}", response_model=schemas.Task)
def update_task(id: int, task: schemas.TaskUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_task = db.query(models.Task).filter(models.Task.id == id, models.Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check group ownership if changing groups
    if task.group_id:
        group = db.query(models.Group).filter(models.Group.id == task.group_id, models.Group.user_id == current_user.id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Target group not found")
    
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{id}")
def delete_task(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id, models.Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}