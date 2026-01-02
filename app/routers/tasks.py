from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..config import database, config
from ..utils import auth
from ..models import model as models
from ..schemas import tasks as schemas
from groq import AsyncGroq

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Initialize Groq Client
client = AsyncGroq(api_key=config.settings.GROQ_API_KEY)

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

@router.get("/suggestions")
async def get_ai_suggestions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Fetch user tasks with group info for better AI context
    tasks = db.query(models.Task).options(joinedload(models.Task.group)).filter(models.Task.user_id == current_user.id).all()
    
    task_context = [f"- {t.title} (Category: {t.group.name if t.group else 'General'})" for t in tasks]
    context_str = "\n".join(task_context) if task_context else "No tasks currently."

    try:
        completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a productivity coach. Provide one short, actionable tip based on the user's task list."},
                {"role": "user", "content": f"My tasks:\n{context_str}"}
            ],
            model="llama-3.3-70b-versatile",
        )
        return {"tip": completion.choices[0].message.content, "user": current_user.username}
    except Exception as e:
        return {"tip": "Organize your tasks by priority!", "error": "AI service temporarily unavailable"}

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