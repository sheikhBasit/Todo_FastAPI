from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
import re

# Assuming GroupBase is defined in the same file or imported
# If in same file, ensure GroupBase is defined ABOVE TaskBase
class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    model_config = ConfigDict(from_attributes=True)

# --- TASK SCHEMAS ---

class TaskBase(BaseModel):
    # Validation: 1-200 chars, and must contain at least one non-whitespace character
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        description="Task title (cannot be only whitespace)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="Optional task details"
    )
    is_completed: bool = Field(default=False)
    
    # Validation: Ensure group_id is a positive integer
    group_id: int = Field(..., gt=0, description="ID of the group (must be positive)")

    # Custom Validator for Title: Prevent "empty space" titles
    @field_validator('title')
    @classmethod
    def title_must_not_be_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or only spaces')
        return v.strip()

    # Custom Validator for Description: Clean up whitespace
    @field_validator('description')
    @classmethod
    def clean_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip()
        return v

class TaskCreate(TaskBase):
    """Schema used for creating a task (POST /tasks)"""
    pass

class TaskUpdate(BaseModel):
    """Schema used for updating a task (PUT /tasks/{id})"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_completed: Optional[bool] = None
    group_id: Optional[int] = Field(None, gt=0)

    @field_validator('title')
    @classmethod
    def title_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Title cannot be only spaces')
        return v.strip() if v else v

class Task(TaskBase):
    """Schema used for the API output"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Requirement: Using joins to fetch group details
    group: Optional[GroupBase] = None

    # Pydantic V2 style config
    model_config = ConfigDict(from_attributes=True)

