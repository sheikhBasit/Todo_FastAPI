from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

# --- GROUP SCHEMAS ---

class GroupBase(BaseModel):
    # Validation: 1-100 characters, no whitespace-only names allowed
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Name of the task group (e.g., 'Work', 'Personal')"
    )

    # Custom Validator: Ensure name isn't just empty spaces and trim it
    @field_validator('name')
    @classmethod
    def name_must_not_be_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Group name cannot be empty or only spaces')
        return v.strip()

class GroupCreate(GroupBase):
    """Schema for creating a group (POST /groups)"""
    pass

class GroupUpdate(BaseModel):
    """Schema for updating a group (PUT /groups/{id})"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator('name')
    @classmethod
    def name_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Group name cannot be only spaces')
        return v.strip() if v else v

class Group(GroupBase):
    """Schema for API responses (GET /groups)"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Modern Pydantic V2 Configuration
    model_config = ConfigDict(from_attributes=True)

